# 🛠️ 脚本工具目录

> 项目自动化脚本与工具集

## 📁 脚本列表

### 1. `check_docs_consistency.py`
**功能**: 文档一致性检查

**检查项**:
- 文件引用有效性（Markdown 链接）
- 版本号一致性（README, CHANGELOG, Git Tag）
- 目录结构与文档描述对齐
- 文档交叉引用正确性

**使用**:
```bash
python3 scripts/check_docs_consistency.py

# 输出示例:
# ✅ 所有检查通过！文档完全一致。
# 或
# ❌ 错误: README.md 引用的文件不存在: docs/missing.md
```

**退出码**:
- `0`: 所有检查通过
- `1`: 存在错误

---

### 2. `update_docs.py`
**功能**: 文档自动更新

**更新内容**:
- 项目目录树（README.md）
- 文档更新日期（ARCHITECTURE.md, ITERATION_GUIDE.md 等）
- 文件统计信息（模块数、Notebook 数）

**使用**:
```bash
python3 scripts/update_docs.py

# 输出示例:
# 📋 文档更新摘要
# ✅ README.md 目录树已更新
# ✅ ARCHITECTURE.md 日期已更新
# 📊 文件统计: {'core_modules': 8, 'optimization_notebooks': 1}
```

**特点**:
- 非破坏性（仅更新特定标记的部分）
- 可扩展（易于添加新的更新规则）

---

## 🔄 集成方式

### 方式一：手动运行
```bash
# 提交前检查
python3 scripts/check_docs_consistency.py

# 有问题时自动修复
python3 scripts/update_docs.py

# 再次检查
python3 scripts/check_docs_consistency.py
```

### 方式二：Git Hook 集成
已集成在 `.git-hooks/pre-commit` 中，每次提交自动运行。

### 方式三：GitHub Actions（未来）
可配置为 CI 流程的一部分：
```yaml
- name: Check Documentation
  run: python3 scripts/check_docs_consistency.py
```

---

## 📝 开发新脚本指南

### 脚本规范
1. **文件名**: 使用小写+下划线（如 `update_docs.py`）
2. **Shebang**: `#!/usr/bin/env python3`
3. **文档字符串**: 模块级别的 docstring 说明功能
4. **退出码**: 成功 `0`, 失败 `非0`
5. **输出格式**: 使用 emoji 和颜色标识状态

### 代码结构
```python
#!/usr/bin/env python3
"""
脚本功能简述
"""

import os
from pathlib import Path

class ToolName:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
    
    def run(self):
        """主逻辑"""
        pass

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tool = ToolName(project_root)
    tool.run()

if __name__ == "__main__":
    main()
```

### 添加到此 README
新脚本开发完成后，请在上面添加说明条目。

---

## 🧪 测试脚本

### 单元测试（未来）
```bash
# 运行所有测试
pytest scripts/tests/

# 测试特定脚本
pytest scripts/tests/test_check_docs.py
```

### 手动测试
```bash
# 测试检查脚本（应该通过）
python3 scripts/check_docs_consistency.py

# 测试更新脚本（应该有输出）
python3 scripts/update_docs.py

# 制造错误测试（修改 README 引用不存在的文件）
# 应该检测到错误
```

---

## 📚 相关文档

- [docs/DOCS_UPDATE_WORKFLOW.md](../docs/DOCS_UPDATE_WORKFLOW.md) - 文档更新工作流
- [.git-hooks/README.md](../.git-hooks/README.md) - Git Hook 说明
- [optimization/ITERATION_GUIDE.md](../optimization/ITERATION_GUIDE.md) - 迭代指南

---

## 🤝 贡献

欢迎贡献新的自动化脚本！

**建议脚本方向**:
- [ ] 代码统计工具（行数、函数数、文档覆盖率）
- [ ] 依赖检查工具（requirements.txt vs 实际导入）
- [ ] Notebook 清理工具（清除输出、重置编号）
- [ ] 性能基准对比工具（自动生成对比报告）
- [ ] 文档链接检查（包括外部链接有效性）

---

**维护者**: YFOOOO  
**最后更新**: 2025-12-14
