# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## 项目概述
Maven 依赖分析工具的前端应用，用于可视化分析和管理 Java Maven 项目的依赖关系。

## 构建与运行
- `pnpm dev` - 启动开发服务器
- `pnpm build` - 构建生产版本（执行 tsc -b && vite build）
- `pnpm lint` - ESLint 代码检查
- `pnpm preview` - 预览生产构建

## 代码风格规范

### Tailwind CSS 类名组织顺序
1. 布局类（flex, grid, container）
2. 尺寸类（w-, h-, min-/max-）
3. 排版类（font-, text-, leading-, tracking-）
4. 颜色类（bg-, text-, border-）
5. 状态类（hover:, focus:, active:）

### 命名约定
- 组件文件：PascalCase（如 DependencyTree.tsx）
- 文件夹：kebab-case（如 dependency-tree/）
- 公共样式使用 @apply 指令提取到 src/styles/components/

### 严格避免样式重复
任何在多个地方使用的样式组合都必须提取为公共组件或工具类，禁止在不同组件中重复相同的 Tailwind 类名组合。

## 项目架构

### 核心数据流
用户上传 JSON/TXT 文件 → 前端解析器 → 依赖关系处理器 → 状态管理 → React UI 组件

### 输入数据格式
- 依赖树 JSON：Maven Dependency Plugin tree-mojo 规范
- 依赖分析 TXT：`mvn dependency:analyze` 命令输出

### 状态管理
使用 React Context API 管理全局状态，自定义 hooks 处理业务逻辑

### 目录结构
- `src/components/` - React 组件（按功能模块分组）
- `src/hooks/` - 自定义 React Hooks
- `src/types/` - TypeScript 类型定义
- `src/utils/` - 工具函数和解析器
- `src/contexts/` - React Contexts
- `src/styles/` - 样式文件（components/ 和 utilities/）

## 技术栈
- React 19.2.0 + TypeScript 5.9.3
- Vite 7.2.4 + SWC 编译器
- Tailwind CSS 4.1.18（使用 @tailwindcss/vite 插件）
- pnpm 包管理器

## 注意事项
- 项目目前处于早期阶段，大部分组件目录为空
- 设计文档位于 `design/` 目录，包含详细的架构和规范说明
- 示例数据位于 `example/` 目录
