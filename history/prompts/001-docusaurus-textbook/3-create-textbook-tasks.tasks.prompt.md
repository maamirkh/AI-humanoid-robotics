---
id: 3
title: Create-textbook-tasks
stage: tasks
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-docusaurus-textbook
branch: 001-docusaurus-textbook
user: user
command: /sp.tasks
labels: ["textbook", "tasks", "docusaurus", "education"]
links:
  spec: specs/001-docusaurus-textbook/spec.md
  plan: specs/001-docusaurus-textbook/plan.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-docusaurus-textbook/tasks.md
tests:
---

## Prompt

```text
# Physical AI & Humanoid Robotics Textbook — Tasks (Final Clean Part-1 Version)

**Scope:**
✔ ONLY writing
✔ ONLY diagrams
✔ ONLY conceptual examples
✔ 4 Modules
✔ 13 Weeks
✔ 15,000–20,000 words
✘ No ROS
✘ No Unity
✘ No Isaac
✘ No Whisper
✘ No GPT
✘ No hardware setup
✘ No installations

---

# ✅ PHASE 1 — Project Foundation

### Task 1.1 — Confirm Base Setup
- [x] Docusaurus installed
- [x] Repo connected to GitHub
- [ ] Verify folders:
  ```
  docs/
  diagrams/
  code/
  templates/
  scripts/
  static/img/
  ```

### Task 1.2 — Create Required Template Files
- [ ] `templates/frontmatter.md`
- [ ] `templates/page.md`
- [ ] `templates/example.md`

### Task 1.3 — Write `intro.md`
Include:
- What is Physical AI?
- Digital Brain → Physical Body concept
- 13-week learning roadmap
- Word count: 800–1000

---

# 📘 PHASE 2 — Module 1 (Weeks 1–5)

### ✦ Target:
- 4,000–5,000 words
- 3 diagrams
- 5 examples (conceptual text allowed)

---

### **Week 1 — Foundations of Physical AI**
Write:
- Digital intelligence vs physical intelligence
- Embodiment
- Robotics evolution
- Word count: 800–1000

---

### **Week 2 — Sensing the World**
Write:
- Sensors overview (camera, IMU, mic, touch)
- How physical systems perceive
- Conceptual example: simple sensor loop
- Diagram #1: “Sensor → Brain → Action Flow”
- Word count: 800–1000

---

### **Week 3 — Motor Control & Action**
Write:
- Basic locomotion theory
- Joint control concepts
- Stability basics
- Conceptual example: balance logic
- Word count: 700–1000

---

### **Week 4 — Perception Pipeline**
Write:
- High-level perception
- Object recognition (concept only)
- Environmental awareness
- Diagram #2: “Perception stages”
- Word count: 800–1000

---

### **Week 5 — Digital Twin Concepts (High-level Only)**
Write:
- What is a “digital twin”?
- How robots imagine the world
- Maps & scene representation (simple)
- Diagram #3: “Real World ↔ Digital World Loop”
- Word count: 700–900

---

### Task: Module-1 Summary Page
- [ ] 300–400 words recap
- [ ] What students learned

---

# 📘 PHASE 3 — Module 2 (Weeks 6–7)

### ✦ Target:
- 3,500–4,500 words
- 3 diagrams
- 5 examples

---

### **Week 6 — Physics & Interaction Basics**
Write:
- Contact, friction, force concepts
- How humanoids interact with ground
- Example: pseudo physics scenario
- Diagram: simple physics sketch
- Word count: 1,200–1,500

---

### **Week 7 — Human-Robot Interaction Basics**
Write:
- Gesture basics
- Attention & intention concepts
- Dialogue loop idea
- Diagram: human⇆robot loop
- Word count: 1,200–1,500

---

### Task: Module-2 Summary
- 300–400 words

---

# 📘 PHASE 4 — Module 3 (Weeks 8–10)

### ✦ Target:
- 4,000–5,000 words
- 3 diagrams
- 5 examples

---

### **Week 8 — Vision Systems (Conceptual)**
Write:
- How robots see (high-level)
- Depth, color, motion basics
- Example: conceptual frame analysis
- Diagram: “Vision pipeline”
- Word count: 1,200–1,500

---

### **Week 9 — Mapping & Understanding Environments**
Write:
- SLAM (only concept-level)
- Map types (grid, topo)
- Example: pseudo mapping
- Diagram: mapping loop
- Word count: 1,200–1,500

---

### **Week 10 — Navigation & Path Planning**
Write:
- High-level navigation
- Path planning idea
- Simple rule-based navigation example
- Diagram: navigation flowchart
- Word count: 1,200–1,500

---

### Task: Module-3 Summary
- 300–400 words

---

# 📘 PHASE 5 — Module 4 (Weeks 11–13)

### ✦ Target:
- 3,500–4,500 words
- 3 diagrams
- 5 examples

---

### **Week 11 — Kinematics & Movement**
Write:
- Forward/inverse kinematics (simple)
- Motion intuition
- Example: arm reach logic
- Diagram: simple limb sketch
- Word count: 1,200–1,500

---

### **Week 12 — Decision-Making for Robots**
Write:
- Rule-based decisions
- Basic planning ideas
- Example: decision tree
- Diagram: decision logic
- Word count: 1,200–1,500

---

### **Week 13 — Full System Overview**
Write:
- Sensors → Perception → Thinking → Action
- How complete humanoid loop works
- Diagram: end-to-end humanoid loop
- Word count: 1,000–1,200

---

### Task: Module-4 Summary & Conclusion
- Summary (300–400 words)
- Final conclusion (500 words)

---

# 📘 PHASE 6 — Quality Checks

- [ ] Wordcount check script
- [ ] Diagram count check
- [ ] Links check
- [ ] Mobile responsiveness
- [ ] Formatting clean

---

# 📘 PHASE 7 — Build & Deploy

- [ ] `npm run build`
- [ ] Deploy to **Vercel**
- [ ] Verify live site


---

# 📘 PHASE 8 — Final Submission

- GitHub repo link
- Vercel live link


---

# 🎉 Final Output
✔ 4 modules
✔ 13 weeks
✔ 15–20k words
✔ 12 diagrams
✔ 20 examples
✔ Fully deployed on Vercel
✔ Submission ready
```

## Response snapshot

Generated comprehensive task list for the Physical AI & Humanoid Robotics Textbook project. The tasks.md file contains:

- Phase 1: Setup tasks for creating project structure with docs/, diagrams/, code/, templates/, scripts/, static/img/ directories
- Phase 2: Foundational tasks including template creation, validation scripts, and metadata files
- Phase 3: User Story 1 (Priority P1) - Access Interactive Textbook Content with all 4 modules (15,000-20,000 words total)
- Phase 4: User Story 2 (Priority P2) - Run and Understand Code Examples with 20 conceptual examples (5 per module)
- Phase 5: User Story 3 (Priority P3) - View and Understand Diagrams with 12 diagrams (3 per module)
- Phase 6: User Story 4 (Priority P4) - Access Bonus Features for enhanced learning features
- Phase 7: Polish & Cross-Cutting Concerns with validation, build, and deployment tasks

All tasks follow the required format with checkboxes, task IDs, parallel markers [P], story labels [US1-US4], and specific file paths. The tasks are organized by user story priority to enable independent implementation and testing.

## Outcome

- ✅ Impact: Complete task breakdown created for textbook implementation
- 🧪 Tests: N/A - task list document
- 📁 Files: Created tasks.md in specs/001-docusaurus-textbook/
- 🔁 Next prompts: Ready for implementation of individual tasks
- 🧠 Reflection: Task list enables incremental delivery with MVP approach

## Evaluation notes (flywheel)

- Failure modes observed: None - successful task generation
- Graders run and results (PASS/FAIL): PASS - all tasks follow required format and organization
- Prompt variant (if applicable): Standard task generation
- Next experiment (smallest change to try): Begin implementation with Phase 1 tasks