<template>
  <a-card>
    <h1>Knowledge Organizer</h1>

    <h2>简介</h2>
    <p>
      Knowledge Organizer 是一个个人知识管理与信息抽取的小型系统。
      向系统提交原始文本后，后台会异步运行抽取任务，将文本解析为：标题、标签、描述与摘要，便于后续检索与整理。
    </p>

    <h2>关键功能</h2>
    <a-list bordered>
      <a-list-item>文本输入并异步抽取（Celery + Redis）</a-list-item>
      <a-list-item>条目列表与分页、按关键字搜索</a-list-item>
      <a-list-item>标签管理与快速筛选</a-list-item>
      <a-list-item>实时通知（通过 WebSocket 推送任务状态）</a-list-item>
      <a-list-item>基于 Ant Design Vue 的现代化前端 UI</a-list-item>
    </a-list>

    <h2>如何使用（简要）</h2>
    <ol>
      <li>打开“输入”页面，粘贴或输入原始文本并提交。</li>
      <li>后台将把任务放入队列并异步处理；处理状态会通过 WebSocket 推送到页面。</li>
      <li>在“列表”页面查看已创建的条目、标签与摘要，点击可查看原文或删除条目。</li>
    </ol>

    <h2>架构概览</h2>
    <p>
      后端：FastAPI（异步 API）
      <br />
      异步任务：Celery（使用 Redis 作为 broker 与 backend）
      <br />
      数据库：MySQL（或其它兼容数据库）
      <br />
      前端：Vue 3 + Vite，UI 使用 Ant Design Vue
    </p>

    <h2>本地运行（快速）</h2>
    <pre style="background:#f5f5f5;padding:12px;border-radius:6px"># 使用 docker compose（包含 app / db / redis / worker）
docker compose up --build

# 或分别运行开发环境
# 前端：
cd frontend
npm install
npm run dev

# 后端（在项目根目录）：
# 启动 API
uvicorn app.main:app --reload
# 启动 Celery worker
celery -A app.celery_task.celery worker --loglevel=info
    </pre>

    <h2>贡献与反馈</h2>
    <p>欢迎提出 issue 或提交 PR，讨论功能改进与 bug 修复。</p>
  </a-card>
</template>

<script setup>
// 静态页面，无需额外逻辑
</script>

<style scoped>
h1 {
  margin-bottom: 8px
}

h2 {
  margin-top: 16px;
  margin-bottom: 8px
}

pre {
  font-size: 13px
}
</style>
