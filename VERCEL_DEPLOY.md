# Vercel 部署指南

## 🚀 部署步骤

### 1. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 2. 登录 Vercel
```bash
vercel login
```

### 3. 部署项目
在项目根目录运行：
```bash
vercel --prod
```

### 4. 环境变量配置 (如果需要)
在 Vercel 控制台中设置以下环境变量：
- `OPENAI_API_KEY`: OpenAI API密钥 (如果使用)
- `AMAP_API_KEY`: 高德地图API密钥 (如果使用)
- 其他需要的API密钥

## 📁 项目结构说明

```
MeetSpot/
├── api/
│   └── index.py          # Vercel入口点
├── web_server.py         # FastAPI应用主文件
├── requirements.txt      # Python依赖
├── vercel.json          # Vercel配置
├── package.json         # 项目配置
└── .vercelignore        # 忽略文件配置
```

## 🔧 配置说明

### vercel.json
- 指定Python运行时环境
- 配置路由规则
- 设置静态文件服务

### api/index.py
- Vercel无服务器函数入口点
- 导入并暴露FastAPI应用

## 🌐 访问方式

部署成功后，你将获得一个类似以下的URL：
```
https://meetspot-xxxxx.vercel.app
```

## 🛠️ 故障排除

### 1. 依赖问题
确保 `requirements.txt` 包含所有必要依赖。

### 2. 路径问题
所有文件路径应使用相对路径。

### 3. 静态文件
静态文件会自动从 `workspace/` 和 `docs/` 目录提供服务。

### 4. 日志查看
在 Vercel 控制台的 Functions 标签页可以查看运行日志。

## 📝 注意事项

1. **冷启动**: 无服务器函数可能有冷启动延迟
2. **超时限制**: Vercel免费版有10秒函数执行时间限制
3. **文件大小**: 单个函数包不能超过50MB

## 🔄 更新部署

代码更新后，重新运行：
```bash
vercel --prod
```

或者连接GitHub自动部署。
