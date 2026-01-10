# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Python tool for analyzing Maven dependency trees from Java repositories. It processes two types of Maven outputs:

1. **Dependency Tree Data** (`data/deps/`): JSON output from `mvn dependency:tree -DoutputType=json -DoutputFile=dependency-tree.json`
2. **Dependency Analysis Data** (`data/deps-analysis/`): Text output from `mvn dependency:analyze`

The tool aims to:
- Parse and visualize Maven dependency trees
- Identify used-but-undeclared dependencies
- Identify declared-but-unused dependencies  
- Detect redundant dependencies (cases where package A is imported only to use its transitive dependency B)
- Export analysis results to Excel with formatting

## Environment Setup

This project uses `uv` for Python package management with Python 3.13.

```bash
# Install dependencies
uv sync

# Activate virtual environment (if needed manually)
source .venv/bin/activate

# Run the main script
python main.py
```

## Data Sources

### Generating Input Data from Java Projects

To generate the required input files from a Java Maven project:

```bash
# Generate dependency tree JSON
mvn dependency:tree -DoutputType=json -DoutputFile=dependency-tree.json

# Generate dependency analysis report
mvn dependency:analyze > deps-analysis.txt
```

### Data Format

**Dependency Tree JSON Structure:**
- Hierarchical JSON with root node describing the project artifact
- Each node contains: `groupId`, `artifactId`, `version`, `type`, `scope`, `classifier`, `optional`
- `children` array contains transitive dependencies recursively
- Reference: https://maven.apache.org/components/plugins/maven-dependency-plugin/examples/tree-mojo.html

**Dependency Analysis Text Format:**
- Section after `Used undeclared dependencies found:` lists dependencies that are used in code but not explicitly declared
- Section after `Unused declared dependencies found:` lists dependencies that are declared but not actually used

### Example Data

Example input files are version-controlled in:
- `data/deps/example-dependency-tree.json`
- `data/deps-analysis/example-deps-analysis.txt`

These serve as reference examples for the expected input format.

## Project Structure

The project is in early development with minimal code structure currently:
- `main.py`: Entry point (currently a placeholder)
- `data/`: Directory for input data files (mostly gitignored except examples)
- `example/`: Additional example files

## Development Notes

### Language and Documentation
The README and documentation are primarily in Chinese (中文). Code comments and variable names may be bilingual.

### Key Analysis Goals

**Redundant Dependency Detection:**
The core analysis focuses on identifying cases where:
- Package A is imported only to use classes from its transitive dependency B
- No classes/functionality from Package A itself are used
- Solution: Directly declare dependency B instead of relying on transitive dependency through A

This requires cross-referencing:
1. The dependency tree structure (which packages bring in which transitive dependencies)
2. The usage analysis (which packages are actually used vs declared)
