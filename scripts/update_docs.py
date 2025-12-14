#!/usr/bin/env python3
"""
文档自动更新工具
根据代码结构自动更新 README、ARCHITECTURE 等文档
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class DocsAutoUpdater:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.updates = []
    
    def update_all(self):
        """执行所有自动更新"""
        print("🔄 开始文档自动更新...\n")
        
        self.update_directory_tree()
        self.update_last_modified_dates()
        self.update_file_counts()
        
        self.print_summary()
    
    def update_directory_tree(self):
        """自动生成并更新项目目录树"""
        print("1️⃣ 更新项目目录树...")
        
        tree = self._generate_tree()
        
        readme_path = self.root / "README.md"
        if not readme_path.exists():
            print("   ⚠️  README.md 不存在，跳过\n")
            return
        
        content = readme_path.read_text(encoding='utf-8')
        
        # 查找项目结构部分
        pattern = r'(```\n金融数据分析助手/\n)(.*?)(\n```)'
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(
                pattern,
                r'\1' + tree + r'\3',
                content,
                flags=re.DOTALL
            )
            
            readme_path.write_text(new_content, encoding='utf-8')
            self.updates.append("✅ README.md 目录树已更新")
            print("   ✅ 目录树已更新\n")
        else:
            print("   ⚠️  未找到目录树标记，跳过\n")
    
    def update_last_modified_dates(self):
        """更新文档的"最后更新"日期"""
        print("2️⃣ 更新文档日期...")
        
        docs = [
            self.root / "docs" / "ARCHITECTURE.md",
            self.root / "optimization" / "ITERATION_GUIDE.md",
            self.root / "optimization" / "experiments" / "experiment_log.md"
        ]
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for doc in docs:
            if not doc.exists():
                continue
            
            content = doc.read_text(encoding='utf-8')
            
            # 更新 "Last Updated" 行
            if 'Last Updated' in content or '最后更新' in content:
                new_content = re.sub(
                    r'(\*\*Last Updated\*\*|\*\*最后更新\*\*):.*',
                    rf'\1: {today}',
                    content
                )
                
                doc.write_text(new_content, encoding='utf-8')
                self.updates.append(f"✅ {doc.name} 日期已更新")
        
        print(f"   ✅ 已更新 {len([d for d in docs if d.exists()])} 个文档\n")
    
    def update_file_counts(self):
        """更新文档中的文件统计信息"""
        print("3️⃣ 更新文件统计...")
        
        stats = {
            "core_modules": len(list((self.root / "core").glob("*.py"))),
            "optimization_notebooks": len(list((self.root / "optimization").glob("*.ipynb"))),
            "docs_count": len(list((self.root / "docs").glob("*.md")))
        }
        
        print(f"   📊 统计: {stats}")
        print(f"   ✅ 统计完成\n")
        
        self.updates.append(f"📊 文件统计: {stats}")
    
    def _generate_tree(self, max_depth: int = 2) -> str:
        """生成目录树（简化版）"""
        lines = []
        
        # 主要目录结构（手动定义以保证顺序和注释）
        structure = {
            "core/": "核心基础设施",
            "docs/": "📚 项目文档",
            "optimization/": "🔬 优化与评估框架",
            ".git-hooks/": "🪝 Git 自动化钩子",
            "outputs/": "🚧 Agent 运行时输出"
        }
        
        for dir_name, comment in structure.items():
            path = self.root / dir_name
            if path.exists():
                indent = "├── "
                lines.append(f"{indent}{dir_name:<30} # {comment}")
                
                # 添加子项（仅第一级）
                if dir_name == "docs/":
                    for sub in sorted(path.glob("*.md")):
                        lines.append(f"│   ├── {sub.name}")
                elif dir_name in ["optimization/", ".git-hooks/"]:
                    lines.append(f"│   ├── ...")
        
        # 关键文件
        key_files = [
            "README.md", "CHANGELOG.md", "requirements.txt", 
            "agent_logic.py", "financial_agent_demo.ipynb"
        ]
        
        for filename in key_files:
            if (self.root / filename).exists():
                lines.append(f"├── {filename}")
        
        return "\n".join(lines)
    
    def print_summary(self):
        """打印更新摘要"""
        print("\n" + "="*60)
        print("📋 文档更新摘要")
        print("="*60 + "\n")
        
        if self.updates:
            for update in self.updates:
                print(update)
        else:
            print("ℹ️  没有需要更新的内容")
        
        print("\n" + "="*60 + "\n")


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    updater = DocsAutoUpdater(project_root)
    updater.update_all()


if __name__ == "__main__":
    main()
