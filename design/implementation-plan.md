# 项目实现方案

## 问题陈述

当前项目是一个空白的Python工具，需要实现Maven依赖树的解析、分析和可视化功能。主要目标是帮助Java项目识别冗余依赖、未声明的使用依赖和未使用的声明依赖。

## 当前状态

- 项目使用Python 3.13 + uv包管理器
- 只有一个空白的main.py入口文件
- 已有示例数据文件：
  - `data/deps/example-dependency-tree.json` - 包含完整的Maven依赖树结构
  - `data/deps-analysis/example-deps-analysis.txt` - 包含Maven依赖使用情况分析
- 无任何依赖包配置

## 方案设计

### 0. 技术栈选型

**核心库：**

- **Pydantic**: 用于数据模型定义和验证，提供类型安全和自动验证
- **Polars**: 用于数据分析和Excel导出，比Pandas更快且API更现代
- **Click**: CLI框架，比argparse更优雅
- **Rich**: 终端美化输出，提供丰富的格式化和进度条

**优势：**

- Pydantic的数据类提供自动验证和序列化
- Polars的DataFrame非常适合处理依赖数据的统计和导出
- Rich可以美化树形结构和表格输出

### 1. 项目架构设计

采用分层架构，将功能模块化：

```
maven-dependency-analyze/
├── main.py                      # CLI入口
├── src/
│   ├── __init__.py
│   ├── parser/                  # 解析模块
│   │   ├── __init__.py
│   │   ├── tree_parser.py       # 依赖树JSON解析器
│   │   └── analysis_parser.py   # 依赖分析文本解析器
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── dependency.py        # 依赖节点数据类
│   │   └── analysis_result.py   # 分析结果数据类
│   ├── analyzer/                # 分析模块
│   │   ├── __init__.py
│   │   ├── tree_analyzer.py     # 依赖树分析
│   │   └── redundancy_analyzer.py # 冗余依赖检测
│   ├── exporter/                # 导出模块
│   │   ├── __init__.py
│   │   ├── excel_exporter.py    # Excel导出
│   │   └── tree_visualizer.py   # 树形可视化
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py        # 文件处理工具
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_analyzer.py
│   └── test_exporter.py
└── output/                      # 输出目录
```

### 2. 核心数据模型（使用Pydantic）

#### 2.1 Dependency类 (Pydantic BaseModel)

```python
from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Set

class Dependency(BaseModel):
    group_id: str
    artifact_id: str
    version: str
    scope: str = ""  # compile/test/runtime等
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
    
    def get_all_descendants(self) -> Set['Dependency']:
        """递归获取所有传递依赖（扁平化）"""
        descendants = set()
        for child in self.children:
            descendants.add(child)
            descendants.update(child.get_all_descendants())
        return descendants
    
    def find_path_to(self, target_coordinate: str) -> Optional[List['Dependency']]:
        """查找到某个依赖的路径"""
        if self.coordinate == target_coordinate:
            return [self]
        for child in self.children:
            path = child.find_path_to(target_coordinate)
            if path:
                return [self] + path
        return None
```

#### 2.2 DependencyTree类 (Pydantic BaseModel)

```python
class DependencyTree(BaseModel):
    root: Dependency
    all_dependencies: dict[str, List[Dependency]] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}
    
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
    
    def to_polars_df(self) -> pl.DataFrame:
        """转换为Polars DataFrame用于分析"""
        flattened = self.flatten()
        data = {
            "group_id": [d.group_id for d in flattened],
            "artifact_id": [d.artifact_id for d in flattened],
            "version": [d.version for d in flattened],
            "scope": [d.scope for d in flattened],
            "type": [d.type for d in flattened],
            "depth": [d.depth for d in flattened],
            "coordinate": [d.coordinate for d in flattened],
        }
        return pl.DataFrame(data)
```

#### 2.3 AnalysisResult类 (Pydantic BaseModel)

```python
class AnalysisResult(BaseModel):
    project_coordinate: str
    used_undeclared: List[str] = Field(default_factory=list)
    unused_declared: List[str] = Field(default_factory=list)
    
    def to_polars_df(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """转换为两个DataFrame"""
        used_df = pl.DataFrame({"coordinate": self.used_undeclared, "issue_type": ["used_undeclared"] * len(self.used_undeclared)})
        unused_df = pl.DataFrame({"coordinate": self.unused_declared, "issue_type": ["unused_declared"] * len(self.unused_declared)})
        return used_df, unused_df
```

#### 2.4 RedundancyCase类 (Pydantic BaseModel)

```python
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
```

### 3. 解析器实现

#### 3.1 TreeParser (tree_parser.py)

功能：解析dependency-tree.json

关键方法：

- `parse(file_path: str) -> DependencyTree`
- `_parse_node(node_dict: dict, parent: Optional[Dependency], depth: int) -> Dependency`

实现逻辑：

1. 递归解析JSON结构
2. 构建Dependency对象树
3. 维护parent引用和depth信息
4. 构建coordinate索引字典

#### 3.2 AnalysisParser (analysis_parser.py)

功能：解析mvn dependency:analyze输出文本

关键方法：

- `parse(file_path: str) -> AnalysisResult`

实现逻辑：

1. 读取文本文件
2. 使用正则表达式查找"Used undeclared dependencies found:"和"Unused declared dependencies found:"标记
3. 提取依赖坐标（格式：groupId:artifactId:type:version:scope）
4. 解析到AnalysisResult对象

### 4. 分析器实现

#### 4.1 TreeAnalyzer (tree_analyzer.py)

功能：依赖树统计和分析（利用Polars进行高效分析）

关键方法：

- `get_statistics(tree: DependencyTree) -> Dict`：统计信息（总依赖数、直接依赖数、传递依赖数、各scope分布）
  - 使用tree.to_polars_df()转换为DataFrame
  - 使用Polars的group_by和agg进行统计
- `get_dependency_paths(tree: DependencyTree, target: str) -> List[List[Dependency]]`：查找依赖引入路径
- `group_by_depth(tree: DependencyTree) -> pl.DataFrame`：按深度分组，返回Polars DataFrame

#### 4.2 RedundancyAnalyzer (redundancy_analyzer.py)

功能：冗余依赖检测（核心功能）

关键方法：

- `analyze(tree: DependencyTree, analysis: AnalysisResult) -> List[RedundancyCase]`

检测逻辑：

1. 对于每个"unused declared"依赖A：
   - 在依赖树中找到A的所有出现位置
   - 如果A是直接依赖（depth=1），检查其所有子依赖
   - 对于A的每个子依赖B，检查B是否在"used undeclared"列表中
   - 如果存在这样的B，标记为冗余情况："声明了A但只使用了其传递依赖B"
2. 输出RedundancyCase对象，包含：
   - declared_dependency: str (依赖A)
   - actually_used: List[str] (实际使用的传递依赖B列表)
   - recommendation: str (建议：移除A，直接声明B)

### 5. 导出器实现

#### 5.1 ExcelExporter (excel_exporter.py)

使用Polars的write_excel()方法实现Excel导出（底层使用xlsxwriter）

导出内容分多个Sheet：

**Sheet 1: 项目概览**

- 项目坐标
- 统计信息（总依赖数、直接依赖数等）

**Sheet 2: 完整依赖树**

列：深度 | GroupId | ArtifactId | Version | Scope | 类型 | 引入路径

使用缩进展示层级关系

**Sheet 3: 使用但未声明依赖**

列：GroupId | ArtifactId | Version | Scope | 引入路径 | 建议

**Sheet 4: 声明但未使用依赖**

列：GroupId | ArtifactId | Version | Scope | 建议

**Sheet 5: 冗余依赖分析**

列：声明的依赖 | 实际使用的传递依赖 | 优化建议

格式优化：

- 标题行加粗、背景色
- 自动列宽
- 冻结首行
- 使用条件格式标记问题依赖（红色/黄色）

#### 5.2 TreeVisualizer (tree_visualizer.py)

控制台树形可视化输出（使用Rich库）

关键方法：

- `print_tree(tree: DependencyTree, show_scope: bool = True)`

使用Rich的Tree组件绘制美观的树形结构：

```python
from rich.tree import Tree
from rich.console import Console

# Rich会自动提供漂亮的Unicode树形字符和颜色
tree = Tree("[bold blue]com.example:demo:0.0.1-SNAPSHOT[/bold blue]")
webmvc = tree.add("org.springframework.boot:spring-boot-starter-webmvc:4.0.1 [yellow][compile][/yellow]")
starter = webmvc.add("org.springframework.boot:spring-boot-starter:4.0.1 [yellow][compile][/yellow]")
starter.add("org.yaml:snakeyaml:2.5 [yellow][compile][/yellow]")
# ...
console = Console()
console.print(tree)
```

提供可选参数：

- max_depth: 限制显示深度
- filter_scope: 只显示特定scope
- highlight_coordinates: 高亮特定依赖

### 6. CLI入口设计 (main.py)

使用Click库实现命令行接口

命令结构：

```bash
# 基础分析
python main.py analyze --tree data/deps/dep-tree.json --analysis data/deps-analysis/analysis.txt

# 输出Excel
python main.py analyze --tree <tree-file> --analysis <analysis-file> --output output/report.xlsx

# 只看树形结构
python main.py show-tree --tree <tree-file> --max-depth 3

# 只检测冗余依赖
python main.py check-redundancy --tree <tree-file> --analysis <analysis-file>
```

参数：

- `--tree`: 依赖树JSON文件路径
- `--analysis`: 依赖分析文本文件路径
- `--output`: 输出文件路径（可选，默认output/report.xlsx）
- `--format`: 输出格式（excel/console/json）
- `--max-depth`: 树形显示最大深度
- `--verbose`: 详细输出模式

### 7. 依赖包需求

在pyproject.toml中添加：

```toml
dependencies = [
    "pydantic>=2.10.0",     # 数据模型和验证
    "polars>=1.20.0",       # 数据分析和处理
    "xlsxwriter>=3.2.0",    # Excel导出（Polars依赖）
    "click>=8.1.0",         # CLI框架
    "rich>=13.0.0",         # 终端美化输出
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",          # 代码检查和格式化
    "mypy>=1.8.0",          # 类型检查
]
```

### 8. 实现优先级

**Phase 1 (MVP核心功能)：**

1. 数据模型定义 (models/) - 使用Pydantic定义所有数据类
2. 依赖树解析器 (parser/tree_parser.py) - 解析JSON并构建Pydantic模型
3. 依赖分析解析器 (parser/analysis_parser.py) - 解析文本并构建AnalysisResult
4. 基础树形可视化 (exporter/tree_visualizer.py) - 使用Rich.Tree实现
5. 简单CLI入口 - 使用Click实现

**Phase 2 (分析功能)：**

6. 树分析器 (analyzer/tree_analyzer.py) - 使用Polars进行统计分析
7. 冗余依赖检测器 (analyzer/redundancy_analyzer.py) - 核心分析逻辑
8. 增强CLI功能 - 添加更多命令和选项

**Phase 3 (导出和美化)：**

9. Excel导出器 (exporter/excel_exporter.py) - 使用Polars的write_excel
10. Rich表格输出 - 使用Rich.Table展示统计数据
11. 完善错误处理和日志 - 使用Rich的日志功能

## 需要确认的问题

### Q1: Excel导出格式偏好

是否需要在Excel中包含图表（如依赖分布饼图、深度柱状图）？

### Q2: 冗余依赖检测逻辑确认

当前理解：如果声明了依赖A但未使用A本身，只使用了A的传递依赖B，则认为A是冗余的，应该直接声明B。

是否还需要检测其他类型的冗余？例如：

- 多个依赖引入了同一个传递依赖的不同版本（版本冲突）
- 某个依赖在多处以不同scope引入

### Q3: 可视化方式

除了Excel和控制台输出，是否需要生成图形化的可视化（如HTML文件、GraphViz图）？

### Q4: 批量处理

是否需要支持批量处理多个项目（如扫描某个目录下所有Java项目）？

### Q5: 配置文件

是否需要支持配置文件（如忽略某些依赖、自定义规则等）？
