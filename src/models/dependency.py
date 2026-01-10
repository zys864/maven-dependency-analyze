"""Maven 依赖节点和依赖树数据模型"""

from typing import Optional, List, Set
from pydantic import BaseModel, Field, computed_field
import polars as pl


class Dependency(BaseModel):
    """Maven 依赖节点

    表示依赖树中的一个节点，包含依赖的完整信息和父子关系
    """

    group_id: str
    artifact_id: str
    version: str
    scope: str = ""  # compile/test/runtime/provided等
    type: str = "jar"
    classifier: str = ""
    optional: bool = False
    children: List["Dependency"] = Field(default_factory=list)
    parent: Optional["Dependency"] = Field(default=None, exclude=True)  # 避免循环引用序列化问题
    depth: int = 0  # 在依赖树中的深度，根节点为0

    model_config = {"arbitrary_types_allowed": True}

    @computed_field
    @property
    def coordinate(self) -> str:
        """返回完整坐标: groupId:artifactId:type:version:scope"""
        return f"{self.group_id}:{self.artifact_id}:{self.type}:{self.version}:{self.scope}"

    @computed_field
    @property
    def simple_coordinate(self) -> str:
        """返回简化坐标: groupId:artifactId:version"""
        return f"{self.group_id}:{self.artifact_id}:{self.version}"

    @computed_field
    @property
    def display_name(self) -> str:
        """返回用于显示的名称"""
        if self.scope:
            return f"{self.group_id}:{self.artifact_id}:{self.version} [{self.scope}]"
        return f"{self.group_id}:{self.artifact_id}:{self.version}"

    def get_all_descendants(self) -> Set["Dependency"]:
        """递归获取所有传递依赖（扁平化）"""
        descendants = set()
        for child in self.children:
            descendants.add(child)
            descendants.update(child.get_all_descendants())
        return descendants

    def find_path_to(self, target_coordinate: str) -> Optional[List["Dependency"]]:
        """查找到某个依赖的路径

        Args:
            target_coordinate: 目标依赖的坐标

        Returns:
            如果找到，返回从当前节点到目标节点的路径；否则返回 None
        """
        if self.coordinate == target_coordinate or self.simple_coordinate == target_coordinate:
            return [self]

        for child in self.children:
            path = child.find_path_to(target_coordinate)
            if path:
                return [self] + path

        return None

    def __hash__(self):
        """使 Dependency 可哈希，用于 Set 操作"""
        return hash(self.coordinate)

    def __eq__(self, other):
        """定义相等性比较"""
        if not isinstance(other, Dependency):
            return False
        return self.coordinate == other.coordinate


class DependencyTree(BaseModel):
    """Maven 依赖树

    表示完整的 Maven 依赖树结构，提供查询和分析功能
    """

    root: Dependency
    all_dependencies: dict[str, List[Dependency]] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def flatten(self) -> List[Dependency]:
        """扁平化所有依赖节点（深度优先遍历）"""
        result = []

        def traverse(node: Dependency):
            result.append(node)
            for child in node.children:
                traverse(child)

        traverse(self.root)
        return result

    def find_dependency(self, coordinate: str) -> List[Dependency]:
        """根据 coordinate 查找所有匹配节点（可能在树中多处出现）"""
        return self.all_dependencies.get(coordinate, [])

    @computed_field
    @property
    def max_depth(self) -> int:
        """获取树的最大深度"""
        flattened = self.flatten()
        return max((dep.depth for dep in flattened), default=0)

    @computed_field
    @property
    def total_dependencies(self) -> int:
        """获取总依赖数（包括根节点）"""
        return len(self.flatten())

    @computed_field
    @property
    def direct_dependencies(self) -> List[Dependency]:
        """获取直接依赖（depth=1）"""
        return self.root.children

    def to_polars_df(self) -> pl.DataFrame:
        """转换为 Polars DataFrame 用于分析

        Returns:
            包含所有依赖信息的 DataFrame
        """
        flattened = self.flatten()

        # 构建路径信息
        def get_path(dep: Dependency) -> str:
            path = []
            current = dep
            while current.parent is not None:
                path.insert(0, f"{current.parent.artifact_id}")
                current = current.parent
            return " → ".join(path) if path else "root"

        data = {
            "group_id": [d.group_id for d in flattened],
            "artifact_id": [d.artifact_id for d in flattened],
            "version": [d.version for d in flattened],
            "scope": [d.scope for d in flattened],
            "type": [d.type for d in flattened],
            "depth": [d.depth for d in flattened],
            "coordinate": [d.coordinate for d in flattened],
            "simple_coordinate": [d.simple_coordinate for d in flattened],
            "path": [get_path(d) for d in flattened],
        }

        return pl.DataFrame(data)

    def get_dependencies_by_depth(self, depth: int) -> List[Dependency]:
        """获取指定深度的所有依赖"""
        return [dep for dep in self.flatten() if dep.depth == depth]

    def build_coordinate_index(self):
        """构建 coordinate 到节点列表的索引"""
        self.all_dependencies.clear()
        for dep in self.flatten():
            coord = dep.simple_coordinate
            if coord not in self.all_dependencies:
                self.all_dependencies[coord] = []
            self.all_dependencies[coord].append(dep)
