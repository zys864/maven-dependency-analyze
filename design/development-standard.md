# 前端开发规范标准文档

## 目录
1. [路由规范](#路由规范)
2. [Tailwind CSS 规范](#tailwind-css-规范)
3. [UI 组件库使用规范](#ui-组件库使用规范)
4. [代码组织与架构](#代码组织与架构)
5. [最佳实践](#最佳实践)

## 路由规范

### React Router 使用规范

- **统一使用 React Router v6+**
  - 所有项目必须使用最新稳定版本的 React Router
  - 使用 `<BrowserRouter>` 作为根路由组件
  - 使用 `<Routes>` 和 `<Route>` 进行路由配置

- **路由文件组织**
  ```jsx
  // routes/index.jsx
  import { BrowserRouter, Routes, Route } from 'react-router-dom';
  import Home from '../pages/Home';
  import About from '../pages/About';
  
  const AppRoutes = () => (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
  
  export default AppRoutes;
  ```

- **嵌套路由结构**
  - 对于复杂的嵌套结构，使用 Outlet 组件
  - 按功能模块划分路由文件

- **路由守卫**
  - 实现统一的认证和权限检查中间件
  - 使用自定义 hooks 处理路由守卫逻辑

## Tailwind CSS 规范

### 类名组织原则

**类名按逻辑分组，推荐顺序：**

1. **布局类** - 控制元素的整体布局（flex, grid, container, etc.）
2. **尺寸类** - 控制元素的宽高（w-, h-, min-/max-）
3. **排版类** - 控制文本样式（font-, text-, leading-, tracking-）
4. **颜色类** - 控制颜色相关（bg-, text-, border-）
5. **状态类** - 控制交互状态（hover:, focus:, active:）

```html
<!-- 推荐写法 -->
<button class="flex items-center justify-center w-full max-w-xs h-12 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200">
  Submit Button
</button>

<!-- 不推荐写法 -->
<button class="text-white bg-blue-600 focus:ring-offset-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200 w-full max-w-xs h-12 px-6 py-3 flex items-center justify-center font-medium rounded-lg">
  Submit Button
</button>
```

### 公共样式处理

- **提取公共组件**
  - 任何在多个地方使用的样式组合都应该提取为公共组件
  - 创建可重用的 UI 组件，如按钮、卡片、表单元素等
  - 使用 `@apply` 指令创建可重用的样式类

- **管理重复和创建可复用抽象**
  ```css
  /* 在自定义 CSS 文件中 */
  @layer components {
    .btn-primary {
      @apply inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200;
    }
    
    .card {
      @apply rounded-lg border border-gray-200 bg-white p-6 shadow-sm;
    }
  }
  ```

- **避免样式重复**
  - 严格禁止在不同页面或组件中重复相同的 Tailwind 类名组合
  - 使用工具检查和识别重复的样式模式
  - 定期重构重复的样式为可复用组件

### 样式提取策略

- **能复用的样式一定要抽离**
  - 否则 Tailwind 使用成本会随页面增长线性上升
  - 创建原子化的工具类组件
  - 使用组合而非重复来构建界面

## UI 组件库使用规范

### Shadcn UI 使用规范

- **安装和配置**
  - 使用官方推荐的安装方式
  - 确保 Tailwind CSS 正确配置为 PostCSS 插件
  - 配置主题以匹配项目设计系统

- **组件使用原则**
  - 优先使用 Shadcn 提供的组件，保持一致的用户体验
  - 只有在 Shadcn 无法满足需求时才自定义组件
  - 自定义组件应遵循 Shadcn 的设计模式和 API 设计

- **定制化规范**
  - 通过修改配置文件进行全局定制
  - 避免直接修改组件源码
  - 保持组件的可升级性

### Tailwind CSS 安装

- **使用 PostCSS 插件安装**
  - 按照官方文档使用 PostCSS 插件方式安装
  - 确保与现有构建流程兼容
  - 配置正确的配置文件

## 代码组织与架构

### 组件结构

- **文件组织**
  ```
  src/
  ├── components/     # 可复用 UI 组件
  ├── pages/         # 页面级组件
  ├── hooks/         # 自定义 hooks
  ├── utils/         # 工具函数
  ├── services/      # API 服务
  ├── styles/        # 全局样式
  └── routes/        # 路由配置
  ```

- **组件命名规范**
  - 使用 PascalCase 命名组件
  - 使用 kebab-case 命名文件夹和文件
  - 保持组件名称语义化

### 依赖管理

- **包管理**
  - 统一使用 package.json 中定义的版本
  - 定期更新依赖到安全版本
  - 使用锁文件确保环境一致性

## 最佳实践

### 性能优化

- **按需加载**
  - 使用 React.lazy() 实现组件懒加载
  - 路由级别的代码分割
  - 图片和资源的懒加载

- **渲染优化**
  - 使用 React.memo 优化组件渲染
  - 使用 useMemo 和 useCallback 减少不必要的计算
  - 避免在渲染中创建新对象和函数

### 测试策略

- **单元测试**
  - 使用 Jest 和 React Testing Library
  - 覆盖核心业务逻辑
  - 组件渲染和交互测试

- **集成测试**
  - 路由和数据流测试
  - API 集成测试

### 代码质量

- **ESLint & Prettier**
  - 统一代码风格
  - 集成到开发工作流中
  - 提交前自动格式化

- **类型安全**
  - 推荐使用 TypeScript
  - 定义清晰的接口和类型
  - 利用 TypeScript 提供的类型检查能力

### 文档规范

- **组件文档**
  - 为每个公共组件编写文档
  - 包含使用示例和属性说明
  - 更新文档与代码同步

- **贡献指南**
  - 编写清晰的开发环境搭建说明
  - 代码提交规范
  - PR 审查流程