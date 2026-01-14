# frontend/Dockerfile

# 阶段 1: 构建 (Build Stage)
# 修改这里：使用与你本地一致的 Node 24 版本
FROM node:24-alpine as build-stage

WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖 (使用淘宝源加速)
RUN npm install --registry=https://registry.npmmirror.com

# 复制所有前端代码
COPY . .

# 执行构建
RUN npm run build

# 阶段 2: 部署 (Production Stage)
# Nginx 版本通常不需要严格对应，stable-alpine 是最稳妥的选择
FROM nginx:stable-alpine as production-stage

# 复制构建好的静态文件到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]