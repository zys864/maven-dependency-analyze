# Project Coding Rules (Non-Obvious Only)

- Always use the specific JSON format expected by the parser: fields must include groupId, artifactId, version, type, scope, classifier, optional, and children array
- TXT parser specifically looks for "Used undeclared dependencies found:" and "Unused declared dependencies found:" markers to identify sections
- Dependency analysis algorithm must distinguish between "依赖树" (dependency tree) and "依赖使用情况分析" (usage analysis) data processing
- Redundancy detection logic must identify cases where package A is imported only to use its sub-dependency B (when B should be imported directly)
- Use React Context for managing global state (uploaded files, dependency trees, analysis results) instead of prop drilling
- Custom hooks like useDependencyParser and useAnalysis should encapsulate complex business logic
- Tailwind classes must follow order: Layout → Sizing → Typography → Colors → States for maintainability