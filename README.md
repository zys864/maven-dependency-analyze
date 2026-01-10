# java 仓库maven依赖树解析

## 数据来源
- `data/deps` maven项目的依赖树, java仓库`mvn dependency:tree -DoutputType=json -DoutputFile=dependency-tree.json`命令导出得到
- `data/deps-analysis` maven项目的依赖使用情况分析结果, java仓库`mvn dependency:analyze`命令导出得到
## `依赖树`数据格式
> 参考`https://maven.apache.org/components/plugins/maven-dependency-plugin/examples/tree-mojo.html`
### Description: 
The JSON format represents the dependency tree as a hierarchical JSON object. The root node describes the project's artifact, and its dependencies are listed in a children array, with nested dependencies recursively included.

### Structure:

#### Root Node:
- groupId: The group ID of the project or dependency (e.g., org.apache.maven.extensions).
- artifactId: The artifact ID (e.g., maven-build-cache-extension).
- version: The version (e.g., 1.2.1-SNAPSHOT).
- type: The artifact type (e.g., jar).
- scope: The dependency scope (e.g., compile, test, or empty for the project itself).
- classifier: The classifier, if any (e.g., empty string if none).
- optional: Whether the dependency is optional (true or false).
- children: An array of dependency objects with the same structure, representing transitive dependencies.
#### Nested Dependencies: 
Each dependency in the children array follows the same structure, allowing for recursive representation of the dependency tree.

## `依赖使用情况分析`数据格式
- `Used undeclared dependencies found:`后面到数据树是 `未显示声明且使用的依赖`
- `Unused declared dependencies found:`后面到数据树是 `显示声明但未使用的依赖`

## `依赖树`分析功能
- 依赖树解析：将依赖树解析为树状结构，方便查看和分析。
- 依赖树可视化：将依赖树可视化为图形，方便查看和分析。
- 依赖树导出：将依赖树导出为Excel文件（格式优化后），方便查看和分析。

## `依赖使用情况分析`功能
- 依赖使用情况分析：将依赖使用情况分析为树状结构，方便查看和分析。
- 依赖使用情况可视化：将依赖使用情况可视化为图形，方便查看和分析。
- 依赖使用情况导出：将依赖使用情况导出为Excel文件（格式优化后），方便查看和分析。

## 冗余/多余依赖分析
根据`依赖树`分析功能和`依赖使用情况分析`功能的数据分析不需要引入的依赖
- 引入包A，只为了使用包A的子依赖B的类，为使用包A的任何功能/类，这种情况需要直接使用B，而不是引入A去使用B
- 冗余依赖分析：将冗余依赖分析为树状结构，方便查看和分析。
- 冗余依赖可视化：将冗余依赖可视化为图形，方便查看和分析。
- 冗余依赖导出：将冗余依赖导出为Excel文件（格式优化后），方便查看和分析。
