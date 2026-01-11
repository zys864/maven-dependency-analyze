# AGENTS.md - Code Mode

This file provides guidance to agents when working with code in this repository.

## 项目编码规则（非显而易见）

### 组件开发
- 组件文件使用 PascalCase 命名（如 DependencyTree.tsx），文件夹使用 kebab-case（如 dependency-tree/）
- 每个组件目录应包含 index.ts 作为导出入口
- 公共样式必须使用 @apply 指令提取到 src/styles/components/，禁止在多个组件中重复相同的 Tailwind 类名组合

### 依赖解析器
- 依赖树 JSON 解析器位于 src/utils/parser.ts，遵循 Maven Dependency Plugin tree-mojo 规范
- 依赖分析 TXT 解析器处理 `mvn dependency:analyze` 命令输出格式
- 解析器必须返回符合 DependencyNode 接口的数据结构

### 状态管理
- 使用 React Context API 管理全局状态（src/contexts/DependencyContext.ts）
- 自定义 hooks 位于 src/hooks/，如 useDependencyParser 和 useAnalysis
- 避免在组件中直接修改全局状态，通过 Context 提供的方法更新

### 数据模型
- 核心类型定义在 src/types/index.ts
- DependencyNode 接口包含 usageStatus 字段：'used' | 'unused' | 'undeclared'
- AnalysisResult 接口包含 dependencyTree、usedUndeclaredDeps、unusedDeclaredDeps 等字段

### 样式规范
- Tailwind CSS 类名按顺序组织：布局 → 尺寸 → 排版 → 颜色 → 状态
- 使用 @tailwindcss/vite 插件（非 PostCSS 方式）
- 公共组件样式提取到 src/styles/components/，工具类提取到 src/styles/utilities/

### 性能优化
- 大型依赖树使用虚拟滚动（React Virtual）
- 使用 React.memo、useMemo、useCallback 优化组件渲染
- 使用 React.lazy 进行路由级代码分割
