# 多阶段构建：先构建前端再构建后端镜像
# FROM public.ecr.aws/docker/library/node:slim AS frontend-build
# WORKDIR /src/frontend
# COPY frontend/package*.json frontend/index.html frontend/vite.config.mjs ./
# COPY frontend/src ./src

# # 安装所有依赖（包括 devDependencies 用于构建）
# RUN npm config set registry=https://registry.npmmirror.com \
#     && npm install
# RUN npm run build

FROM public.ecr.aws/docker/library/python:3.11-slim
WORKDIR /app
# 系统依赖（包括 supervisor 用于运行多进程）
# RUN sed -i 's#deb.debian.org#mirrors.aliyun.com#g' /etc/apt/sources.list.d/debian.sources
# RUN apt-get update \
# 	&& apt-get install -y --no-install-recommends build-essential supervisor \
# 	&& rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -r requirements.txt


# Copy supervisor config and run supervisord to manage uvicorn + celery in one container
# COPY supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 80
# CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["celery", "-A", "app.celery_task.celery", "worker", "--loglevel=info"]