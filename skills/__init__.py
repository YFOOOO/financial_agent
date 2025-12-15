"""
Skills 包初始化

提供 Skill 发现和加载的便捷接口。

核心功能：
1. discover_skills() - 自动发现所有 Skill 目录
2. load_skill() - 动态加载指定 Skill
3. 导出核心类供外部使用

参考：
- docs/ARCHITECTURE_CLAUDE_SKILLS.md 第 6.2 节
"""

from pathlib import Path
from typing import List, Optional
from skills.base_skill import BaseSkill
from skills.orchestrator import SkillOrchestrator

__all__ = [
    'BaseSkill',
    'SkillOrchestrator',
    'discover_skills',
    'load_skill',
]


def discover_skills(skills_dir: str | Path = None) -> List[str]:
    """
    发现所有 Skill 目录
    
    扫描 skills_dir，返回所有包含 SKILL.md 的目录名称。
    
    Args:
        skills_dir: Skills 根目录，默认为当前包目录
    
    Returns:
        List[str]: Skill 名称列表（目录名）
    
    Example:
        >>> discover_skills()
        ['financial-data-fetch', 'technical-indicators', 'chart-generation']
    """
    if skills_dir is None:
        skills_dir = Path(__file__).parent
    else:
        skills_dir = Path(skills_dir)
    
    if not skills_dir.exists():
        return []
    
    skill_names = []
    
    for item in skills_dir.iterdir():
        # 必须是目录
        if not item.is_dir():
            continue
        
        # 跳过特殊目录
        if item.name.startswith('_') or item.name.startswith('.'):
            continue
        
        # 跳过 __pycache__
        if item.name == '__pycache__':
            continue
        
        # 必须包含 SKILL.md
        if (item / "SKILL.md").exists():
            skill_names.append(item.name)
    
    return sorted(skill_names)


def load_skill(skill_name: str, skills_dir: str | Path = None) -> Optional[BaseSkill]:
    """
    动态加载指定 Skill
    
    Args:
        skill_name: Skill 名称（目录名）
        skills_dir: Skills 根目录，默认为当前包目录
    
    Returns:
        BaseSkill 实例，加载失败则返回 None
    
    Example:
        >>> skill = load_skill('financial-data-fetch')
        >>> if skill:
        ...     print(skill.description)
    """
    if skills_dir is None:
        skills_dir = Path(__file__).parent
    else:
        skills_dir = Path(skills_dir)
    
    skill_dir = skills_dir / skill_name
    
    if not skill_dir.exists():
        print(f"❌ Skill 目录不存在: {skill_dir}")
        return None
    
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ SKILL.md 不存在: {skill_md}")
        return None
    
    # 使用 SkillOrchestrator 的内部方法加载
    try:
        orchestrator = SkillOrchestrator(skills_dir)
        return orchestrator.get_skill(skill_name)
    
    except Exception as e:
        print(f"❌ 加载 Skill 失败 ({skill_name}): {e}")
        return None


# 版本信息
__version__ = "1.4.0"
__author__ = "YFOOOO"
__description__ = "金融数据分析助手 - Skill 模式架构（基于 Anthropic Agent Skills Spec v1.0）"
