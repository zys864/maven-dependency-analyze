"""依赖树可视化器"""

from rich.tree import Tree as RichTree
from rich.console import Console
from rich.text import Text
from ..models.dependency import Dependency, DependencyTree


class TreeVisualizer:
    """依赖树可视化器

    使用 Rich 库在控制台展示美观的依赖树结构
    """

    def __init__(self, console: Console | None = None):
        """初始化

        Args:
            console: Rich Console 对象，如果为 None 则创建新的
        """
        self.console = console or Console()

    def print_tree(
        self,
        tree: DependencyTree,
        show_scope: bool = True,
        max_depth: int | None = None,
        filter_scope: str | None = None,
        highlight_coordinates: list[str] | None = None,
    ):
        """打印依赖树

        Args:
            tree: 要显示的依赖树
            show_scope: 是否显示 scope 信息
            max_depth: 最大显示深度，None 表示无限制
            filter_scope: 只显示特定 scope 的依赖，None 表示显示全部
            highlight_coordinates: 需要高亮的依赖坐标列表
        """
        root_node = tree.root

        # 创建根节点标签
        root_label = self._create_node_label(
            root_node, show_scope=False, highlight=False
        )

        # 创建 Rich Tree
        rich_tree = RichTree(root_label)

        # 递归添加子节点
        for child in root_node.children:
            if self._should_include_node(child, filter_scope, max_depth):
                self._add_node_to_tree(
                    rich_tree,
                    child,
                    show_scope=show_scope,
                    max_depth=max_depth,
                    filter_scope=filter_scope,
                    highlight_coordinates=highlight_coordinates or [],
                )

        # 打印树
        self.console.print(rich_tree)

    def _add_node_to_tree(
        self,
        parent_tree: RichTree,
        node: Dependency,
        show_scope: bool,
        max_depth: int | None,
        filter_scope: str | None,
        highlight_coordinates: list[str],
    ):
        """递归添加节点到 Rich Tree

        Args:
            parent_tree: 父节点的 Rich Tree 对象
            node: 当前依赖节点
            show_scope: 是否显示 scope
            max_depth: 最大深度
            filter_scope: 过滤 scope
            highlight_coordinates: 高亮坐标列表
        """
        # 检查是否需要高亮
        is_highlighted = node.simple_coordinate in highlight_coordinates

        # 创建节点标签
        node_label = self._create_node_label(node, show_scope, is_highlighted)

        # 添加到父树
        child_tree = parent_tree.add(node_label)

        # 递归添加子节点
        if max_depth is None or node.depth < max_depth:
            for child in node.children:
                if self._should_include_node(child, filter_scope, max_depth):
                    self._add_node_to_tree(
                        child_tree,
                        child,
                        show_scope,
                        max_depth,
                        filter_scope,
                        highlight_coordinates,
                    )

    def _create_node_label(
        self, node: Dependency, show_scope: bool, highlight: bool
    ) -> Text:
        """创建节点标签

        Args:
            node: 依赖节点
            show_scope: 是否显示 scope
            highlight: 是否高亮显示

        Returns:
            Rich Text 对象
        """
        # 构建基础文本
        label_parts = [f"{node.group_id}:{node.artifact_id}:{node.version}"]

        if show_scope and node.scope:
            label_parts.append(f"[{node.scope}]")

        label_text = " ".join(label_parts)

        # 创建 Text 对象并应用样式
        text = Text(label_text)

        if highlight:
            text.stylize("bold yellow on red")
        elif node.optional:
            text.stylize("dim italic")
        elif node.scope == "test":
            text.stylize("cyan")
        elif node.scope == "provided":
            text.stylize("magenta")
        elif node.scope == "compile" or not node.scope:
            text.stylize("green")
        else:
            text.stylize("white")

        return text

    def _should_include_node(
        self, node: Dependency, filter_scope: str | None, max_depth: int | None
    ) -> bool:
        """判断节点是否应该包含在输出中

        Args:
            node: 依赖节点
            filter_scope: 过滤 scope
            max_depth: 最大深度

        Returns:
            True 如果应该包含，否则 False
        """
        # 检查深度限制
        if max_depth is not None and node.depth > max_depth:
            return False

        # 检查 scope 过滤
        if filter_scope is not None and node.scope != filter_scope:
            return False

        return True

    def print_statistics(self, tree: DependencyTree):
        """打印依赖树统计信息

        Args:
            tree: 依赖树
        """
        from rich.table import Table

        table = Table(title="依赖树统计信息", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan", justify="left")
        table.add_column("数值", style="green", justify="right")

        # 添加统计数据
        table.add_row("总依赖数", str(tree.total_dependencies))
        table.add_row("直接依赖数", str(len(tree.direct_dependencies)))
        table.add_row("最大深度", str(tree.max_depth))

        # 按 scope 统计
        df = tree.to_polars_df()
        scope_counts = df.group_by("scope").agg({"coordinate": "count"})

        table.add_section()
        table.add_row("[bold]Scope 分布[/bold]", "")

        for row in scope_counts.iter_rows(named=True):
            scope = row["scope"] if row["scope"] else "compile"
            count = row["coordinate"]
            table.add_row(f"  {scope}", str(count))

        self.console.print(table)
