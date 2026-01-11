# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview
- Java Maven dependency analysis tool that parses dependency trees and analyzes unused/undeclared dependencies
- Frontend built with React, using Tailwind CSS for styling and shadcn components
- Parses JSON dependency tree files (from `mvn dependency:tree -DoutputType=json`) and TXT analysis files (from `mvn dependency:analyze`)

## Build/Lint/Test Commands
- No explicit build commands in package.json - likely relies on Maven for backend and simple React dev server for frontend
- Project expects JSON dependency tree files in data/deps/ directory
- Analysis files should be in data/deps-analysis/ directory

## Code Style Guidelines
- Frontend uses React with TypeScript-like interfaces (as shown in design documents)
- Tailwind CSS classes should follow the recommended order: Layout → Sizing → Typography → Colors → States
- Components should be organized following the architecture described in design/frontend-architecture.md
- Use React Context for global state management (uploaded files, dependency trees, analysis results)
- Use custom hooks (like useDependencyParser, useAnalysis) for business logic separation

## Critical Architecture Patterns
- File parsing logic handles both JSON dependency trees and TXT analysis reports
- Dependency analysis identifies "used undeclared dependencies" and "unused declared dependencies"
- Tree visualization shows hierarchical Maven dependencies
- Redundancy analysis identifies unnecessary dependencies (when using only sub-dependencies of a package)
- The project distinguishes between "依赖树" (dependency tree) and "依赖使用情况分析" (usage analysis)

## Non-Standard Conventions
- JSON parser expects specific Maven dependency tree format with fields: groupId, artifactId, version, type, scope, classifier, optional, and children array
- TXT parser expects Maven dependency analysis format with "Used undeclared dependencies found:" and "Unused declared dependencies found:" sections
- Algorithm for redundancy detection looks for cases where package A is imported only to use its sub-dependency B, when B should be imported directly