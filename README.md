# java 仓库maven依赖树解析

## 数据来源
java仓库`mvn dependency:tree -DoutputType=json -DoutputFile=dependency-tree.json`命令导出得到

## 数据格式
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
