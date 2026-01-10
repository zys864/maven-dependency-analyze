"""Dependency data models using Pydantic."""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Set


class Dependency(BaseModel):
    group_id: str
    artifact_id: str
    version: str
    scope: str = ""
    type: str = "jar"
    classifier: str = ""
    optional: bool = False
    children: List['Dependency'] = Field(default_factory=list)
    parent: Optional['Dependency'] = Field(default=None, exclude=True)  # 避免循环引用
    depth: int = 0
    
    model_config = {"arbitrary_types_allowed": True}
    
    @computed_field
    @property
    def coordinate(self) -> str:
        """返回 groupId:artifactId:type:version:scope 格式"""
        return f"{self.group_id}:{self.artifact_id}:{self.type}:{self.version}:{self.scope}"
    
    @computed_field
    @property
    def simple_coordinate(self) -> str:
        """返回简化格式 groupId:artifactId:version"""
        return f"{self.group_id}:{self.artifact_id}:{self.version}"
    
    def get_all_descendants(self) -> List['Dependency']:
        """递归获取所有传递依赖（扁平化）"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def find_path_to(self, target_coordinate: str) -> Optional[List['Dependency']]:
        """查找到某个依赖的路径"""
        if self.simple_coordinate == target_coordinate or self.coordinate == target_coordinate:
            return [self]
        for child in self.children:
            path = child.find_path_to(target_coordinate)
            if path:
                return [self] + path
        return None


class DependencyTree(BaseModel):
    root: Dependency
    all_dependencies: dict[str, List[Dependency]] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}
    
    def build_coordinate_index(self):
        """构建坐标索引以快速查找依赖"""
        self.all_dependencies.clear()
        
        def traverse(node: Dependency):
            coords = [node.coordinate, node.simple_coordinate]
            for coord in coords:
                if coord not in self.all_dependencies:
                    self.all_dependencies[coord] = []
                self.all_dependencies[coord].append(node)
            
            for child in node.children:
                traverse(child)
        
        traverse(self.root)
    
    def flatten(self) -> List[Dependency]:
        """扁平化所有依赖节点"""
        result = []
        
        def traverse(node: Dependency):
            result.append(node)
            for child in node.children:
                traverse(child)
        
        traverse(self.root)
        return result
    
    def find_dependency(self, coordinate: str) -> List[Dependency]:
        """根据coordinate查找所有匹配节点"""
        return self.all_dependencies.get(coordinate, [])
    
    @computed_field
    @property
    def max_depth(self) -> int:
        """获取树的最大深度"""
        return max((dep.depth for dep in self.flatten()), default=0)
    
    @computed_field
    @property
    def total_dependencies(self) -> int:
        """获取依赖总数"""
        return len(self.flatten())
    
    @computed_field
    @property
    def direct_dependencies(self) -> int:
        """获取直接依赖数量（depth=1）"""
        return len([dep for dep in self.flatten() if dep.depth == 1])
    
    def to_polars_df(self) -> 'pl.DataFrame':
        """转换为Polars DataFrame用于分析"""
        import polars as pl
        
        flattened = self.flatten()
        data = {
            "group_id": [d.group_id for d in flattened],
            "artifact_id": [d.artifact_id for d in flattened],
            "version": [d.version for d in flattened],
            "scope": [d.scope for d in flattened],
            "type": [d.type for d in flattened],
            "depth": [d.depth for d in flattened],
            "coordinate": [d.coordinate for d in flattened],
            "simple_coordinate": [d.simple_coordinate for d in flattened],
        }
        return pl.DataFrame(data)


# Update forward reference
Dependency.model_rebuild()