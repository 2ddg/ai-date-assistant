# ---- Stage 1: 构建前端 ----
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ---- Stage 2: 后端 + 内置前端 ----
# rebuild: include models/ (fix ModuleNotFoundError)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
COPY --from=frontend /app/frontend/dist frontend/dist
RUN mkdir -p uploads
ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]