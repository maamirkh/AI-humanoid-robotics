# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

# Physical AI & Humanoid Robotics Textbook Project

## Project Overview
Create a comprehensive, interactive digital textbook for teaching Physical AI and Humanoid Robotics, built with Docusaurus and enhanced with AI-powered features.

## Core Requirements

### 1. AI/Spec-Driven Book Creation
- **Framework**: Docusaurus
- **Development Tools**: 
  - Claude Code (https://www.claude.com/product/claude-code)
  - Spec-Kit Plus (https://github.com/panaversity/spec-kit-plus/)
- **Deployment**: GitHub Pages
- **Content Focus**: Physical AI and Humanoid Robotics curriculum

### 2. Integrated RAG Chatbot
Build and embed a fully functional RAG chatbot within the published textbook.

**Technology Stack**:
- **Backend Framework**: FastAPI
- **AI SDK**: OpenAI Agents/ChatKit SDKs (configured with Gemini API Key)
- **LLM Provider**: Google Gemini API
- **Vector Database**: Qdrant Cloud (Free Tier)
- **Relational Database**: Neon Serverless Postgres
- **Embedding Model**: Google text-embedding-004 or similar Gemini embedding model

**Core Features**:
- Answer questions about book content
- Context-aware responses based on selected text
- Real-time query processing
- Seamless integration within Docusaurus pages

**Implementation Requirements**:
- Index all book content in Qdrant vector database
- Implement semantic search for relevant content retrieval
- Use Google Gemini API (via OpenAI SDK configuration) for generating contextual answers
- Support user text selection for targeted Q&A
- Deploy chatbot API separately and embed in book via iframe/widget
- Configure OpenAI SDK to use Gemini API endpoint with Gemini API key

## Advanced Features

### Feature 1: Reusable Intelligence
Create and utilize reusable intelligence components via Claude Code.

**Requirements**:
- Develop **Claude Code Subagents** for specific tasks:
  - Content generation subagent
  - Code example validator
  - Diagram generator
  - Quiz/assessment creator
- Create **Agent Skills** that can be reused across book chapters:
  - Technical concept explainer
  - Code snippet optimizer
  - Terminology definer
  - Learning path recommender

**Deliverables**:
- Document all subagents and skills in `/docs/claude-intelligence/`
- Demonstrate reusability across multiple chapters
- Include usage examples and configuration guides

### Feature 2: Authentication System
Implement comprehensive user authentication using Better Auth.

**Technology**: Better Auth (https://www.better-auth.com/)

**Features**:
- **Signup Process**:
  - Collect user information:
    - Software background (programming languages, frameworks)
    - Hardware background (robotics experience, electronics knowledge)
    - Educational level
    - Learning goals
  - Store user profiles in Neon Postgres
  
- **Signin Process**:
  - Secure authentication
  - Session management
  - Profile retrieval

- **User Profile Schema**:
```typescript
interface UserProfile {
  id: string;
  email: string;
  name: string;
  softwareBackground: {
    programmingLanguages: string[];
    frameworks: string[];
    experienceLevel: 'beginner' | 'intermediate' | 'advanced';
  };
  hardwareBackground: {
    roboticsExperience: boolean;
    electronicsKnowledge: 'none' | 'basic' | 'intermediate' | 'advanced';
    hasBuiltRobot: boolean;
  };
  educationalLevel: string;
  learningGoals: string[];
  createdAt: Date;
}
```

### Feature 3: Personalized Content
Enable logged-in users to personalize chapter content based on their background.

**Requirements**:
- Add "Personalize Content" button at the start of each chapter
- Adjust content based on user's:
  - Software knowledge (show/hide code examples)
  - Hardware experience (adjust technical depth)
  - Learning goals (highlight relevant sections)

**Personalization Examples**:
- **Beginner Software**: Show detailed code explanations
- **Advanced Hardware**: Skip basic electronics, focus on advanced topics
- **Specific Goals**: Highlight content matching user's learning objectives

**Implementation**:
- Use Google Gemini API to regenerate content sections
- Store personalization preferences in user profile
- Cache personalized content for performance
- Provide "Reset to Default" option

### Feature 4: Urdu Translation
Allow logged-in users to translate chapter content to Urdu.

**Requirements**:
- Add "Translate to Urdu" button at the start of each chapter
- Real-time translation using OpenAI API
- Preserve formatting and technical terms
- Toggle between English and Urdu

**Technical Considerations**:
- Use Google Gemini API for high-quality translation
- Implement caching to reduce API costs
- Handle code blocks (keep untranslated)
- Preserve mathematical formulas and diagrams
- Right-to-left text support in UI

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           Docusaurus Frontend                    │
│  ┌──────────────────────────────────────────┐   │
│  │  Chapter Pages with:                     │   │
│  │  - Personalize Button                    │   │
│  │  - Translate Button                      │   │
│  │  - Embedded RAG Chatbot                  │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                     │
│  ┌──────────────────────────────────────────┐   │
│  │  - RAG Endpoints                         │   │
│  │  - Auth Endpoints (Better Auth)          │   │
│  │  - Personalization API                   │   │
│  │  - Translation API                       │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
          │              │              │
          ▼              ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌──────────┐
│   Qdrant    │  │    Neon      │  │  Google  │
│   Vector    │  │  Postgres    │  │  Gemini  │
│     DB      │  │   (User &    │  │   API    │
│  (Content)  │  │  Chat Data)  │  │          │
└─────────────┘  └──────────────┘  └──────────┘
```

## Development Workflow

### Phase 1: Book Structure
1. Set up Docusaurus project
2. Define book outline and chapters using Spec-Kit Plus
3. Create initial content with Claude Code
4. Deploy to GitHub Pages

### Phase 2: RAG Chatbot
1. Set up FastAPI backend
2. Configure Neon Postgres and Qdrant
3. Implement content indexing pipeline
4. Build chatbot API endpoints
5. Embed chatbot in Docusaurus

### Phase 3: Authentication
1. Integrate Better Auth
2. Create signup/signin UI
3. Design user profile questionnaire
4. Set up profile storage in Postgres

### Phase 4: Advanced Features
1. Implement content personalization
2. Add Urdu translation
3. Create Claude Code subagents
4. Document all agent skills

### Phase 5: Testing & Refinement
1. End-to-end testing
2. Performance optimization
3. Documentation completion
4. Final deployment

## Deliverables Checklist

### Core Deliverables
- [ ] Docusaurus book deployed on GitHub Pages
- [ ] Complete RAG chatbot integrated in book
- [ ] Text selection-based Q&A functionality
- [ ] FastAPI backend deployed
- [ ] Qdrant vector database configured
- [ ] Neon Postgres database set up
- [ ] Google Gemini API integrated via OpenAI SDK

### Advanced Features
- [ ] Claude Code subagents
- [ ] Agent skills documentation
- [ ] Better Auth integration
- [ ] User profile questionnaire
- [ ] Content personalization
- [ ] Urdu translation feature

## Technical Stack Summary

| Component | Technology |
|-----------|------------|
| Frontend Framework | Docusaurus |
| Backend Framework | FastAPI |
| Vector Database | Qdrant Cloud (Free) |
| Relational Database | Neon Serverless Postgres |
| AI/LLM | Google Gemini API (via OpenAI SDK) |
| Embeddings | Google text-embedding-004 |
| Authentication | Better Auth |
| AI Development | Claude Code + Spec-Kit Plus |
| Deployment | GitHub Pages (Frontend) + Cloud (Backend) |
| Languages | TypeScript, Python, React |

## API Configuration Notes

### Using Gemini API with OpenAI SDK

The OpenAI Agents/ChatKit SDK can be configured to use Google Gemini API as the backend. Here's how:

```python
# FastAPI backend configuration
from openai import OpenAI

# Configure OpenAI client to use Gemini
client = OpenAI(
    api_key="YOUR_GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# For embeddings
from google.generativeai import embed_content

# Use Gemini embedding models
embedding_response = embed_content(
    model="models/text-embedding-004",
    content="Your text here"
)
```

**Environment Variables Required**:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
NEON_DATABASE_URL=your_neon_postgres_url
```

## Scoring Breakdown

All features are important components of the complete textbook platform:

| Feature Category | Components |
|------------------|------------|
| Core Platform | Book + RAG Chatbot + Deployment |
| Intelligence Layer | Claude Code Subagents & Skills |
| User Management | Authentication & Profiles |
| Personalization | Content Adaptation |
| Localization | Urdu Translation |

## Getting Started

1. **Install Dependencies**:
```bash
npm install -g claude-code
git clone https://github.com/panaversity/spec-kit-plus/
```

2. **Initialize Project**:
```bash
npx create-docusaurus@latest physical-ai-textbook classic --typescript
cd physical-ai-textbook
```

3. **Set Up Backend**:
```bash
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn google-generativeai qdrant-client psycopg2-binary better-auth openai
```

4. **Configure API Keys**:
```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" >> .env
echo "QDRANT_URL=your_qdrant_url" >> .env
echo "QDRANT_API_KEY=your_qdrant_key" >> .env
echo "NEON_DATABASE_URL=your_neon_url" >> .env
```

5. **Follow Development Workflow** as outlined above.

## Resources

- [Spec-Kit Plus Documentation](https://github.com/panaversity/spec-kit-plus/)
- [Claude Code Product Page](https://www.claude.com/product/claude-code)
- [Docusaurus Documentation](https://docusaurus.io/)
- [Better Auth Documentation](https://www.better-auth.com/)
- [Qdrant Cloud](https://qdrant.tech/)
- [Neon Serverless Postgres](https://neon.tech/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [OpenAI SDK with Custom Endpoints](https://platform.openai.com/docs/api-reference)

---

**Project Goal**: Create an innovative, AI-enhanced educational platform that adapts to each learner's background and provides intelligent, context-aware assistance throughout their Physical AI and Humanoid Robotics learning journey.

## Active Technologies
- Markdown/MDX, Node.js 18+ + Docusaurus v3, Node.js, NPM (001-docusaurus-textbook)
- Files only (no database) (001-docusaurus-textbook)
- Python 3.11+ + fastapi, uvicorn, pydantic, python-dotenv, uv (package manager) (002-uv-backend-init)
- N/A (initial setup phase) (002-uv-backend-init)
- Python 3.11, TypeScript/JavaScript (Node.js 18+) + FastAPI, uvicorn, pydantic, Cohere, Qdrant, OpenAI Agent SDK, Neon PostgreSQL, Docusaurus (001-rag-chatbot-workflow)
- Vector database (Qdrant Cloud), Relational database (Neon PostgreSQL), File storage (Docusaurus content) (001-rag-chatbot-workflow)

## Recent Changes
- 001-docusaurus-textbook: Added Markdown/MDX, Node.js 18+ + Docusaurus v3, Node.js, NPM
