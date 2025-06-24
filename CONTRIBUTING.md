# 贡献指南 Contributing Guidelines

感谢您对 MeetSpot 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题 Issues
- 使用清晰的标题描述问题
- 提供重现步骤
- 包含错误信息和系统环境
- 如果可能，提供修复建议

### 功能请求 Feature Requests
- 详细描述新功能的用途
- 解释为什么这个功能对用户有价值
- 如果可能，提供实现思路

### 代码贡献 Pull Requests

#### 开发流程
1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature-name`
3. 进行开发并编写测试
4. 确保所有测试通过
5. 提交代码：`git commit -m "feat: add your feature"`
6. 推送分支：`git push origin feature/your-feature-name`
7. 创建 Pull Request

#### 代码规范
- **Python**: 遵循 PEP 8 规范
- **JavaScript**: 使用 ES6+ 语法
- **HTML/CSS**: 语义化标签，响应式设计
- **提交信息**: 使用约定式提交格式

#### 提交信息格式
```
类型(范围): 简短描述

详细描述（可选）

关联 issue（可选）
```

类型：
- `feat`: 新功能
- `fix`: 修复问题
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 代码审查
- 所有 PR 都需要经过代码审查
- 确保代码质量和一致性
- 测试覆盖率应保持在合理水平

## 🛠 开发环境设置

### 依赖要求
- Python 3.11+
- Node.js 16+ (如果需要前端构建)
- 高德地图 API 密钥

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/JasonRobertDestiny/MeetSpot.git
cd MeetSpot

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp config/config.toml.example config/config.toml
# 编辑 config.toml 添加您的高德地图 API 密钥

# 运行测试
python -m pytest tests/

# 启动开发服务器
python web_server.py
```

### 测试
```bash
# 运行所有测试
python test_optimizations.py
python test_multi_scenario.py
python comprehensive_test.py

# 运行特定测试
python -m pytest tests/test_specific.py -v
```

## 📝 文档贡献

- 文档使用 Markdown 格式
- 包含中英文版本
- 代码示例应该可运行
- 截图使用高质量图片

## 🎯 项目优先级

### 高优先级
- 性能优化
- 错误处理增强
- 用户体验改进
- 安全性提升

### 中优先级
- 新功能开发
- API 扩展
- 国际化支持

### 低优先级
- 代码重构
- 文档完善
- 样式调整

## 🤔 需要帮助？

- 查看 [Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues) 寻找适合新手的问题
- 在 [Discussions](https://github.com/JasonRobertDestiny/MeetSpot/discussions) 参与讨论
- 联系维护者：Johnrobertdestiny@gmail.com

## 📄 许可证

通过贡献代码，您同意您的贡献将在与项目相同的许可证下授权。

---

再次感谢您的贡献！🎉
