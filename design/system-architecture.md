# Maven依赖分析工具 - 系统架构详图

## 1. 整体架构

```mermaid
graph TB
    subgraph "输入层"
        A1["deps/*.json<br/>依赖树JSON文件"]
        A2["deps-analysis/*.txt<br/>依赖分析文本文件"]
    end
    
    subgraph "解析层"
        P1["DependencyParser<br/>JSON解析器"]
        P2["AnalysisParser<br/>文本分析解析器"]
    end
    
    subgraph "数据模型层"
        DM1["DependencyTree<br/>依赖树数据模型"]
        DM2["UsageAnalysis<br/>使用分析数据模型"]
    end
    
    subgraph "分析引擎层"
        AE1["DependencyAnalyzer<br/>依赖分析器"]
        AE2["RedundancyDetector<br/>冗余检测器"]
        AE3["RelationshipProcessor<br/>关系处理器"]
    end
    
    subgraph "输出层"
        O1["TreeExporter<br/>树状结构导出"]
        O2["Visualizer<br/>可视化组件"]
        O3["ExcelExporter<br/>Excel导出"]
        O4["RedundancyReporter<br/>冗余报告生成"]
    end
    
    subgraph "应用接口层"
        API1["CLI Interface<br/>命令行接口"]
        API2["API Service<br/>API服务接口"]
    end
    
    A1 --> P1
    A2 --> P2
    P1 --> DM1
    P2 --> DM2
    DM1 --> AE3
    DM2 --> AE3
    AE3 --> AE1
    AE1 --> AE2
    AE2 --> DM1
    AE1 --> O1
    AE1 --> O2
    AE1 --> O3
    AE2 --> O4
    O1 --> API1
    O2 --> API1
    O3 --> API1
    O4 --> API1
    API1 --> API2
```

## 2. 数据流向说明

### 2.1 解析阶段
1. DependencyParser读取deps目录下的JSON文件，将其转换为DependencyTree数据结构
2. AnalysisParser读取deps-analysis目录下的文本文件，提取使用情况信息

### 2.2 分析阶段
1. RelationshipProcessor整合DependencyTree和UsageAnalysis数据
2. DependencyAnalyzer执行基本分析，标记依赖的使用状态
3. RedundancyDetector检测冗余依赖并生成报告

### 2.3 输出阶段
1. TreeExporter生成树状结构输出
2. Visualizer生成可视化数据
3. ExcelExporter导出Excel格式
4. RedundancyReporter生成冗余依赖报告

## 3. 模块交互

```mermaid
sequenceDiagram
    participant Input as 输入数据
    participant Parser as 解析器
    participant Model as 数据模型
    participant Analyzer as 分析引擎
    participant Output as 输出模块
    participant User as 用户

    Input->>Parser: 提供JSON和TXT文件
    Parser->>Model: 构建依赖树和分析数据
    Model->>Analyzer: 传输数据进行分析
    Analyzer->>Model: 更新分析结果
    Model->>Output: 提供完整分析结果
    Output->>User: 输出各类报告
```

## 4. 核心组件职责

### 4.1 解析器组件
- **DependencyParser**: 将Maven生成的JSON依赖树转换为内部数据结构
- **AnalysisParser**: 解析dependency:analyze命令输出的文本，提取使用情况

### 4.2 分析器组件
- **DependencyAnalyzer**: 对比依赖声明与实际使用情况
- **RedundancyDetector**: 检测间接依赖使用模式和冗余依赖
- **RelationshipProcessor**: 整合多源数据，建立依赖关系映射

### 4.3 输出组件
- **TreeExporter**: 生成层次化的依赖树视图
- **Visualizer**: 创建依赖关系图用于可视化展示
- **ExcelExporter**: 将分析结果导出为Excel格式
- **RedundancyReporter**: 生成详细的冗余依赖分析报告