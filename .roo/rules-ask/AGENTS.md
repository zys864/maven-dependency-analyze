# Project Documentation Rules (Non-Obvious Only)

- "依赖树" refers to Maven dependency tree parsed from JSON output of `mvn dependency:tree -DoutputType=json`
- "依赖使用情况分析" refers to dependency usage analysis from `mvn dependency:analyze` command output
- Data files should be placed in data/deps/ (for JSON dependency trees) and data/deps-analysis/ (for TXT analysis reports) directories
- The frontend architecture uses React with Context API for state management instead of Redux or other state management libraries
- Parsing logic differentiates between two file types: JSON dependency trees and TXT analysis reports with different structures and parsing requirements
- Redundancy analysis identifies when a package is imported only to use its sub-dependency, suggesting direct dependency on the sub-dependency instead
- The UI provides three main views: tree view, chart view, and analysis report view for different visualization needs