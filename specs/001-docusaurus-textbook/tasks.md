---
description: "Task list for Physical AI & Humanoid Robotics Textbook implementation"
---

# Tasks: Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `/specs/001-docusaurus-textbook/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `docs/`, `diagrams/`, `code/`, `scripts/`, `templates/`, `static/img/` at repository root
- **Web app**: Not applicable
- **Mobile**: Not applicable
- Paths shown below follow the Docusaurus project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan with docs/, diagrams/, code/, templates/, scripts/, static/img/
- [x] T002 [P] Create module directories in docs/ (module-1/, module-2/, module-3/, module-4/)
- [x] T003 [P] Create module directories in diagrams/ (module-1/, module-2/, module-3/, module-4/)
- [x] T004 [P] Create module directories in code/ (module-1/, module-2/, module-3/, module-4/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create required template files in templates/
- [x] T006 [P] Create `templates/frontmatter.md` with Docusaurus frontmatter template
- [x] T007 [P] Create `templates/page.md` with Docusaurus page template
- [x] T008 [P] Create `templates/example.md` with Docusaurus example template
- [x] T009 Create validation scripts in scripts/
- [x] T010 [P] Create `scripts/check-wordcount.py` for word count validation
- [x] T011 [P] Create `scripts/link-check.sh` for link validation
- [x] T012 [P] Create `scripts/verify.sh` for comprehensive validation
- [x] T013 Create examples/meta.yaml for code example metadata
- [x] T014 Create diagrams/meta.yaml for diagram metadata
- [x] T015 Create README with setup instructions and environment details

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Access Interactive Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Students can access and navigate the Physical AI & Humanoid Robotics textbook with all 4 modules (15,000-20,000 words total)

**Independent Test**: The textbook can be fully accessed and navigated by a student, with all 4 modules available and properly formatted with proper navigation between sections.

### Implementation for User Story 1

- [x] T016 [P] [US1] Create `docs/intro.md` with Physical AI introduction, Digital Brain → Physical Body concept, and 13-week roadmap (800-1000 words)
- [x] T017 [P] [US1] Create `docs/module-1/week-1-foundations.md` with Digital intelligence vs physical intelligence, Embodiment, Robotics evolution (800-1000 words)
- [x] T018 [P] [US1] Create `docs/module-1/week-2-sensing.md` with Sensors overview, How physical systems perceive, Conceptual example: simple sensor loop (800-1000 words)
- [x] T019 [P] [US1] Create `docs/module-1/week-3-motor-control.md` with Basic locomotion theory, Joint control concepts, Stability basics, Conceptual example: balance logic (700-1000 words)
- [x] T020 [P] [US1] Create `docs/module-1/week-4-perception.md` with High-level perception, Object recognition (concept only), Environmental awareness (800-1000 words)
- [x] T021 [P] [US1] Create `docs/module-1/week-5-digital-twin.md` with What is a "digital twin"?, How robots imagine the world, Maps & scene representation (700-900 words)
- [x] T022 [US1] Create `docs/module-1/summary.md` with 300-400 word recap of what students learned in Module 1
- [x] T023 [P] [US1] Create `docs/module-2/week-6-physics.md` with Contact, friction, force concepts, How humanoids interact with ground, Example: pseudo physics scenario (1,200-1,500 words)
- [x] T024 [P] [US1] Create `docs/module-2/week-7-human-robot.md` with Gesture basics, Attention & intention concepts, Dialogue loop idea (1,200-1,500 words)
- [x] T025 [US1] Create `docs/module-2/summary.md` with 300-400 word summary of Module 2
- [x] T026 [P] [US1] Create `docs/module-3/week-8-vision.md` with How robots see (high-level), Depth, color, motion basics, Example: conceptual frame analysis (1,200-1,500 words)
- [x] T027 [P] [US1] Create `docs/module-3/week-9-mapping.md` with SLAM (only concept-level), Map types (grid, topo), Example: pseudo mapping (1,200-1,500 words)
- [x] T028 [P] [US1] Create `docs/module-3/week-10-navigation.md` with High-level navigation, Path planning idea, Simple rule-based navigation example (1,200-1,500 words)
- [x] T029 [US1] Create `docs/module-3/summary.md` with 300-400 word summary of Module 3
- [x] T030 [P] [US1] Create `docs/module-4/week-11-kinematics.md` with Forward/inverse kinematics (simple), Motion intuition, Example: arm reach logic (1,200-1,500 words)
- [x] T031 [P] [US1] Create `docs/module-4/week-12-decision.md` with Rule-based decisions, Basic planning ideas, Example: decision tree (1,200-1,500 words)
- [x] T032 [P] [US1] Create `docs/module-4/week-13-system.md` with Sensors → Perception → Thinking → Action, How complete humanoid loop works (1,000-1,200 words)
- [x] T033 [US1] Create `docs/module-4/summary.md` with 300-400 word summary of Module 4
- [x] T034 [US1] Create `docs/conclusion.md` with 500 word final conclusion

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Run and Understand Code Examples (Priority: P2)

**Goal**: Students can access 20 runnable code examples (5 per module) with proper documentation, environment files, and test scripts that run in Ubuntu 22.04

**Independent Test**: All 20 code examples (5 per module) are available with proper documentation, environment files, and test scripts that can run successfully in Ubuntu 22.04.

### Implementation for User Story 2

- [ ] T035 [P] [US2] Create `code/module-1/example-1-sensor-loop.py` with conceptual sensor loop example, type hints, English comments, error handling
- [ ] T036 [P] [US2] Create `code/module-1/example-2-balance-logic.py` with conceptual balance logic example, type hints, English comments, error handling
- [ ] T037 [P] [US2] Create `code/module-1/example-3-object-recognition.py` with conceptual object recognition example, type hints, English comments, error handling
- [ ] T038 [P] [US2] Create `code/module-1/example-4-digital-twin.py` with conceptual digital twin example, type hints, English comments, error handling
- [ ] T039 [P] [US2] Create `code/module-1/example-5-embodiment.py` with conceptual embodiment example, type hints, English comments, error handling
- [ ] T040 [P] [US2] Create `code/module-2/example-1-physics-scenario.py` with pseudo physics scenario example, type hints, English comments, error handling
- [ ] T041 [P] [US2] Create `code/module-2/example-2-human-robot-interaction.py` with human-robot interaction example, type hints, English comments, error handling
- [ ] T042 [P] [US2] Create `code/module-2/example-3-contact-modeling.py` with contact modeling example, type hints, English comments, error handling
- [ ] T043 [P] [US2] Create `code/module-2/example-4-force-analysis.py` with force analysis example, type hints, English comments, error handling
- [ ] T044 [P] [US2] Create `code/module-2/example-5-friction-modeling.py` with friction modeling example, type hints, English comments, error handling
- [ ] T045 [P] [US2] Create `code/module-3/example-1-vision-pipeline.py` with conceptual vision pipeline example, type hints, English comments, error handling
- [ ] T046 [P] [US2] Create `code/module-3/example-2-frame-analysis.py` with conceptual frame analysis example, type hints, English comments, error handling
- [ ] T047 [P] [US2] Create `code/module-3/example-3-slam-concept.py` with conceptual SLAM example, type hints, English comments, error handling
- [ ] T048 [P] [US2] Create `code/module-3/example-4-map-types.py` with conceptual map types example, type hints, English comments, error handling
- [ ] T049 [P] [US2] Create `code/module-3/example-5-pseudo-mapping.py` with conceptual pseudo mapping example, type hints, English comments, error handling
- [ ] T050 [P] [US2] Create `code/module-4/example-1-kinematics.py` with conceptual kinematics example, type hints, English comments, error handling
- [ ] T051 [P] [US2] Create `code/module-4/example-2-arm-reach.py` with conceptual arm reach logic example, type hints, English comments, error handling
- [ ] T052 [P] [US2] Create `code/module-4/example-3-decision-tree.py` with decision tree example, type hints, English comments, error handling
- [ ] T053 [P] [US2] Create `code/module-4/example-4-rule-based.py` with rule-based decisions example, type hints, English comments, error handling
- [ ] T054 [P] [US2] Create `code/module-4/example-5-system-overview.py` with system overview example, type hints, English comments, error handling
- [ ] T055 [P] [US2] Create `code/module-1/test.sh` to verify module-1 examples run in Ubuntu 22.04
- [ ] T056 [P] [US2] Create `code/module-2/test.sh` to verify module-2 examples run in Ubuntu 22.04
- [ ] T057 [P] [US2] Create `code/module-3/test.sh` to verify module-3 examples run in Ubuntu 22.04
- [ ] T058 [P] [US2] Create `code/module-4/test.sh` to verify module-4 examples run in Ubuntu 22.04
- [ ] T059 [US2] Update `examples/meta.yaml` with all 20 examples and proper GPU tagging where needed

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View and Understand Diagrams (Priority: P3)

**Goal**: Students can access 12 diagrams (3 per module) with proper alt text, captions, and WCAG 2.1 AA accessibility compliance

**Independent Test**: All 12 diagrams (3 per module) are accessible with proper alt text, captions, and accessibility compliance (WCAG 2.1 AA).

### Implementation for User Story 3

- [x] T060 [P] [US3] Create `diagrams/module-1/diagram-1-sensor-flow.svg` with "Sensor → Brain → Action Flow" diagram, proper alt text, and caption
- [x] T061 [P] [US3] Create `diagrams/module-1/diagram-2-perception-stages.svg` with "Perception stages" diagram, proper alt text, and caption
- [x] T062 [P] [US3] Create `diagrams/module-1/diagram-3-real-digital-loop.svg` with "Real World ↔ Digital World Loop" diagram, proper alt text, and caption
- [x] T063 [P] [US3] Create `diagrams/module-2/diagram-1-physics-sketch.svg` with simple physics sketch diagram, proper alt text, and caption
- [x] T064 [P] [US3] Create `diagrams/module-2/diagram-2-human-robot-loop.svg` with "human⇆robot loop" diagram, proper alt text, and caption
- [x] T065 [P] [US3] Create `diagrams/module-3/diagram-1-vision-pipeline.svg` with "Vision pipeline" diagram, proper alt text, and caption
- [x] T066 [P] [US3] Create `diagrams/module-3/diagram-2-mapping-loop.svg` with "mapping loop" diagram, proper alt text, and caption
- [x] T067 [P] [US3] Create `diagrams/module-3/diagram-3-navigation-flowchart.svg` with "navigation flowchart" diagram, proper alt text, and caption
- [x] T068 [P] [US3] Create `diagrams/module-4/diagram-1-limb-sketch.svg` with "simple limb sketch" diagram, proper alt text, and caption
- [x] T069 [P] [US3] Create `diagrams/module-4/diagram-2-decision-logic.svg` with "decision logic" diagram, proper alt text, and caption
- [x] T070 [P] [US3] Create `diagrams/module-4/diagram-3-end-to-end-loop.svg` with "end-to-end humanoid loop" diagram, proper alt text, and caption
- [x] T071 [US3] Update `diagrams/meta.yaml` with all 12 diagrams, alt text, captions, and accessibility compliance status
- [x] T072 [US3] Ensure all diagrams meet WCAG 2.1 AA accessibility standards

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Access Bonus Features (Priority: P4)

**Goal**: Students can optionally access enhanced learning features like content personalization, Urdu translation, or authentication-based features

**Independent Test**: Optional bonus features (subagents, authentication, personalization, Urdu translation) are available and functional when implemented.

### Implementation for User Story 4

- [x] T073 [US4] Research and document Claude subagent implementation for textbook
- [x] T074 [US4] Research and document Better-auth implementation for profiling
- [x] T075 [US4] Research and document personalization engine implementation
- [x] T076 [US4] Research and document Urdu translation toggle implementation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T077 [P] Update README with complete setup instructions, how to run examples, environment variables, known issues, and WhatsApp contact
- [ ] T078 [P] Update README with demo-video.mp4 (≤90 seconds) reference
- [ ] T079 Run wordcount validation to ensure 15,000-20,000 word target is met
- [ ] T080 Run link validation to ensure 100% link accuracy
- [ ] T081 Run accessibility audit to ensure WCAG 2.1 AA compliance
- [ ] T082 Run comprehensive validation script to check all requirements
- [ ] T083 [P] Ensure mobile responsiveness of the textbook
- [ ] T084 [P] Clean up formatting and ensure consistency across all content
- [ ] T085 Run `npm run build` to ensure successful build
- [ ] T087 [P] Run quickstart.md validation
- [ ] T088 Create GitHub repo link documentation
- [ ] T089 Create Vercel live link documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with previous stories but should be independently testable

### Within Each User Story

- Content implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Content creation within each module can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence