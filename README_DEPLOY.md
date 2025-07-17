# MeetSpot 🗺️

智能会面点推荐系统 - 为每次聚会找到完美的地点

[![部署到Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/你的用户名/MeetSpot)

## 🌟 功能特点

- 🎯 **智能中心点计算**: 基于多个位置计算几何中心，确保公平性
- 🏢 **多场景推荐**: 同时搜索多种场所类型（咖啡馆+餐厅+图书馆）
- 📍 **多地点支持**: 支持2-10个参与者位置
- 🎨 **直观用户界面**: 现代化响应式设计
- 🚀 **实时推荐**: 快速生成个性化推荐
- 📊 **智能排序**: 基于评分、距离和用户需求的综合排序

## 🚀 快速部署

### 部署到 Vercel (推荐)

1. 点击上方的 "Deploy to Vercel" 按钮
2. 或者手动部署：

```bash
# 克隆仓库
git clone https://github.com/你的用户名/MeetSpot.git
cd MeetSpot

# 安装 Vercel CLI
npm install -g vercel

# 登录并部署
vercel login
vercel --prod
```

## 📋 环境变量配置

在 Vercel 控制台中设置以下环境变量：

- `OPENAI_API_KEY`: OpenAI API密钥（如果使用AI功能）
- `AMAP_API_KEY`: 高德地图API密钥（地图服务）

## 🛠️ 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python web_server.py
```

访问 http://localhost:8000

## 📁 项目结构

```
MeetSpot/
├── api/
│   └── index.py          # Vercel入口点
├── app/                  # 核心应用代码
├── web_server.py         # FastAPI应用
├── requirements.txt      # Python依赖
├── vercel.json          # Vercel配置
└── workspace/           # 静态文件和前端资源
```

## 🔧 技术栈

- **后端**: FastAPI, Python 3.11+
- **AI**: OpenAI GPT, 智能推荐算法
- **地图**: 高德地图 API
- **部署**: Vercel无服务器函数
- **前端**: HTML5, CSS3, JavaScript

## 📱 使用说明

1. 输入2-10个地点地址
2. 选择场所类型（咖啡馆、餐厅等）
3. 添加特殊要求（可选）
4. 获取智能推荐结果

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">
Made with ❤️ for better meetups
</div>
