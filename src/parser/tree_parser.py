"""Maven 依赖树 JSON 解析器"""

import json
from pathlib import Path
from typing import Optional, Dict
from ..models.dependency import Dependency, DependencyTree


class TreeParser:
    """依赖树解析器

    解析 Maven dependency:tree 命令生成的 JSON 文件
    """

    def parse(self, file_path: str | Path) -> DependencyTree:
        """解析依赖树 JSON 文件

        Args:
            file_path: JSON 文件路径

        Returns:
            解析后的 DependencyTree 对象

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: JSON 格式错误或数据不完整
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析错误: {e}")

        # 解析根节点
        root = self._parse_node(data, parent=None, depth=0)

        # 创建依赖树对象
        tree = DependencyTree(root=root)

        # 构建坐标索引
        tree.build_coordinate_index()

        return tree

    def _parse_node(
        self, node_dict: Dict, parent: Optional[Dependency], depth: int
    ) -> Dependency:
        """递归解析节点

        Args:
            node_dict: 节点的 JSON 字典
            parent: 父节点，根节点为 None
            depth: 当前节点的深度

        Returns:
            解析后的 Dependency 对象
        """
        # 提取节点信息
        group_id = node_dict.get("groupId", "")
        artifact_id = node_dict.get("artifactId", "")
        version = node_dict.get("version", "")
        scope = node_dict.get("scope", "")
        dep_type = node_dict.get("type", "jar")
        classifier = node_dict.get("classifier", "")
        optional = node_dict.get("optional", "false") == "true"

        # 创建当前节点
        node = Dependency(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
            scope=scope,
            type=dep_type,
            classifier=classifier,
            optional=optional,
            parent=parent,
            depth=depth,
        )

        # 递归解析子节点
        children_data = node_dict.get("children", [])
        for child_data in children_data:
            child = self._parse_node(child_data, parent=node, depth=depth + 1)
            node.children.append(child)

        return node

    def parse_from_string(self, json_str: str) -> DependencyTree:
        """从 JSON 字符串解析依赖树

        Args:
            json_str: JSON 字符串

        Returns:
            解析后的 DependencyTree 对象

        Raises:
            ValueError: JSON 格式错误
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析错误: {e}")

        root = self._parse_node(data, parent=None, depth=0)
        tree = DependencyTree(root=root)
        tree.build_coordinate_index()

        return tree
