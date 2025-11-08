import json
import re
import logging
import traceback
import asyncio

import jieba.analyse
import openai

from app.core.config import settings

logger = logging.getLogger(__name__)


asyncClient = openai.AsyncOpenAI(
    api_key = settings.OPENAI_API_KEY,
    base_url = settings.OPENAI_BASE_URL
)
# configure openai

def split_sentences(text):
    sentences = re.split(r'(?<=[。！？\?\!\n])\s*', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def local_extract(text: str):
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
        "llm_raw": None,
        "confidence": None,
        "source": "local",
        "status": "done",
    }

def _extract_json_from_text(text):
    m = re.search(r'(\{.*\})', text, flags=re.DOTALL)
    if not m:
        return None
    json_text = m.group(1)
    try:
        return json.loads(json_text)
    except Exception:
        fixed = json_text.replace("'", '"')
        try:
            return json.loads(fixed)
        except Exception:
            return None

async def call_openai_async(text: str):
    """
    异步调用 OpenAI ChatCompletion（acreate），期望返回可解析 JSON：
    {
      "title": "...",
      "tags": ["..."],
      "description": "...",
      "summary": "...",
      "confidence": "0.9" (optional)
    }
    返回 dict 或 None。
    """
    if not settings.OPENAI_API_KEY:
        return None

    system_prompt = (
        "You are a helpful assistant that extracts structured metadata from a user-provided text. "
        "Given an input text, produce a JSON object with exactly these keys: title, tags, description, summary, confidence (optional). "
        "title: a concise title (string). "
        "tags: an array of short tag strings (can be empty). "
        "description: a one-sentence short description (<=120 chars). "
        "summary: a short summary (a few sentences). "
        "confidence: optional string or number representing confidence. "
        "Output ONLY a valid JSON object and nothing else."
    )

    user_prompt = f"Text:\n\"\"\"\n{text}\n\"\"\"\n\nReturn the JSON."

    try:
        # use the async create method
        resp = await asyncClient.chat.completions.create(
            model=settings.OPENAI_MODEL,  # 或其他支持的模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
           temperature=0.0,
           max_tokens=800
        )
        # obtain content
        choice = resp.choices[0]
        # Chat API returns message content
        content = choice.message.content

        if not content:
            return None

        data = None
        try:
            data = json.loads(content)
        except Exception:
            data = _extract_json_from_text(content)

        if not data:
            logger.warning("OpenAI response could not be parsed as JSON: %s", content[:500])
            return {"llm_raw": content, "parsed": None}

        # Normalize fields
        title = data.get("title", "").strip()
        tags = data.get("tags", []) or []
        if isinstance(tags, str):
            tags = [t.strip() for t in re.split(r'[,\s;，；]+', tags) if t.strip()]
        tags = [str(t) for t in tags if str(t).strip()]
        description = data.get("description", "").strip()
        summary = data.get("summary", "").strip()
        confidence = data.get("confidence")
        return {
            "title": title,
            "tags": tags,
            "description": description,
            "summary": summary,
            "llm_raw": content,
            "confidence": str(confidence) if confidence is not None else None,
            "source": "llm",
            "status": "done",
        }
    except Exception as e:
        logger.error("OpenAI async call failed: %s\n%s", e, traceback.format_exc())
        return None

async def extract_from_text_async(text: str):
    """
    异步提取入口，优先调用 OpenAI 异步接口，失败回退到本地。
    """
    text = (text or "").strip()
    if not text:
        return local_extract(text)

    result = await call_openai_async(text)
    if result is None:
        # openai call failed entirely
        return local_extract(text)
    # If result contains parsed==None but llm_raw exists, treat as failure -> fallback
    if "parsed" in result and result.get("parsed") is None:
        return local_extract(text)
    return result