# Implementation Plan: Physical AI — Capstone Quarter

**Branch**: `001-physical-ai-capstone` | **Date**: 2025-12-11 | **Spec**: [specs/001-physical-ai-capstone/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-physical-ai-capstone/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan details the full implementation strategy for building the **Physical AI — Capstone Quarter** textbook content using:
- Docusaurus (user installed manually)
- SpecKit Plus automation
- Claude Code file generation
- GitHub Pages deployment

Scope covers:
4 modules (Foundations, ROS 2, Simulation, VLA), 13 weeks of content, 15k–20k words.

The textbook focuses on Physical AI principles and embodied intelligence, covering ROS 2, Gazebo, NVIDIA Isaac, and Vision-Language-Action systems as outlined in the spec.

## Technical Context

**Language/Version**: Markdown/MDX, Node.js 18+ + Docusaurus v3, Node.js, NPM
**Primary Dependencies**: Docusaurus v3, Node.js, NPM
**Storage**: Files only (no database)
**Testing**: Bash scripts, validation tools
**Target Platform**: Web (GitHub Pages deployment)
**Project Type**: Single static site project
**Performance Goals**: Fast loading, WCAG 2.1 AA accessibility compliance
**Constraints**: Must deploy on GitHub Pages, Ubuntu 22.04 for testing scripts
**Scale/Scope**: Educational textbook with 4 modules, 15k-20k words, 20 examples, 12 diagrams

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Language rules: Code → English, Docs → English, File names → English (kebab-case)
- Directory rules: Organize by feature/module, max 3-4 nesting levels
- Auto-create rules: Auto-generate missing files/folders when needed
- Content requirements: 15,000-20,000 words total (Module 1: 4k-5k, Module 2: 3.5k-4.5k, Module 3: 4k-5k, Module 4: 3.5k-4.5k)
- Code requirements: 20 examples (5 per module), Ubuntu 22.04 compatibility, type hints, English comments, error handling
- Diagrams: 12 diagrams (3 per module), accessibility WCAG 2.1 AA
- Technical standards: Ubuntu 22.04, no hardware/ROS execution
- Deployment: GitHub Pages only
- Exclusions: No hardware installation, no robot drivers, no operating robots, no chatbot/VLA agent development, no ROS/Isaac execution

**New Content Considerations**:
- Module 1 (ROS 2): Will require examples demonstrating ROS 2 Nodes, Topics, Services, and rclpy integration
- Module 2 (Gazebo & Unity): Will require simulation environment documentation and examples
- Module 3 (NVIDIA Isaac): Will require documentation for Isaac Sim and Isaac ROS integration
- Module 4 (VLA): Will require examples for voice-to-action and cognitive planning with LLMs

## Project Structure

### Documentation (this feature)
```text
specs/001-physical-ai-capstone/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
docs/                    # All textbook chapters (module-1/, module-2/, module-3/, module-4/)
diagrams/                # 12 diagrams (SVG/PNG) (module-1/, module-2/, module-3/, module-4/)
code/                    # 20 runnable examples (module-1/, module-2/, module-3/, module-4/)
examples/                # example metadata (meta.yaml)
scripts/                 # CI scripts (check-wordcount.py, link-check.sh, verify.sh)
static/                  # Docusaurus static assets
specs/                   # All specifications
.specify/                # SpecKit internal
.claude/                 # Claude automation data
templates/               # frontmatter + content templates
history/                 # automation logs
CLAUDE.md
```

**Structure Decision**: Single static site project structure selected, aligned with Docusaurus requirements. No backend, frontend, or mobile components needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified. Project fully constitution-compliant.

**Additional Considerations for New Content**:
- **ROS 2 Integration**: Need to ensure examples can run in simulated environments without requiring physical hardware
- **NVIDIA Isaac Dependencies**: May require special setup instructions for Isaac SDK integration
- **Gazebo/Unity Simulation**: Need to document how to set up simulation environments
- **VLA Implementation**: Voice-to-action examples may require audio processing libraries
