"""Analysis result data models using Pydantic."""

from pydantic import BaseModel, Field, computed_field
from typing import List
import polars as pl


class AnalysisResult(BaseModel):
    project_coordinate: str
    used_undeclared: List[str] = Field(default_factory=list)
    unused_declared: List[str] = Field(default_factory=list)
    
    def to_polars_df(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """转换为两个DataFrame"""
        used_df = pl.DataFrame({
            "coordinate": self.used_undeclared, 
            "issue_type": ["used_undeclared"] * len(self.used_undeclared),
            "project": [self.project_coordinate] * len(self.used_undeclared)
        })
        unused_df = pl.DataFrame({
            "coordinate": self.unused_declared, 
            "issue_type": ["unused_declared"] * len(self.unused_declared),
            "project": [self.project_coordinate] * len(self.unused_declared)
        })
        return used_df, unused_df


class RedundancyCase(BaseModel):
    declared_dependency: str  # 声明但未使用的依赖A
    actually_used: List[str]  # 实际使用的传递依赖B列表
    dependency_path: List[str]  # A到B的路径
    recommendation: str  # 优化建议
    
    @computed_field
    @property
    def severity(self) -> str:
        """问题严重程度"""
        return "high" if len(self.actually_used) > 0 else "medium"