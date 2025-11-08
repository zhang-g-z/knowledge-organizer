# 知识整理系统（FastAPI + Vue + MySQL + SQLAlchemy）

项目功能概述：
- 前端（Vue）：
  - 信息输入页：提交一段文字给后端，后端自动提炼：标题、标签（可多个）、描述、摘要、原文。
  - 列表页：分页展示提取后的条目（不展示原文）。点击「查看原文」弹窗显示原文。
- 后端（FastAPI）：
  - 所有 API 前缀为 `/api`。
  - 提供 CRUD 接口：创建、分页查询、单条获取（含原文）、更新、删除。
  - 将 Vue 编译后的静态文件挂载为根路径 `/`，以便直接用 FastAPI 提供前端静态页面。
- 数据库：MySQL，使用 SQLAlchemy ORM（同步实现，易于理解与调试）。
- 自动提取：示例中使用 `jieba.analyse` 做关键词提取与简单规则生成标题/摘要。可替换为 LLM / 更复杂的 NLP。

快速开始（开发）：
1. 准备 MySQL，并创建数据库，例如 `knowledge_db`。
2. 后端：
   - 安装依赖：`pip install -r requirements.txt`
   - 编辑 `app/core/config.py` 中的 DATABASE_URL 为你的 MySQL 连接字符串。
   - 运行：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. 前端：
   - 进入 `frontend/`，安装依赖：`npm install`
   - 开发模式：`npm run dev`
   - 生产构建：`npm run build`，将 `dist/` 内容拷贝到后端 `frontend_dist/`（或后端配置的静态目录）。
4. 生产部署（示例）：
   - 在后端项目根目录运行：`uvicorn app.main:app --host 0.0.0.0 --port 8000`（假设已经把前端 dist 放到 `frontend_dist/`）
   - 启动celery异步任务 celery -A app.celery_task.celery worker --loglevel=info -P eventlet
   - 或使用提供的 Dockerfile 与 docker-compose 构建镜像并运行（见 `docker-compose.yml`）。

注意与扩展建议：
- 自动提取模块为可替换实现，建议未来接入 LLM（如 OpenAI）或更强的中文文本抽取（如 THU Lexical models）。
- 若并发量大，建议改为 SQLAlchemy async + async DB driver（aiomysql 或 asyncmy）。
- 若需要全文搜索/过滤标签，建议加上 Elasticsearch / Meilisearch / MySQL 全文索引。
