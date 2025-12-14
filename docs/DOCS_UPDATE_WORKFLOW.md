# 📝 文档更新工作流

> 每次迭代开发后的文档同步检查清单

## 🎯 使用时机

当你完成以下任一操作时，请执行本检查清单：

- ✅ 添加/删除/移动文件或目录
- ✅ 修改核心模块 (`core/`, `agent_logic.py`)
- ✅ 完成功能迭代（准备提交新版本）
- ✅ 重构项目结构
- ✅ 更新依赖或配置

---

## ✅ 文档对齐检查清单

### 📂 目录结构相关

#### 1. README.md 项目结构图
- [ ] 检查 "项目结构" 部分的目录树
- [ ] 确认新增/删除的目录已更新
- [ ] 确认目录注释与实际用途一致
- [ ] 验证所有引用的文件路径正确

**快速命令**:
```bash
# 查看实际目录结构
find . -maxdepth 2 -type d ! -path '*/\.*' | sort

# 对比 README.md 中的结构
grep -A 30 "项目结构" README.md
```

#### 2. 文档路径引用
- [ ] 检查 README.md 中的文档链接
- [ ] 检查 ARCHITECTURE.md 的相对路径
- [ ] 检查 optimization/README.md 的引用
- [ ] 确认所有 `[text](path)` 格式的链接有效

**快速命令**:
```bash
# 运行自动检查脚本
python3 scripts/check_docs_consistency.py
```

---

### 📝 版本与日期相关

#### 3. 版本号同步
- [ ] README.md 中的版本标识
- [ ] CHANGELOG.md 中的最新版本
- [ ] Git Tag 版本号
- [ ] package.json / requirements.txt（如果有版本号）

**快速检查**:
```bash
# 查看当前 Git Tag
git describe --tags --abbrev=0

# 查看 CHANGELOG 最新版本
head -n 20 CHANGELOG.md | grep -E "\[\d+\.\d+\.\d+\]"
```

#### 4. 更新日期
- [ ] ARCHITECTURE.md 底部的 "Last Updated"
- [ ] ITERATION_GUIDE.md 底部的 "最后更新"
- [ ] experiment_log.md 的日期字段
- [ ] CHANGELOG.md 的发布日期

**快速更新**:
```bash
# 自动更新所有文档日期
python3 scripts/update_docs.py
```

---

### 🔬 实验记录相关

#### 5. 实验日志完整性
- [ ] experiment_log.md 索引表已更新
- [ ] 新实验已添加完整记录
- [ ] 实验报告已归档到 `optimization/outputs/`
- [ ] CHANGELOG.md 已记录实验摘要

**模板检查**:
```markdown
### 实验 #XXX: [名称]
**日期**: YYYY-MM-DD
**目标**: [清晰的目标]
**结果**: ✅/⚠️/❌
**决策**: [合并/继续/放弃]
**相关文件**: [链接]
```

#### 6. 性能基准数据
- [ ] 基准 JSON 文件已保存
- [ ] 对比报告已生成
- [ ] 实验产出已归档到 `outputs/`
- [ ] 演示图片已添加到 Git（如需要）

---

### 🗂️ 新增/重命名文件处理

#### 7. 文件归档规范
- [ ] 文档放在 `docs/` 目录
- [ ] 实验产出放在 `optimization/outputs/`
- [ ] Agent 输出放在 `outputs/`（临时）
- [ ] 脚本工具放在 `scripts/`

#### 8. Git 追踪策略
- [ ] 临时文件已添加到 `.gitignore`
- [ ] 演示图片正确追踪（`optimization/outputs/*.png`）
- [ ] README 文档正确追踪
- [ ] 敏感信息已排除（.env, API keys）

**快速验证**:
```bash
# 检查 gitignore 规则
git check-ignore -v outputs/*.png
git check-ignore -v optimization/outputs/*.png
```

---

### 📚 交叉引用检查

#### 9. 文档间引用
- [ ] README → docs/ 的链接正确
- [ ] ARCHITECTURE → 其他文档的相对路径正确
- [ ] optimization/README → 主 README 的回链
- [ ] CHANGELOG → experiment_log 的引用

#### 10. 示例代码同步
- [ ] README 中的代码示例可运行
- [ ] ARCHITECTURE 的导入示例正确
- [ ] Notebook 中的路径引用有效
- [ ] 代码注释与文档描述一致

---

## 🤖 自动化工具

### 方式一：运行检查脚本
```bash
# 文档一致性检查
python3 scripts/check_docs_consistency.py

# 自动更新文档
python3 scripts/update_docs.py
```

### 方式二：Git Hook 自动检查
```bash
# 已集成在 pre-commit hook 中
# 每次提交时自动运行文档检查
git commit -m "your message"
```

### 方式三：手动逐项检查
使用本文档作为检查清单，逐项确认。

---

## 📋 快速检查命令总结

```bash
# 1. 目录结构对比
find . -maxdepth 2 -type d ! -path '*/\.*' | sort
grep -A 30 "项目结构" README.md

# 2. 文档链接检查
python3 scripts/check_docs_consistency.py

# 3. 版本号检查
git describe --tags --abbrev=0
grep -E "\[\d+\.\d+\.\d+\]" CHANGELOG.md | head -n 1

# 4. 文件引用检查
grep -r "\.md\|\.py" README.md docs/ARCHITECTURE.md

# 5. Git 追踪验证
git status --short
git check-ignore -v **/*.png

# 6. 实验记录检查
grep -E "^### 实验" optimization/experiments/experiment_log.md
```

---

## 🎯 最佳实践

### 提交前必做
1. ✅ 运行 `python3 scripts/check_docs_consistency.py`
2. ✅ 检查 Git 状态（无意外的未追踪文件）
3. ✅ 确认版本号一致（Git Tag = CHANGELOG = README）
4. ✅ 更新 CHANGELOG.md（如果是新版本）

### 大型重构后
1. ✅ 完整执行本检查清单
2. ✅ 运行 `python3 scripts/update_docs.py` 自动更新
3. ✅ 手动检查关键文档（README, ARCHITECTURE）
4. ✅ 生成对比报告（git diff）

### 迭代发布前
1. ✅ 确认 CHANGELOG 完整
2. ✅ 确认 experiment_log 已记录
3. ✅ 确认所有文档日期更新
4. ✅ 确认 Git Tag 已创建

---

## 📊 检查清单使用记录

| 日期 | 版本 | 检查人 | 问题数 | 状态 |
|------|------|--------|--------|------|
| 2025-12-14 | v1.1.1 | YuFan | 3 | ✅ 已修复 |
| | | | | |
| | | | | |

---

**维护者**: YFOOOO  
**最后更新**: 2025-12-14  
**版本**: v1.0
