# backend/Dockerfile

# 修改这里：使用与你本地一致的 3.11 版本
FROM python:3.11-slim

WORKDIR /app

# 1. 复制依赖文件
COPY requirements.txt .

# 2. 安装依赖 (使用清华源加速)
# --no-cache-dir 减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 复制后端所有代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]