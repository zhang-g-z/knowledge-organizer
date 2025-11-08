import json
import re
import logging
import traceback

import jieba.analyse
import openai

from app.core.config import settings

logger = logging.getLogger(__name__)

# 初始化 openai 客户端的全局设置（会在导入时设置）
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
if settings.OPENAI_BASE_URL:
    # 注意：openai.api_base 用于替换基础 URL（例如私有部署或代理）
    openai.api_base = settings.OPENAI_BASE_URL

def split_sentences(text):
    sentences = re.split(r'(?<=[。！？\?\!\n])\s*', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def _local_extract(text: str):
    # 之前的本地简单提取（jieba + 规则），作为回退
    text = text.strip()
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    title = first_line if 5 <= len(first_line) <= 120 else text[:30].replace("\n", " ")
    try:
        tags = jieba.analyse.extract_tags(text, topK=6)
    except Exception:
        tags = []
    sents = split_sentences(text)
    if sents:
        description = sents[0] if len(sents[0]) <= 120 else sents[0][:120]
        summary = " ".join(sents[:2]) if len(sents) >= 2 else sents[0]
    else:
        description = text[:120]
        summary = text[:300]
    return {
        "title": title,
        "tags": tags,
        "description": description,
        "summary": summary,
        "source": "local"
    }

def _extract_json_from_text(text):
    # 尝试从 LLM 的返回文本中提取第一个 JSON 对象
    m = re.search(r'(\{.*\})', text, flags=re.DOTALL)
    if not m:
        return None
    json_text = m.group(1)
    try:
        return json.loads(json_text)
    except Exception:
        # 尝试修复常见的 JSON 问题：单引号 -> 双引号
        fixed = json_text.replace("'", '"')
        try:
            return json.loads(fixed)
        except Exception:
            return None

def _call_openai(text: str):
    """
    调用 OpenAI ChatCompletion，要求返回严格的 JSON：
    {
      "title": "...",
      "tags": ["tag1","tag2"],
      "description": "...",
      "summary": "..."
    }
    如果解析失败，会返回 None。
    """
    if not settings.OPENAI_API_KEY:
        return None

    system_prompt = (
        "You are a helpful assistant that extracts structured metadata from a user-provided text. "
        "Given an input text, produce a JSON object with exactly these keys: title, tags, description, summary. "
        "title: a concise title (string). "
        "tags: an array of short tag strings (can be empty). "
        "description: a one-sentence short description (preferably <=120 chars). "
        "summary: a short summary (a few sentences). "
        "Output ONLY a valid JSON object and nothing else."
    )

    user_prompt = f"Text:\n\"\"\"\n{text}\n\"\"\"\n\nReturn the JSON."

    try:
        resp = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=800,
            request_timeout=settings.OPENAI_TIMEOUT,
        )
        # 解析响应
        if not resp or "choices" not in resp or len(resp.choices) == 0:
            return None
        content = resp.choices[0].message.get("content") if hasattr(resp.choices[0], "message") else resp.choices[0].get("message", {}).get("content")
        if not content:
            # 兼容不同 openai 返回结构
            content = resp.choices[0].get("text") if "text" in resp.choices[0] else None
        if not content:
            return None

        # 尝试直接解析 JSON 或提取并解析 JSON
        try:
            data = json.loads(content)
        except Exception:
            data = _extract_json_from_text(content)

        if not data:
            # 如果解析失败，尝试用简单的行解析（极简）
            # 不认为安全，改为返回 None 以触发本地回退
            logger.warning("OpenAI response could not be parsed as JSON: %s", content[:500])
            return None

        # 验证并 normalize fields
        title = data.get("title") or ""
        tags = data.get("tags") or []
        # tags 可能为字符串，尝试分割
        if isinstance(tags, str):
            tags = [t.strip() for t in re.split(r'[,\s;，；]+', tags) if t.strip()]
        # ensure list of strings
        tags = [str(t) for t in tags if str(t).strip()]
        description = data.get("description") or ""
        summary = data.get("summary") or ""
        return {
            "title": title.strip(),
            "tags": tags,
            "description": description.strip(),
            "summary": summary.strip(),
            "source": "openai"
        }
    except Exception as e:
        logger.error("OpenAI call failed: %s\n%s", e, traceback.format_exc())
        return None

def extract_from_text(text: str):
    """
    主提取入口：优先调用 OpenAI（若配置了 API），若失败则回退到本地 jieba 提取器。
    返回 dict 包含 title, tags (list), description, summary, source (openai/local).
    """
    text = (text or "").strip()
    if not text:
        return _local_extract(text)

    # 先尝试 LLM（OpenAI）
    result = _call_openai(text)
    if result:
        return result

    # 回退
    return _local_extract(text)