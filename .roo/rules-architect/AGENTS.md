# AGENTS.md - Architect Mode

This file provides guidance to agents when working with code in this repository.

## 项目架构规则（非显而易见）

### 核心数据流
用户上传 JSON/TXT 文件 → 前端解析器 → 依赖关系处理器 → 状态管理 → React UI 组件

### 输入数据格式
- 依赖树 JSON：遵循 Maven Dependency Plugin tree-mojo 规范
  - 根节点包含 groupId、artifactId、version、type、scope、classifier、optional、children
  - 依赖项通过 children 数组递归表示
- 依赖分析 TXT：处理 `mvn dependency:analyze` 命令输出
  - "Used undeclared dependencies found:" 后面的数据
  - "Unused declared dependencies found:" 后面的数据

### 状态管理架构
- 使用 React Context API 管理全局状态（src/contexts/DependencyContext.ts）
- 自定义 hooks 处理业务逻辑（src/hooks/）
  - useDependencyParser：解析 JSON/TXT 文件
  - useAnalysis：执行依赖分析、冗余检测、冲突检测
- 避免在组件中直接修改全局状态，通过 Context 提供的方法更新

### 组件架构
- 按功能模块分组（src/components/）
  - FileUploader：文件上传组件
  - DependencyTree：依赖树视图组件
  - ChartView：图表视图组件
  - AnalysisReport：分析报告组件
  - common：通用组件
- 每个组件目录应包含 index.ts 作为导出入口

### 样式架构
- Tailwind CSS 类名按顺序组织：布局 → 尺寸 → 排版 → 颜色 → 状态
- 公共样式使用 @apply 指令提取到 src/styles/components/
- 工具类提取到 src/styles/utilities/
- 严格避免在不同组件中重复相同的 Tailwind 类名组合

### 性能优化策略
- 大型依赖树使用虚拟滚动（React Virtual）
- 使用 React.memo、useMemo、useCallback 优化组件渲染
- 使用 React.lazy 进行路由级代码分割

### 技术栈
- React 19.2.0 + TypeScript 5.9.3
- Vite 7.2.4 + SWC 编译器
- Tailwind CSS 4.1.18（使用 @tailwindcss/vite 插件）
- pnpm 包管理器
