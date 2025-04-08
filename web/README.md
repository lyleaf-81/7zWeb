# 文件管理系统
[![element-ui](https://img.shields.io/badge/Element--UI-2.15.14-green)](https://element.eleme.io)
[![vue](https://img.shields.io/badge/Vue.js-2.x-brightgreen)](https://vuejs.org)
基于Vue.js + Element UI构建的Web文件管理系统，提供目录导航、文件管理、压缩包解压等功能。
![Demo截图](screenshot.png) <!-- 建议实际添加截图 -->
## 功能亮点 ✨
### 文件管理
- 🗂 可视化目录结构展示
- 📂 支持多级目录导航（面包屑导航+返回上级）
- 📦 自动识别分卷压缩包（7z/zip等格式）
- 🔍 文件详细信息展示（大小、修改时间）
- 🗑️ 安全的文件删除机制（二次确认）
### 解压功能
- ⚡ 多线程解压任务管理
- 📊 实时解压进度展示
- 🔑 支持密码解压
- ❌ 解压错误日志查看
- 🚫 支持取消进行中的解压任务
### 用户体验
- 🎨 Element UI现代化界面
- ⏱ 自动刷新任务列表（2秒间隔）
- 🎯 分卷包解压指引提示
- ⌨️ 右键快速操作支持
- ⚠️ 错误提示与日志追踪
## 快速开始 🚀
### 前置要求
- Node.js v14+
- Vue CLI 5.x
- Element UI 2.15
### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/lyleaf-81/7zWeb.git
# 进入目录
cd 7zWeb
# 安装依赖
npm install
# 本地运行
npm run serve
