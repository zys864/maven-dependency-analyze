# Project Documentation Rules (Non-Obvious Only)

## Data Sources and Formats
- "data/deps/" contains Maven dependency tree JSON files, not general project dependencies
- "data/deps-analysis/" contains Maven dependency analysis text files, different from tree JSON format
- Input files must be generated with specific Maven commands: `mvn dependency:tree -DoutputType=json` and `mvn dependency:analyze`

## Project Structure Context
- "src/" directory contains the core Maven dependency analysis logic, not a web application
- Chinese documentation (README.md) is the primary documentation; WARP.md provides additional context in English
- The project focuses on identifying redundant dependencies where package A is used only for its transitive dependency B

## Tool Usage
- This is a CLI tool using Click framework, not a web or GUI application
- Commands like `show-tree` and `analyze` have specific required parameters for input files
- The tool uses uv for package management, not pip or poetry (despite pyproject.toml format)