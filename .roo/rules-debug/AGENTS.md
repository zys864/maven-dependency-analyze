# Project Debug Rules (Non-Obvious Only)

- Dependency tree parsing errors often occur due to unexpected JSON structure - verify all required fields (groupId, artifactId, version, etc.) are present
- Large dependency trees may cause performance issues - implement virtual scrolling for tree visualization
- TXT parser is sensitive to Maven output format changes - ensure markers "Used undeclared dependencies found:" and "Unused declared dependencies found:" are correctly identified
- Redundancy detection algorithm may have false positives when sub-dependencies are used indirectly - verify actual usage before flagging as redundant
- File upload component should handle both JSON and TXT files with appropriate parsers based on file extension
- Analysis results may be affected by Maven scope settings (compile, test, runtime) - ensure proper scope handling in algorithms