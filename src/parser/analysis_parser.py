"""Maven 依赖分析文本解析器"""

import re
from pathlib import Path

from ..models.analysis_result import AnalysisResult


class AnalysisParser:
    """依赖分析解析器

    解析 mvn dependency:analyze 命令的文本输出
    """

    # 正则表达式模式
    USED_UNDECLARED_PATTERN = r"Used undeclared dependencies found:"
    UNUSED_DECLARED_PATTERN = r"Unused declared dependencies found:"
    DEPENDENCY_LINE_PATTERN = r"\[WARNING\]\s+(.+:\w+:[^:]+:[^:]+:[^:]+)"
    PROJECT_PATTERN = r"-+<\s*(.+:.+)\s*>-+"

    def parse(self, file_path: str | Path) -> AnalysisResult:
        """解析依赖分析文本文件

        Args:
            file_path: 文本文件路径

        Returns:
            解析后的 AnalysisResult 对象

        Raises:
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_from_string(content)

    def parse_from_string(self, content: str) -> AnalysisResult:
        """从字符串解析依赖分析结果

        Args:
            content: 分析结果文本内容

        Returns:
            解析后的 AnalysisResult 对象
        """
        lines = content.split("\n")

        # 提取项目坐标
        project_coordinate = self._extract_project_coordinate(lines)

        # 提取依赖列表
        used_undeclared = self._extract_used_undeclared(lines)
        unused_declared = self._extract_unused_declared(lines)

        return AnalysisResult(
            project_coordinate=project_coordinate,
            used_undeclared=used_undeclared,
            unused_declared=unused_declared,
        )

    def _extract_project_coordinate(self, lines: list[str]) -> str:
        """提取项目坐标

        Args:
            lines: 文本行列表

        Returns:
            项目坐标，如果未找到返回 "unknown"
        """
        for line in lines:
            match = re.search(self.PROJECT_PATTERN, line)
            if match:
                return match.group(1)

        return "unknown"

    def _extract_used_undeclared(self, lines: list[str]) -> list[str]:
        """提取使用但未声明的依赖

        Args:
            lines: 文本行列表

        Returns:
            依赖坐标列表
        """
        dependencies = []
        in_section = False

        for line in lines:
            # 检查是否进入 "Used undeclared" 区域
            if re.search(self.USED_UNDECLARED_PATTERN, line):
                in_section = True
                continue

            # 检查是否离开当前区域
            if in_section and (
                re.search(self.UNUSED_DECLARED_PATTERN, line)
                or line.strip().startswith("[INFO]")
                and "---" in line
            ):
                break

            # 提取依赖坐标
            if in_section:
                match = re.search(self.DEPENDENCY_LINE_PATTERN, line)
                if match:
                    dependencies.append(match.group(1))

        return dependencies

    def _extract_unused_declared(self, lines: list[str]) -> list[str]:
        """提取声明但未使用的依赖

        Args:
            lines: 文本行列表

        Returns:
            依赖坐标列表
        """
        dependencies = []
        in_section = False

        for line in lines:
            # 检查是否进入 "Unused declared" 区域
            if re.search(self.UNUSED_DECLARED_PATTERN, line):
                in_section = True
                continue

            # 检查是否离开当前区域
            if in_section and (line.strip().startswith("[INFO]") and "---" in line):
                break

            # 提取依赖坐标
            if in_section:
                match = re.search(self.DEPENDENCY_LINE_PATTERN, line)
                if match:
                    dependencies.append(match.group(1))

        return dependencies


# 测试函数
# 测试 AnalysisParser
def test_analyze_deps():
    import json

    parser = AnalysisParser()
    with open("data/deps/example-dependency-tree.json", "r") as f:
        data = json.load(f)
    dependencies = parser._extract_used_undeclared(data["dependencies"])
    assert len(dependencies) == 2
    assert "org.apache.commons:commons-lang3:3.12.0" in dependencies
    assert "org.apache.commons:commons-text:1.10.0" in dependencies
