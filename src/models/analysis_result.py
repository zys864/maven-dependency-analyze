"""Maven 依赖分析结果数据模型"""

from typing import List
from pydantic import BaseModel, Field, computed_field
import polars as pl


class AnalysisResult(BaseModel):
    """Maven 依赖分析结果

    存储 mvn dependency:analyze 命令的分析结果
    """

    project_coordinate: str  # 项目坐标
    used_undeclared: List[str] = Field(default_factory=list)  # 使用但未声明的依赖坐标
    unused_declared: List[str] = Field(default_factory=list)  # 声明但未使用的依赖坐标

    @computed_field
    @property
    def has_issues(self) -> bool:
        """是否存在依赖问题"""
        return len(self.used_undeclared) > 0 or len(self.unused_declared) > 0

    @computed_field
    @property
    def total_issues(self) -> int:
        """问题总数"""
        return len(self.used_undeclared) + len(self.unused_declared)

    def to_polars_df(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """转换为两个 DataFrame

        Returns:
            (used_undeclared_df, unused_declared_df) 两个 DataFrame
        """
        # 使用但未声明的依赖
        if self.used_undeclared:
            used_data = []
            for coord in self.used_undeclared:
                parts = coord.split(":")
                if len(parts) >= 3:
                    used_data.append(
                        {
                            "coordinate": coord,
                            "group_id": parts[0],
                            "artifact_id": parts[1],
                            "version": parts[3] if len(parts) > 3 else parts[2],
                            "scope": parts[4] if len(parts) > 4 else "",
                            "issue_type": "used_undeclared",
                        }
                    )
            used_df = pl.DataFrame(used_data) if used_data else pl.DataFrame()
        else:
            used_df = pl.DataFrame()

        # 声明但未使用的依赖
        if self.unused_declared:
            unused_data = []
            for coord in self.unused_declared:
                parts = coord.split(":")
                if len(parts) >= 3:
                    unused_data.append(
                        {
                            "coordinate": coord,
                            "group_id": parts[0],
                            "artifact_id": parts[1],
                            "version": parts[3] if len(parts) > 3 else parts[2],
                            "scope": parts[4] if len(parts) > 4 else "",
                            "issue_type": "unused_declared",
                        }
                    )
            unused_df = pl.DataFrame(unused_data) if unused_data else pl.DataFrame()
        else:
            unused_df = pl.DataFrame()

        return used_df, unused_df


class RedundancyCase(BaseModel):
    """冗余依赖案例

    表示一个冗余依赖的具体情况
    """

    declared_dependency: str  # 声明但未使用的依赖A
    actually_used: List[str] = Field(default_factory=list)  # 实际使用的传递依赖B列表
    dependency_path: List[str] = Field(default_factory=list)  # A到B的路径
    recommendation: str  # 优化建议

    @computed_field
    @property
    def severity(self) -> str:
        """问题严重程度

        Returns:
            'high' 如果有实际使用的传递依赖，否则 'medium'
        """
        return "high" if len(self.actually_used) > 0 else "medium"

    @computed_field
    @property
    def severity_level(self) -> int:
        """严重程度数值（用于排序）

        Returns:
            2: high, 1: medium
        """
        return 2 if self.severity == "high" else 1

    def to_dict(self) -> dict:
        """转换为字典格式

        Returns:
            包含所有字段的字典
        """
        return {
            "declared_dependency": self.declared_dependency,
            "actually_used": ", ".join(self.actually_used),
            "actually_used_count": len(self.actually_used),
            "dependency_path": " → ".join(self.dependency_path),
            "recommendation": self.recommendation,
            "severity": self.severity,
        }


class RedundancyAnalysisResult(BaseModel):
    """冗余依赖分析结果集

    包含所有检测到的冗余依赖案例
    """

    cases: List[RedundancyCase] = Field(default_factory=list)
    analysis_summary: str = ""

    @computed_field
    @property
    def total_redundancies(self) -> int:
        """冗余依赖总数"""
        return len(self.cases)

    @computed_field
    @property
    def high_severity_count(self) -> int:
        """高严重性问题数量"""
        return sum(1 for case in self.cases if case.severity == "high")

    @computed_field
    @property
    def medium_severity_count(self) -> int:
        """中等严重性问题数量"""
        return sum(1 for case in self.cases if case.severity == "medium")

    def to_polars_df(self) -> pl.DataFrame:
        """转换为 Polars DataFrame

        Returns:
            包含所有冗余依赖案例的 DataFrame
        """
        if not self.cases:
            return pl.DataFrame()

        data = [case.to_dict() for case in self.cases]
        return pl.DataFrame(data)

    def get_sorted_cases(self, by_severity: bool = True) -> List[RedundancyCase]:
        """获取排序后的案例列表

        Args:
            by_severity: 是否按严重程度排序

        Returns:
            排序后的 RedundancyCase 列表
        """
        if by_severity:
            return sorted(self.cases, key=lambda c: c.severity_level, reverse=True)
        return self.cases
