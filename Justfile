# Justfile for Maven Dependency Analyzer

# Default recipe
default:
    echo "Maven Dependency Analyzer - Available recipes:"
    just --list

# Sync dependencies
sync:
    uv sync

# Run the application with various options
run:
    @echo "Usage: just run [command] [args...]"
    @echo "Examples:"
    @echo "  just run show-tree example/example-dependency-tree.json"
    @echo "  just run analyze example/example-dependency-tree.json example/example-deps-analysis.txt"
    @echo "  just run export-report example/example-dependency-tree.json example/example-deps-analysis.txt output/report.xlsx"

# Show dependency tree
show-tree tree_path:
    uv run python main.py show-tree --tree {{tree_path}}

# Analyze dependencies
analyze tree_path analysis_path:
    uv run python main.py analyze --tree {{tree_path}} --analysis {{analysis_path}}

# Check redundancy
check-redundancy tree_path analysis_path:
    uv run python main.py check-redundancy --tree {{tree_path}} --analysis {{analysis_path}}

# Export report
export-report tree_path analysis_path output_path:
    mkdir -p output
    uv run python main.py export-report --tree {{tree_path}} --analysis {{analysis_path}} --output {{output_path}}

# Run with example files
example:
    just analyze example/example-dependency-tree.json example/example-deps-analysis.txt

# Export example report
example-export:
    just export-report example/example-dependency-tree.json example/example-deps-analysis.txt output/example-report.xlsx

# Test all commands
test-all:
    @echo "Testing show-tree..."
    just show-tree example/example-dependency-tree.json
    @echo ""
    @echo "Testing analyze..."
    just analyze example/example-dependency-tree.json example/example-deps-analysis.txt
    @echo ""
    @echo "Testing check-redundancy..."
    just check-redundancy example/example-dependency-tree.json example/example-deps-analysis.txt
    @echo ""
    @echo "Testing export-report..."
    just export-report example/example-dependency-tree.json example/example-deps-analysis.txt output/test-just.xlsx