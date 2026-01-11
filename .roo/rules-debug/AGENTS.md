# AGENTS.md - Debug Mode

This file provides guidance to agents when working with code in this repository.

## 项目调试规则（非显而易见）

### 构建调试
- 使用 `pnpm build` 执行完整构建，包含 TypeScript 编译（tsc -b）和 Vite 构建
- 构建失败时，先检查 TypeScript 编译错误，再检查 Vite 构建错误
- SWC 编译器错误可能不提供详细堆栈，需查看源文件定位问题

### 依赖解析调试
- 依赖树 JSON 解析遵循 Maven Dependency Plugin tree-mojo 规范
- 依赖分析 TXT 解析处理 `mvn dependency:analyze` 输出格式
- 解析失败时，检查文件格式是否符合预期，查看 src/utils/parser.ts 中的验证逻辑

### 状态管理调试
- 全局状态通过 React Context API 管理（src/contexts/DependencyContext.ts）
- 状态更新通过 Context 提供的方法，避免直接修改状态
- 使用 React DevTools Profiler 检查组件重渲染

### 样式调试
- Tailwind CSS 使用 @tailwindcss/vite 插件（非 PostCSS 方式）
- 样式不生效时，检查类名顺序：布局 → 尺寸 → 排版 → 颜色 → 状态
- 检查是否有重复的 Tailwind 类名组合未提取到 src/styles/components/

### 性能调试
- 大型依赖树使用虚拟滚动，检查是否正确配置
- 使用 React.memo、useMemo、useCallback 优化组件渲染
- 使用 Chrome DevTools Performance 分析渲染性能
