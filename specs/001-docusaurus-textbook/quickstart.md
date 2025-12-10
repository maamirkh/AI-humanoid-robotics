# Quickstart Guide: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-docusaurus-textbook
**Date**: 2025-12-09
**Status**: Complete

## Getting Started

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git for version control
- Ubuntu 22.04 (for testing code examples)

### Installation

1. **Install Docusaurus globally** (if not already installed):
   ```bash
   npm install -g @docusaurus/core@latest
   ```

2. **Navigate to project root**:
   ```bash
   cd /path/to/your/project
   ```

3. **Install project dependencies**:
   ```bash
   npm install
   ```

### Project Structure Overview
```
docs/                    # Textbook content organized by modules
├── module-1/            # Module 1 content (4000-5000 words)
├── module-2/            # Module 2 content (3500-4500 words)
├── module-3/            # Module 3 content (4000-5000 words)
└── module-4/            # Module 4 content (3500-4500 words)
diagrams/                # Visual diagrams organized by modules
├── module-1/            # Module 1 diagrams
├── module-2/            # Module 2 diagrams
├── module-3/            # Module 3 diagrams
└── module-4/            # Module 4 diagrams
code/                    # Code examples organized by modules
├── module-1/            # Module 1 examples
├── module-2/            # Module 2 examples
├── module-3/            # Module 3 examples
└── module-4/            # Module 4 examples
examples/                # Example metadata
scripts/                 # Validation scripts
static/                  # Static assets
templates/               # Content templates
```

## Development Workflow

### 1. Adding Content
1. Create or edit markdown files in the appropriate `docs/module-x/` directory
2. Ensure each file includes proper Docusaurus frontmatter:
   ```yaml
   ---
   title: "Your Title"
   description: "Your description"
   sidebar_position: 1
   ---
   ```
3. Maintain word count within the specified ranges per module

### 2. Adding Code Examples
1. Create example in the appropriate `code/module-x/` directory
2. Include environment files (environment.yaml, requirements.txt, or pyproject.toml)
3. Create a test script that verifies the example runs in Ubuntu 22.04
4. Add to `examples/meta.yaml` with proper tagging (including `gpu: true` if needed)

### 3. Adding Diagrams
1. Place diagram in the appropriate `diagrams/module-x/` directory
2. Ensure SVG format is preferred, PNG as fallback
3. Add to `diagrams/meta.yaml` with proper alt text and caption for accessibility
4. Verify WCAG 2.1 AA compliance

### 4. Running the Development Server
```bash
npm start
```
This starts a local development server at `http://localhost:3000`

## Validation

### Running Validation Scripts
1. **Check word count**:
   ```bash
   python scripts/check-wordcount.py
   ```

2. **Check links**:
   ```bash
   bash scripts/link-check.sh
   ```

3. **Run full verification**:
   ```bash
   bash scripts/verify.sh
   ```

### Before Creating a Pull Request
1. Ensure all content meets word count requirements
2. Verify all code examples run in Ubuntu 22.04
3. Confirm all diagrams have proper alt text and accessibility compliance
4. Run all validation scripts and fix any issues
5. Test locally with `npm start`

## Building for Production

### Build the Static Site
```bash
npm run build
```
This creates a static site in the `build/` directory optimized for deployment.

### Deployment
The site is designed for deployment on Vercel only. The build output in the `build/` directory can be deployed directly to Vercel.

## Troubleshooting

### Common Issues
- **Module word count too high/low**: Adjust content to meet the specified ranges
- **Broken links**: Run `scripts/link-check.sh` to identify and fix broken links
- **Code example not running**: Test in a clean Ubuntu 22.04 environment
- **Diagram accessibility issues**: Ensure all diagrams have proper alt text and captions

### Validation Script Issues
- If `check-wordcount.py` fails, verify the word count in each module
- If `link-check.sh` fails, verify all internal links point to existing files
- If `verify.sh` fails, address all issues before proceeding