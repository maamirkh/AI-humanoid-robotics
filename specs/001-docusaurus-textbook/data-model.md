# Data Model: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-docusaurus-textbook
**Date**: 2025-12-09
**Status**: Complete

## Core Entities

### Textbook Module
- **Name**: String (required) - Module identifier (e.g., "module-1", "module-2")
- **Title**: String (required) - Display title for the module
- **Content**: String (required) - Markdown/MDX content (4000-5000 words for modules 1&3, 3500-4500 for modules 2&4)
- **WordCount**: Integer (required) - Actual word count for validation
- **Frontmatter**: Object (required) - Docusaurus frontmatter metadata
- **Sections**: Array of Section objects - Organized content sections

### Section
- **Title**: String (required) - Section title
- **Content**: String (required) - Section content in markdown
- **Diagrams**: Array of Diagram references - Associated diagrams
- **CodeExamples**: Array of CodeExample references - Associated code examples

### Code Example
- **Id**: String (required) - Unique identifier
- **Title**: String (required) - Display title
- **Description**: String (required) - Purpose and explanation
- **Code**: String (required) - Source code content
- **Language**: String (required) - Programming language for syntax highlighting
- **FilePath**: String (required) - Path to the example file
- **Environment**: Object - Environment configuration (environment.yaml, requirements.txt, etc.)
- **TestScript**: String - Path to test script
- **GpuRequired**: Boolean - Whether GPU is required to run
- **Module**: String (required) - Reference to parent module

### Diagram
- **Id**: String (required) - Unique identifier
- **Title**: String (required) - Diagram title
- **AltText**: String (required) - Accessibility alt text
- **Caption**: String (required) - Descriptive caption
- **FilePath**: String (required) - Path to the diagram file (SVG/PNG)
- **Format**: String (required) - SVG or PNG
- **Module**: String (required) - Reference to parent module
- **AccessibilityCompliant**: Boolean - WCAG 2.1 AA compliance status

### Validation Script
- **Name**: String (required) - Script name (check-wordcount.py, link-check.sh, verify.sh)
- **Purpose**: String (required) - What the script validates
- **FilePath**: String (required) - Path to the script file
- **Dependencies**: Array of String - Required dependencies
- **OutputFormat**: String - Format of validation output

## File Structure Model

### Module Directory Structure
```
docs/
  module-1/          # Contains module-1 content files
  module-2/          # Contains module-2 content files
  module-3/          # Contains module-3 content files
  module-4/          # Contains module-4 content files
diagrams/
  module-1/          # Contains module-1 diagrams
  module-2/          # Contains module-2 diagrams
  module-3/          # Contains module-3 diagrams
  module-4/          # Contains module-4 diagrams
code/
  module-1/          # Contains module-1 code examples
  module-2/          # Contains module-2 code examples
  module-3/          # Contains module-3 code examples
  module-4/          # Contains module-4 code examples
examples/            # Contains example metadata
scripts/             # Contains validation scripts
static/              # Static assets
```

### Content File Schema
```yaml
---
title: "Module Title"
description: "Module description"
sidebar_position: 1  # Position in sidebar navigation
---
```

### Meta Configuration Schema (examples/meta.yaml)
```yaml
examples:
  - id: "example-id"
    gpu: true/false
    module: "module-x"
    title: "Example title"
    description: "Example description"
```

### Diagram Metadata Schema (diagrams/meta.yaml)
```yaml
diagrams:
  - id: "diagram-id"
    title: "Diagram title"
    altText: "Accessibility text"
    caption: "Diagram caption"
    module: "module-x"
    accessibilityCompliant: true
```

## Validation Rules

### Content Validation
- Module word count must be within specified range (4000-5000 for modules 1&3, 3500-4500 for modules 2&4)
- Total word count must be between 15,000-20,000 across all modules
- All diagrams must have alt text and captions
- All code examples must have proper frontmatter and environment files
- All content must include proper Docusaurus frontmatter

### Technical Validation
- Code examples must run successfully in Ubuntu 22.04 environment
- All links must be valid (no broken links)
- All diagrams must be accessible (WCAG 2.1 AA compliance)
- All code must include type hints and English comments
- GPU-required examples must be properly tagged