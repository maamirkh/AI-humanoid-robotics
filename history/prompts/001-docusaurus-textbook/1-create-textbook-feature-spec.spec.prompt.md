---
id: 1
title: Create-textbook-feature-spec
stage: spec
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-docusaurus-textbook
branch: 001-docusaurus-textbook
user: user
command: /sp.specify
labels: ["textbook", "spec", "docusaurus", "education"]
links:
  spec: specs/001-docusaurus-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-docusaurus-textbook/spec.md
 - specs/001-docusaurus-textbook/checklists/requirements.md
tests:
---

## Prompt

```text
# Feature Specification — Physical AI & Humanoid Robotics Textbook
Feature Branch: 001-ai-robotics-textbook
Status: Stable (Aligned With Constitution)

---

## 1. Purpose & Scope

### 1.1 Definition
This specification defines all artifacts, checks, folder structures, automation rules, and deliverables needed to generate the **Docusaurus-based Physical AI & Humanoid Robotics textbook**, strictly following the project constitution.

### 1.2 Scope (Important)
This project ONLY includes:
- Textbook content creation
- Diagrams
- Example code
- Documentation
- CI scripts
- Deployment setup
- Use reuseable intelligence and skills

This project does **NOT** include:
- Hardware installation
- Robot drivers
- Operating robots
- Chatbot or VLA agent development
- ROS/Isaac execution environments

(Execution restriction added for safety.)

### 1.3 Target Audience
- Primary: AI/ML students
- Secondary: Robotics beginners
- Tertiary: Hackathon learners

### 1.4 Deliverables
- Docusaurus textbook
- Public GitHub repository

---

## 2. Success Criteria (Measurable)

### 2.1 Content Requirements
Word count must satisfy:

| Module | Range |
|--------|---------|
| Module 1 | 4000–5000 |
| Module 2 | 3500–4500 |
| Module 3 | 4000–5000 |
| Module 4 | 3500–4500 |
| **Total** | **15000–20000** |

### 2.2 Code Examples
- 20 runnable examples (5 per module)
- Must include:
  - environment.yaml
  - requirements.txt or pyproject.toml
  - test.sh (Ubuntu 22.04 headless run)

### 2.3 Code Quality
- English comments
- Required: Type hints
- Required: Basic error handling

### 2.4 GPU Tagging
- GPU-required examples must include:

```yaml
gpu: true
```

in `examples/meta.yaml`.

---

## 3. Project Structure Requirements

### 3.1 Folder Structure (Final)
```
docs/
  module-1/
  module-2/
  module-3/
  module-4/
diagrams/
  module-1/
  module-2/
  module-3/
  module-4/
code/
  module-1/
  module-2/
  module-3/
  module-4/
examples/
scripts/
static/img/
specs/
templates/
```

### 3.2 Diagrams
- Store in `diagrams/module-x/`
- Formats:
  - Preferred: SVG
  - Fallback: PNG
- Each diagram must include:
  - Alt text (markdown)
  - Caption in `diagrams/meta.yaml`
- Accessibility: WCAG 2.1 AA

---

## 4. Deployment & Release

### 4.1 Build
```
npm run build
```
Output → `/build`

### 4.2 Deployment Platform (Mandatory)
Deployment MUST be done on **Vercel only**.
Claude Code MUST prepare Vercel-compatible build output and deployment instructions exclusively.


### 4.3 Pre-Release Verification
Before releasing:
1. `verify.sh`
2. Link checker
3. Accessibility audit
4. Word count check
5. Diagram count check

---

## 5. Deliverable Checklist (PR Requirement)

### 5.1 Content Deliverables
- [ ] docs/ (all 4 modules, frontmatter included)
- [ ] diagrams/ (12 diagrams + alt text)
- [ ] code/ (20 runnable examples)

### 5.2 Infrastructure Deliverables
- [ ] scripts/verify.sh
- [ ] scripts/check-wordcount.py
- [ ] scripts/link-check.sh

### 5.3 Documentation Deliverables
- [ ] README with:
  - Setup instructions
  - How to run examples
  - Environment variables
  - Known issues
  - WhatsApp contact
- [ ] demo-video.mp4 (≤90 seconds)

### 5.4 Automation Logs
- [ ] specs/auto-created.log (if auto-fill used)

---

## 6. Scoring & Bonuses

### Base Score (100 Points)
- 100% textbook content

### Bonus Features (+50 each)
- Claude Subagents
- Better-auth + profiling
- Personalization engine
- Urdu translation toggle

---

## 7. Exclusions (Strict)

The system MUST NOT:
- Build, install, or configure physical robots
- Run ROS / Gazebo / Isaac simulations
- Provide hardware setup scripts
- Implement chatbot / VLA agents
- Require cloud GPU usage without approval

(Added to avoid unintended execution by Claude Code.)

---

## 8. Notes & Recommendations

### 8.1 Templates
Provide:
- `templates/frontmatter.md`
- `docs/examples/frontmatter.md`

### 8.2 Validation Scripts
Required:
- `scripts/check-wordcount.py`
- `scripts/link-check.sh`

### 8.3 Testing Environment
- Dockerfile for Ubuntu 22.04
- Ensures examples run in a clean reproducible environment

---

## 9. Execution Restrictions (NEW – Added for Safety)
Claude Code MUST:
1. Only execute tasks related to textbook generation.
2. Never auto-start:
   - chatbot systems
   - hardware automation
   - ROS/Isaac execution
3. Only use this spec for:
   - file generation
   - content creation
   - documentation
   - CI tooling

---
```

## Response snapshot

Created comprehensive feature specification for the Physical AI & Humanoid Robotics Textbook project. The specification includes:

- 4 user stories covering core textbook access, code examples, diagrams, and bonus features
- 15 functional requirements covering content, code examples, diagrams, deployment, and validation
- 7 measurable success criteria with specific metrics
- Key entities and edge cases identified
- Quality checklist created and validated

The spec is aligned with the project constitution and defines a complete textbook with 4 modules (15,000-20,000 words), 20 runnable code examples, 12 diagrams, and proper deployment on Vercel.

## Outcome

- ✅ Impact: Complete feature specification created for textbook project
- 🧪 Tests: N/A - specification document
- 📁 Files: Created spec.md and requirements.md in specs/001-docusaurus-textbook/
- 🔁 Next prompts: Ready for planning phase with /sp.plan
- 🧠 Reflection: Specification covers all requirements from constitution and user input

## Evaluation notes (flywheel)

- Failure modes observed: None - successful spec creation
- Graders run and results (PASS/FAIL): PASS - all validation checklist items completed
- Prompt variant (if applicable): Standard feature specification
- Next experiment (smallest change to try): Proceed to planning phase with /sp.plan