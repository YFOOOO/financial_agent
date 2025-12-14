# Git Hooks 说明

> 自动化质量检查工具

## 📋 可用 Hooks

### pre-commit（提交前检查）

在每次 `git commit` 之前自动运行，确保代码质量。

**检查项目**:
1. ✅ **代码格式**: 自动运行 Black 格式化（如果已安装）
2. ✅ **类型检查**: MyPy 静态类型分析（如果已安装）
3. ✅ **语法检查**: Python 语法验证
4. ✅ **导入检查**: 确保所有模块可正常导入
5. ✅ **单元测试**: 快速测试套件（如果存在）
6. ✅ **性能回归**: 对比基准数据（可选）
7. ✅ **文档提醒**: 核心代码修改时提醒更新文档
8. ✅ **Commit Message**: 建议使用 emoji 规范

## 🚀 安装方法

### macOS/Linux

```bash
# 进入项目目录
cd "/Users/yf/Documents/GitHub/AI Agent Adventure/My Agents/金融数据分析助手"

# 给脚本添加执行权限
chmod +x .git-hooks/pre-commit

# 配置 Git 使用自定义 hooks 目录
git config core.hooksPath .git-hooks

# 验证配置
git config core.hooksPath
# 应该输出: .git-hooks
```

### Windows

```powershell
# 进入项目目录
cd "C:\...\My Agents\金融数据分析助手"

# 配置 Git 使用自定义 hooks 目录
git config core.hooksPath .git-hooks

# 注意: Windows 上可能需要安装 Git Bash 来运行 shell 脚本
```

## 🔧 配置选项

### 跳过某次检查

如果需要临时跳过 pre-commit 检查（不推荐）：

```bash
git commit --no-verify -m "紧急修复"
```

### 自定义检查

编辑 `.git-hooks/pre-commit` 文件，可以：
- 注释掉不需要的检查
- 添加自定义检查逻辑
- 调整检查顺序

### 依赖工具安装

```bash
# 代码格式化工具
pip install black

# 类型检查工具
pip install mypy

# 单元测试框架
pip install pytest
```

## 📝 Commit Message 规范

推荐使用 emoji 前缀 + 简洁描述：

```bash
# 性能优化
git commit -m "⚡ 优化: 减少 LLM Token 使用 30%"

# Bug 修复
git commit -m "🐛 修复: 数据获取超时问题"

# 文档更新
git commit -m "📝 文档: 更新 README 安装说明"

# 新功能
git commit -m "✨ 功能: 添加数据缓存机制"

# 配置修改
git commit -m "🔧 配置: 更新 requirements.txt"

# 代码格式
git commit -m "🎨 格式: Black 代码格式化"

# 代码重构
git commit -m "♻️  重构: 优化 Agent 逻辑结构"

# 删除代码
git commit -m "🔥 清理: 移除过时的测试代码"

# 测试相关
git commit -m "✅ 测试: 添加指标计算单元测试"

# 部署相关
git commit -m "🚀 部署: 推送 v1.2.0 到生产环境"
```

## 🎯 工作流示例

```bash
# 1. 修改代码
vim core/llm_client.py

# 2. 添加到暂存区
git add core/llm_client.py

# 3. 提交（自动触发检查）
git commit -m "⚡ 优化: 减少 Prompt Token"

# 输出示例:
# 🔍 运行提交前检查...
# 📝 检查代码格式...
# ✅ 代码格式 通过
# 🐍 检查 Python 语法...
# ✅ 语法检查 通过
# 📦 检查模块导入...
# ✅ 模块导入 通过
# ✅ 所有检查通过，可以提交！
```

## ⚠️ 常见问题

### Q: Hook 没有执行？
A: 检查是否正确配置了 `core.hooksPath`：
```bash
git config core.hooksPath
```

### Q: 权限被拒绝？
A: 确保脚本有执行权限：
```bash
chmod +x .git-hooks/pre-commit
```

### Q: Windows 上无法运行？
A: 需要安装 Git Bash 或使用 WSL。

### Q: 检查太慢？
A: 可以注释掉耗时的检查项，如单元测试。

## 🔄 禁用/启用

### 临时禁用
```bash
git config core.hooksPath ""
```

### 重新启用
```bash
git config core.hooksPath .git-hooks
```

---

**维护者**: YFOOOO  
**最后更新**: 2025-12-14
