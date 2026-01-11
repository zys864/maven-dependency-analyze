# AGENTS.md - Ask Mode

This file provides guidance to agents when working with code in this repository.

## 项目文档规则（非显而易见）

### 项目概述
- Maven 依赖分析工具的前端应用，用于可视化分析和管理 Java Maven 项目的依赖关系
- 核心功能：依赖树可视化、依赖使用情况分析、冗余依赖检测
- 输入：Maven 依赖树 JSON 文件 + 依赖分析 TXT 文件

### 架构文档位置
- 设计文档位于 `design/` 目录，包含：
  - design-document.md：项目概述、数据格式、组件设计、核心算法
  - development-standard.md：路由规范、Tailwind CSS 规范、代码组织
  - frontend-architecture.md：React 组件层级、数据流、状态管理
  - system-architecture.md：系统整体架构、数据流向、模块交互

### 目录结构说明
- `src/components/` - React 组件（按功能模块分组，目前大部分为空）
- `src/hooks/` - 自定义 React Hooks（如 useDependencyParser、useAnalysis）
- `src/types/` - TypeScript 类型定义（DependencyNode、AnalysisResult）
- `src/utils/` - 工具函数和解析器（parser.ts、algorithms.ts）
- `src/contexts/` - React Contexts（DependencyContext.ts）
- `src/styles/` - 样式文件（components/ 和 utilities/）

### 示例数据
- `example/example-dependency-tree.json` - Maven 依赖树示例
- `example/example-deps-analysis.txt` - 依赖分析输出示例

### 关键概念
- DependencyNode 接口：usageStatus 字段（'used' | 'unused' | 'undeclared'）
- AnalysisResult 接口：包含 dependencyTree、usedUndeclaredDeps、unusedDeclaredDeps
- 数据流：用户上传文件 → 前端解析器 → 依赖关系处理器 → 状态管理 → React UI 组件
