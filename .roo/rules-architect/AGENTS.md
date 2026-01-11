# Project Architecture Rules (Non-Obvious Only)

- The frontend uses React with Context API for state management rather than external libraries like Redux
- Two distinct parsing pipelines: JSON parser for dependency trees and TXT parser for analysis reports
- Custom hooks (useDependencyParser, useAnalysis) abstract complex business logic from UI components
- Dependency analysis algorithm distinguishes between declared vs undeclared and used vs unused dependencies
- The architecture separates concerns into File Processing -> Data Parsing -> Business Logic -> UI Rendering layers
- Tree visualization requires efficient algorithms for large dependency graphs (>1000 nodes possible)
- Redundancy detection implements specialized logic to identify when package A is used only for sub-dependency B
- Global state management includes uploaded files, dependency trees, and analysis results through Context providers