"""
BaseSkill - Skill 抽象基类

定义所有 Skill 必须实现的接口，遵循 Anthropic Agent Skills Spec v1.0 规范。

核心职责：
1. 加载 SKILL.md（YAML frontmatter + Markdown body）
2. 提供工具定义（get_tool_definitions）
3. 执行工具调用（execute_tool）

参考：
- docs/ARCHITECTURE_CLAUDE_SKILLS.md 第 6.1 节
- https://github.com/Claude-Skills-Org/skills-main/blob/main/agent_skills_spec.md
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class BaseSkill(ABC):
    """
    Skill 抽象基类
    
    所有 Skill 必须继承此类并实现抽象方法。
    
    Attributes:
        skill_dir (Path): Skill 目录路径
        metadata (Dict): 从 SKILL.md YAML frontmatter 加载的元数据
        instructions (str): SKILL.md Markdown body 内容
    """
    
    def __init__(self, skill_dir: str | Path):
        """
        初始化 Skill
        
        Args:
            skill_dir: Skill 目录路径（包含 SKILL.md）
        
        Raises:
            FileNotFoundError: 如果 SKILL.md 不存在
            ValueError: 如果 SKILL.md 格式不正确
        """
        self.skill_dir = Path(skill_dir)
        self.skill_md_path = self.skill_dir / "SKILL.md"
        
        if not self.skill_md_path.exists():
            raise FileNotFoundError(
                f"SKILL.md not found in {self.skill_dir}"
            )
        
        self.metadata = self.load_metadata()
        self.instructions = self.load_instructions()
        
        # 验证必需字段
        self._validate_metadata()
    
    def load_metadata(self) -> Dict[str, Any]:
        """
        从 SKILL.md 加载 YAML frontmatter
        
        Returns:
            Dict: 包含 name, description 等元数据
        
        Raises:
            ValueError: 如果 frontmatter 格式不正确
        """
        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 YAML frontmatter（被 --- 包围）
        if not content.startswith('---\n'):
            raise ValueError(
                f"SKILL.md must start with YAML frontmatter (---)"
            )
        
        try:
            # 找到第二个 ---
            parts = content.split('---\n', 2)
            if len(parts) < 3:
                raise ValueError("YAML frontmatter must end with ---")
            
            frontmatter_str = parts[1]
            metadata = yaml.safe_load(frontmatter_str)
            
            if not isinstance(metadata, dict):
                raise ValueError("YAML frontmatter must be a dictionary")
            
            return metadata
        
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in SKILL.md: {e}") from e
    
    def load_instructions(self) -> str:
        """
        加载 SKILL.md Markdown body（YAML frontmatter 之后的内容）
        
        Returns:
            str: Markdown 格式的使用说明
        """
        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 Markdown body（第二个 --- 之后）
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return ""
        
        return parts[2].strip()
    
    def _validate_metadata(self) -> None:
        """
        验证元数据必需字段
        
        根据官方规范，name 和 description 是必需的。
        
        Raises:
            ValueError: 如果缺少必需字段
        """
        required_fields = ['name', 'description']
        
        for field in required_fields:
            if field not in self.metadata:
                raise ValueError(
                    f"Missing required field '{field}' in SKILL.md frontmatter"
                )
        
        # 验证 name 与目录名一致（官方规范要求）
        expected_name = self.skill_dir.name
        actual_name = self.metadata['name']
        
        if actual_name != expected_name:
            raise ValueError(
                f"Skill name '{actual_name}' must match directory name '{expected_name}'"
            )
    
    @property
    def name(self) -> str:
        """Skill 名称（来自 metadata）"""
        return self.metadata['name']
    
    @property
    def description(self) -> str:
        """
        Skill 描述（触发机制的关键！）
        
        这是 Claude 决定是否加载此 Skill 的核心依据。
        必须包含"做什么"和"何时使用"。
        """
        return self.metadata['description']
    
    @abstractmethod
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        返回该 Skill 提供的工具定义
        
        Returns:
            List[Dict]: LangChain 工具定义列表，每个工具包含：
                - name: 工具名称
                - description: 工具描述
                - parameters: 参数 schema（JSON Schema 格式）
        
        Example:
            [
                {
                    "name": "fetch_stock_data",
                    "description": "获取股票历史数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "股票代码"},
                            "days": {"type": "integer", "description": "天数"}
                        },
                        "required": ["symbol", "days"]
                    }
                }
            ]
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称（来自 get_tool_definitions）
            tool_input: 工具参数（Dict 格式）
        
        Returns:
            Any: 工具执行结果（通常是 str, Dict, DataFrame 等）
        
        Raises:
            ValueError: 如果 tool_name 不存在
            Exception: 工具执行失败时的具体错误
        """
        pass
    
    def get_script_path(self, script_name: str) -> Path:
        """
        获取 scripts/ 目录下的脚本路径
        
        Args:
            script_name: 脚本文件名（如 "fetch_stock.py"）
        
        Returns:
            Path: 完整的脚本路径
        """
        return self.skill_dir / "scripts" / script_name
    
    def get_reference_path(self, reference_name: str) -> Path:
        """
        获取 references/ 目录下的参考文档路径
        
        Args:
            reference_name: 文档文件名（如 "api_docs.md"）
        
        Returns:
            Path: 完整的文档路径
        """
        return self.skill_dir / "references" / reference_name
    
    def get_asset_path(self, asset_name: str) -> Path:
        """
        获取 assets/ 目录下的资源路径
        
        Args:
            asset_name: 资源文件名（如 "template.html"）
        
        Returns:
            Path: 完整的资源路径
        """
        return self.skill_dir / "assets" / asset_name
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
