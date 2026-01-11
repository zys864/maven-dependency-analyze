# Maven依赖分析工具 - 前端架构详图

## 1. 整体架构

```mermaid
graph TB
    subgraph "用户交互层"
        UI1["FileUploader<br/>文件上传组件"]
        UI2["DependencyTree<br/>依赖树视图"]
        UI3["ChartView<br/>图表视图"]
        UI4["AnalysisReport<br/>分析报告"]
    end
    
    subgraph "React组件层"
        RC1["App Component<br/>主应用组件"]
        RC2["Context Provider<br/>状态提供者"]
        RC3["Custom Hooks<br/>自定义Hooks"]
    end
    
    subgraph "业务逻辑层"
        BL1["useDependencyParser<br/>依赖解析Hook"]
        BL2["useAnalysis<br/>分析Hook"]
        BL3["Algorithm Services<br/>算法服务"]
    end
    
    subgraph "数据处理层"
        DP1["JSON Parser<br/>JSON解析器"]
        DP2["TXT Parser<br/>TXT解析器"]
        DP3["Dependency Mapper<br/>依赖映射器"]
        DP4["Analysis Engine<br/>分析引擎"]
    end
    
    subgraph "工具层"
        UT1["Utility Functions<br/>工具函数"]
        UT2["Type Definitions<br/>类型定义"]
        UT3["Validation<br/>验证工具"]
    end
    
    subgraph "样式层"
        ST1["Tailwind CSS<br/>样式框架"]
        ST2["Component Styles<br/>组件样式"]
    end
    
    UI1 --> RC1
    UI2 --> RC1
    UI3 --> RC1
    UI4 --> RC1
    RC1 --> RC2
    RC1 --> RC3
    RC3 --> BL1
    RC3 --> BL2
    RC3 --> BL3
    BL1 --> DP1
    BL1 --> DP2
    BL2 --> DP3
    BL2 --> DP4
    DP1 --> UT1
    DP2 --> UT1
    DP3 --> UT2
    DP4 --> UT3
    UI1 --> ST1
    UI2 --> ST1
    UI3 --> ST2
    UI4 --> ST2
```

## 2. React组件层级结构

```mermaid
graph TD
    A["App<br/>- 状态管理<br/>- 路由管理"] --> B["FileUploadArea<br/>文件上传区域"]
    A --> C["MainLayout<br/>主布局组件"]
    C --> D["NavBar<br/>导航栏"]
    C --> E["ContentView<br/>内容视图"]
    E --> F["TreeViewTab<br/>树视图标签页"]
    E --> G["ChartViewTab<br/>图表视图标签页"]
    E --> H["AnalysisTab<br/>分析标签页"]
    F --> I["DependencyTree<br/>依赖树组件"]
    G --> J["DependencyChart<br/>依赖图表组件"]
    H --> K["AnalysisReport<br/>分析报告组件"]
    I --> L["TreeNode<br/>树节点组件"]
    J --> M["ChartNode<br/>图表节点组件"]
    K --> N["ReportSection<br/>报告分区组件"]
```

## 3. 数据流

### 3.1 文件上传流程
```mermaid
sequenceDiagram
    participant User as 用户
    participant FU as FileUploader
    participant DP as DependencyParser
    participant DC as DependencyContext
    participant RV as RenderView
    
    User->>FU: 上传JSON/TXT文件
    FU->>DP: 解析文件内容
    DP->>DC: 更新依赖数据
    DC->>RV: 触发视图重渲染
    RV->>User: 显示解析结果
```

### 3.2 依赖分析流程
```mermaid
sequenceDiagram
    participant UI as UI组件
    participant AH as Analysis Hook
    participant AE as Analysis Engine
    participant DS as Data Store
    
    UI->>AH: 请求分析依赖
    AH->>AE: 执行分析算法
    AE->>DS: 获取依赖数据
    AE->>AE: 执行分析逻辑
    AE->>AH: 返回分析结果
    AH->>UI: 更新UI状态
```

## 4. 状态管理

```mermaid
graph LR
    subgraph "Global State<br/>(Context API)"
        GS1["uploadedFiles<br/>上传的文件"]
        GS2["dependencyTree<br/>依赖树数据"]
        GS3["analysisResults<br/>分析结果"]
        GS4["uiState<br/>UI状态"]
    end
    
    subgraph "Local State<br/>(useState/useReducer)"
        LS1["expandedNodes<br/>展开的节点"]
        LS2["selectedNode<br/>选中的节点"]
        LS3["filterOptions<br/>过滤选项"]
        LS4["viewMode<br/>视图模式"]
    end
    
    GS1 -.-> LS1
    GS2 -.-> LS2
    GS3 -.-> LS3
    GS2 -.-> LS4
```

## 5. 核心Hook设计

### 5.1 useDependencyParser Hook
```typescript
interface UseDependencyParser {
  parseJsonFile: (file: File) => Promise<DependencyNode>;
  parseTxtFile: (file: File) => Promise<AnalysisReport>;
  isLoading: boolean;
  error: string | null;
}
```

### 5.2 useAnalysis Hook
```typescript
interface UseAnalysis {
  analyzeDependencies: (tree: DependencyNode, report: AnalysisReport) => AnalysisResult;
  findRedundantDeps: (result: AnalysisResult) => RedundancyReport[];
  detectConflicts: (result: AnalysisResult) => ConflictReport[];
  analysisResult: AnalysisResult | null;
}
```

## 6. 样式架构

采用Tailwind CSS + 自定义组件的方式：

```
styles/
├── globals.css          # 全局样式和Tailwind配置
├── components/          # 自定义组件样式
│   ├── tree.css         # 依赖树样式
│   ├── chart.css        # 图表样式
│   └── report.css       # 报告样式
└── utilities/           # 自定义工具类
    ├── colors.js        # 自定义颜色配置
    └── spacing.js       # 自定义间距配置
```

## 7. 性能优化策略

1. **虚拟滚动**: 对于大型依赖树，使用React Virtual等库实现虚拟滚动
2. **懒加载**: 按需加载组件和数据
3. **Memoization**: 使用React.memo、useMemo和useCallback优化渲染
4. **代码分割**: 使用React.lazy进行代码分割
5. **数据结构优化**: 使用高效的树遍历算法