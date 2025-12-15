"""
SkillOrchestrator - Skill 编排器

统一管理所有 Skills 的加载、注册和调度。

核心职责：
1. 自动发现和加载所有 Skills
2. 聚合所有工具定义
3. 分发工具调用到对应 Skill
4. 提供 Skill 查询接口

参考：
- docs/ARCHITECTURE_CLAUDE_SKILLS.md 第 3.3 节
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from skills.base_skill import BaseSkill


class SkillOrchestrator:
    """
    Skill 编排器
    
    负责统一管理项目中的所有 Skills，提供工具注册和调度机制。
    
    Attributes:
        skills_dir (Path): Skills 根目录
        skills (Dict[str, BaseSkill]): 已加载的 Skills（key 为 skill name）
    """
    
    def __init__(self, skills_dir: str | Path = None):
        """
        初始化编排器
        
        Args:
            skills_dir: Skills 根目录，默认为项目根目录的 skills/
        """
        if skills_dir is None:
            # 默认使用项目根目录的 skills/
            project_root = Path(__file__).parent.parent
            skills_dir = project_root / "skills"
        
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, BaseSkill] = {}
        
        # 自动加载所有 Skills
        self.load_skills()
    
    def load_skills(self) -> None:
        """
        自动发现并加载所有 Skills
        
        扫描 skills_dir 下的所有子目录，查找包含 SKILL.md 的目录并加载。
        """
        if not self.skills_dir.exists():
            print(f"⚠️  Skills 目录不存在: {self.skills_dir}")
            return
        
        # 扫描所有子目录
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            # 跳过特殊目录
            if skill_dir.name.startswith('_') or skill_dir.name.startswith('.'):
                continue
            
            # 检查是否包含 SKILL.md
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            # 动态加载 Skill
            try:
                skill = self._load_skill(skill_dir)
                self.register_skill(skill)
                print(f"✅ 已加载 Skill: {skill.name}")
            
            except Exception as e:
                print(f"❌ 加载 Skill 失败 ({skill_dir.name}): {e}")
    
    def _load_skill(self, skill_dir: Path) -> BaseSkill:
        """
        动态加载单个 Skill
        
        Args:
            skill_dir: Skill 目录路径
        
        Returns:
            BaseSkill: 加载的 Skill 实例
        
        Raises:
            ImportError: 如果 Skill 类不存在
        """
        skill_name = skill_dir.name
        
        # 尝试导入对应的 Skill 类
        # 约定：skills/<skill-name>/skill.py 中定义 Skill 类
        skill_module_path = skill_dir / "skill.py"
        
        if not skill_module_path.exists():
            raise ImportError(
                f"Skill implementation not found: {skill_module_path}\n"
                f"Please create skill.py with a Skill class inheriting BaseSkill"
            )
        
        # 动态导入模块
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            f"skills.{skill_name}.skill",
            skill_module_path
        )
        
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to load module spec for {skill_name}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找 Skill 类（继承自 BaseSkill）
        skill_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # 检查是否是 BaseSkill 的子类（但不是 BaseSkill 本身）
            if (isinstance(attr, type) and 
                issubclass(attr, BaseSkill) and 
                attr is not BaseSkill):
                skill_class = attr
                break
        
        if skill_class is None:
            raise ImportError(
                f"No Skill class found in {skill_module_path}\n"
                f"Please define a class inheriting from BaseSkill"
            )
        
        # 实例化 Skill
        return skill_class(skill_dir)
    
    def register_skill(self, skill: BaseSkill) -> None:
        """
        注册一个 Skill
        
        Args:
            skill: Skill 实例
        """
        self.skills[skill.name] = skill
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取指定 Skill
        
        Args:
            skill_name: Skill 名称
        
        Returns:
            BaseSkill 或 None（如果不存在）
        """
        return self.skills.get(skill_name)
    
    def get_all_skill_names(self) -> List[str]:
        """
        获取所有已加载的 Skill 名称
        
        Returns:
            List[str]: Skill 名称列表
        """
        return list(self.skills.keys())
    
    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        聚合所有 Skills 的工具定义
        
        Returns:
            List[Dict]: 所有工具定义的列表
        """
        all_tools = []
        
        for skill_name, skill in self.skills.items():
            try:
                tools = skill.get_tool_definitions()
                all_tools.extend(tools)
            
            except Exception as e:
                print(f"⚠️  获取 {skill_name} 工具定义失败: {e}")
        
        return all_tools
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        分发工具调用到对应 Skill
        
        Args:
            tool_name: 工具名称
            tool_input: 工具参数
        
        Returns:
            Any: 工具执行结果
        
        Raises:
            ValueError: 如果找不到对应的工具
        """
        # 遍历所有 Skills，查找包含该工具的 Skill
        for skill_name, skill in self.skills.items():
            try:
                tools = skill.get_tool_definitions()
                tool_names = [tool['name'] for tool in tools]
                
                if tool_name in tool_names:
                    # 找到了！执行工具
                    return skill.execute_tool(tool_name, tool_input)
            
            except Exception as e:
                # 继续查找其他 Skills
                continue
        
        # 没有找到对应的工具
        raise ValueError(
            f"Tool '{tool_name}' not found in any Skill.\n"
            f"Available tools: {self.get_all_tool_names()}"
        )
    
    def get_all_tool_names(self) -> List[str]:
        """
        获取所有可用的工具名称
        
        Returns:
            List[str]: 工具名称列表
        """
        all_tools = self.get_all_tool_definitions()
        return [tool['name'] for tool in all_tools]
    
    def get_skill_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有 Skills 的摘要信息
        
        Returns:
            Dict: 每个 Skill 的元数据和工具清单
        """
        summary = {}
        
        for skill_name, skill in self.skills.items():
            tools = skill.get_tool_definitions()
            tool_names = [tool['name'] for tool in tools]
            
            summary[skill_name] = {
                'name': skill.name,
                'description': skill.description,
                'tools': tool_names,
                'tool_count': len(tool_names)
            }
        
        return summary
    
    def __repr__(self) -> str:
        skill_count = len(self.skills)
        tool_count = len(self.get_all_tool_names())
        return (
            f"<SkillOrchestrator: {skill_count} skills, "
            f"{tool_count} tools>"
        )
