# 🎵 VocaLog - 虚拟歌手创作工程管理系统

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Vue](https://img.shields.io/badge/Vue.js-3.x-42b883)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ed)
![License](https://img.shields.io/badge/license-MIT-orange)

**VocaLog** 是一个专为 VOCALOID / Synthesizer V / ACE Studio 等虚拟歌手创作者设计的工程管理与进度追踪平台。

它解决了传统创作中“文件目录混乱”、“Staff 进度沟通成本高”、“进度追踪困难”的痛点，通过现代化的 Web 界面和跨平台客户端，让创作管理变得井井有条。

---

## ✨ 核心功能

* **🎧 多声库与歌手管理**：支持自定义录入歌手信息，支持 VOCALOID, Synthesizer V 等多种引擎的版本管理。
* **📊 细粒度进度追踪**：支持策划、作词、调教、混音等 10+ 种工种的进度管理，精确记录每位 Staff 的完成时间。
* **🛠️ 动态工种生成**：根据选择的声库自动生成对应的调教工种（如：调教 (洛天依) / 调教 (初音未来)）。
* **📂 跨平台文件交互**：
    * **Electron 桌面端**：支持调用原生文件资源管理器打开工程目录。
    * **Web / 移动端**：响应式布局，随时随地查看项目进度。
* **📋 一键导出名单**：自动生成符合 B 站/视频网站投稿格式的 Staff 文字名单。
* **🐳 Docker 一键部署**：无需配置复杂的 Python/Node 环境，开箱即用。

---

## 🚀 快速开始 (推荐)

如果你安装了 Docker，这是最简单的运行方式。

1.  **克隆仓库**
    ```bash
    git clone https://github.com/lclty/VocaLog.git
    cd VocaLog
    ```

2.  **启动服务**
    ```bash
    docker-compose up -d --build
    ```

3.  **访问系统**
    打开浏览器访问 `http://localhost:8080` 即可使用。

---

## 💻 开发者指南 (源码运行)

如果你想体验 **Electron 桌面端功能**（如打开本地文件夹）或修改代码，请按以下步骤操作：

### 环境要求
* Python 3.11+
* Node.js 24+

### 1. 启动后端 (Flask)
```bash
cd backend
# 创建并激活虚拟环境
python -m venv venv
# Windows:
.\venv\Scripts\Activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
# 启动
python app.py
```

### 2. 启动前端 (Vue + Electron)
新建一个终端窗口：
```bash
cd frontend
# 安装依赖
npm install
# 启动开发模式 (包含 Electron 窗口)
npm run electron:dev
```

---

## 🛠️ 技术栈

* **前端**：Vue 3, Vite, Element Plus, Electron
* **后端**：Python Flask
* **数据库**：SQLite (轻量级/无需配置)
* **部署**：Docker, Nginx

---

## 🤝 贡献 (Contributing)

欢迎提交 Issue 或 Pull Request 来改进 VocaLog！

## 📄 开源协议

本项目采用 [MIT] 协议开源。