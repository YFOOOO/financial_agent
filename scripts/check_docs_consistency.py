#!/usr/bin/env python3
"""
文档一致性检查工具
检查项目文档中的路径引用、版本号、目录结构是否一致
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple

class DocsConsistencyChecker:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.errors = []
        self.warnings = []
        
    def check_all(self) -> bool:
        """运行所有检查"""
        print("🔍 开始文档一致性检查...\n")
        
        self.check_file_references()
        self.check_version_consistency()
        self.check_directory_structure()
        self.check_document_links()
        
        self.print_report()
        return len(self.errors) == 0
    
    def check_file_references(self):
        """检查文档中引用的文件是否存在"""
        print("1️⃣ 检查文件引用...")
        
        docs_to_check = [
            self.root / "README.md",
            self.root / "docs" / "ARCHITECTURE.md",
            self.root / "optimization" / "README.md"
        ]
        
        for doc_path in docs_to_check:
            if not doc_path.exists():
                self.warnings.append(f"文档不存在: {doc_path}")
                continue
                
            content = doc_path.read_text(encoding='utf-8')
            
            # 查找 Markdown 链接: [text](path)
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            
            for text, link in links:
                if link.startswith('http'):
                    continue  # 跳过外部链接
                    
                if link.startswith('#'):
                    continue  # 跳过锚点
                
                # 解析相对路径
                target_path = (doc_path.parent / link).resolve()
                
                if not target_path.exists():
                    self.errors.append(
                        f"❌ {doc_path.name}: 引用的文件不存在\n"
                        f"   链接文本: [{text}]\n"
                        f"   目标路径: {link}\n"
                        f"   解析路径: {target_path}"
                    )
        
        print(f"   ✅ 检查完成\n")
    
    def check_version_consistency(self):
        """检查版本号是否一致"""
        print("2️⃣ 检查版本号一致性...")
        
        version_sources = {
            "README.md": self._extract_version_from_readme(),
            "CHANGELOG.md": self._extract_version_from_changelog(),
            "Git Tag": self._extract_git_tag_version()
        }
        
        versions = list(version_sources.values())
        if len(set(versions)) > 1:
            self.warnings.append(
                f"⚠️  版本号不一致:\n" + 
                "\n".join([f"   {src}: {ver}" for src, ver in version_sources.items()])
            )
        else:
            print(f"   ✅ 版本号一致: {versions[0]}\n")
    
    def check_directory_structure(self):
        """检查实际目录结构与文档中的描述是否一致"""
        print("3️⃣ 检查目录结构...")
        
        readme_path = self.root / "README.md"
        if not readme_path.exists():
            self.errors.append("❌ README.md 不存在")
            return
        
        content = readme_path.read_text(encoding='utf-8')
        
        # 提取项目结构代码块
        structure_match = re.search(
            r'```\n金融数据分析助手/\n(.*?)\n```', 
            content, 
            re.DOTALL
        )
        
        if not structure_match:
            self.warnings.append("⚠️  README.md 中未找到项目结构说明")
            return
        
        # 检查关键目录是否存在
        key_dirs = ['core', 'docs', 'optimization', 'outputs', '.git-hooks']
        missing_dirs = []
        
        for dir_name in key_dirs:
            if not (self.root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.errors.append(
                f"❌ README.md 中提到但实际不存在的目录: {', '.join(missing_dirs)}"
            )
        else:
            print(f"   ✅ 关键目录完整\n")
    
    def check_document_links(self):
        """检查文档之间的交叉引用"""
        print("4️⃣ 检查文档交叉引用...")
        
        # 检查 README.md 是否正确引用其他文档
        readme = self.root / "README.md"
        if readme.exists():
            content = readme.read_text(encoding='utf-8')
            
            expected_refs = [
                'docs/docs.md',
                'docs/spec.md', 
                'docs/ARCHITECTURE.md',
                'optimization/README.md'
            ]
            
            for ref in expected_refs:
                if ref not in content:
                    self.warnings.append(
                        f"⚠️  README.md 未引用: {ref}"
                    )
        
        print(f"   ✅ 检查完成\n")
    
    def _extract_version_from_readme(self) -> str:
        """从 README 提取版本号"""
        readme = self.root / "README.md"
        if not readme.exists():
            return "unknown"
        
        content = readme.read_text(encoding='utf-8')
        match = re.search(r'v(\d+\.\d+\.\d+)', content)
        return f"v{match.group(1)}" if match else "unknown"
    
    def _extract_version_from_changelog(self) -> str:
        """从 CHANGELOG 提取最新版本号"""
        changelog = self.root / "CHANGELOG.md"
        if not changelog.exists():
            return "unknown"
        
        content = changelog.read_text(encoding='utf-8')
        match = re.search(r'\[(\d+\.\d+\.\d+)\]', content)
        return f"v{match.group(1)}" if match else "unknown"
    
    def _extract_git_tag_version(self) -> str:
        """从 Git Tag 提取最新版本号"""
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def print_report(self):
        """打印检查报告"""
        print("\n" + "="*60)
        print("📊 文档一致性检查报告")
        print("="*60 + "\n")
        
        if self.errors:
            print("❌ 错误 (必须修复):\n")
            for error in self.errors:
                print(error)
                print()
        
        if self.warnings:
            print("⚠️  警告 (建议检查):\n")
            for warning in self.warnings:
                print(warning)
                print()
        
        if not self.errors and not self.warnings:
            print("✅ 所有检查通过！文档完全一致。\n")
        
        print("="*60)
        print(f"总计: {len(self.errors)} 个错误, {len(self.warnings)} 个警告")
        print("="*60 + "\n")


def main():
    """主函数"""
    import sys
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    checker = DocsConsistencyChecker(project_root)
    success = checker.check_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
