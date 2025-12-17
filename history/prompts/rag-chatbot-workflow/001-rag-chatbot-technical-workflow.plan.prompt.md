---
id: 001
title: RAG Chatbot Technical Workflow
stage: plan
date: 2025-12-16
surface: agent
model: Claude Sonnet 4.5
feature: rag-chatbot-workflow
branch: 001-rag-chatbot-workflow
user: aamir
command: /sp.plan
labels: [rag, chatbot, workflow, architecture, docusaurus]
links:
  spec: /specs/001-rag-chatbot-workflow/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - /specs/001-rag-chatbot-workflow/plan.md
 - /specs/001-rag-chatbot-workflow/research.md
 - /specs/001-rag-chatbot-workflow/data-model.md
 - /specs/001-rag-chatbot-workflow/quickstart.md
 - /specs/001-rag-chatbot-workflow/contracts/api-contracts.md
 - /CLAUDE.md
tests:
 - /specs/001-rag-chatbot-workflow/research.md
 - /specs/001-rag-chatbot-workflow/data-model.md
---

## Prompt

Chatbot Technical Workflow Plan for SpecKitPlus Docusaurus Book

Create:
- High-level architecture flow for the complete RAG chatbot system
- Clear definition of a root-level backend workspace
- Layer-wise responsibility mapping for all RAG components
- End-to-end data flow from documentation ingestion to chatbot response
- Validation checkpoints to ensure a clean, error-free workflow

Backend workspace structure (conceptual):
- A single root-level `backend/` folder will exist
- All RAG-related workflows, services, and logic will operate inside this backend boundary
- Frontend (Docusaurus) remains fully decoupled and only consumes the chatbot interface

Core workflow definition (conceptual):
- Documentation content ingestion pipeline runs inside the backend
- Ingestion pipeline responsibilities:
  - Read and normalize Docusaurus content
  - Chunk content for semantic retrieval
  - Pass prepared content to embedding layer
- Embedding layer uses Cohere to generate vector representations
- Vector data is stored and queried via Qdrant
- User query follows the same embedding and retrieval path
- RAG retrieval layer selects relevant context from Qdrant
- Agent layer (Agent SDK with Gemini-compatible API) reasons over retrieved context
- FastAPI acts as the orchestration and interface layer
- Neon PostgreSQL stores application state, chat history, and metadata
- ChatKit UI communicates with the backend API
- Chatbot UI is embedded into or called from the Docusaurus book frontend

Decisions needing documentation:
- Why ingestion is a backend responsibility
- Separation between vector data (Qdrant) and relational state (PostgreSQL)
- Agent responsibility boundaries vs retrieval logic
- Backend-first design instead of frontend-driven RAG
- Integration boundary between ChatKit UI and Docusaurus

Validation strategy:
- Ingestion, retrieval, reasoning, and UI are clearly separated
- Backend acts as the single source of truth for RAG behavior
- No component performs multiple conflicting responsibilities
- Workflow is understandable without implementation or setup details
- Architecture supports future scaling without redesign

Constraints:
- No installation steps
- No code or configuration
- No deployment or infrastructure details
- Technical workflow planning only

## Response snapshot

Created a comprehensive technical workflow plan for the RAG chatbot system including:

1. **Technical Context**: Defined language versions, dependencies, storage systems, and performance goals
2. **Constitution Check**: Verified compliance with project constitution across all requirements
3. **Project Structure**: Outlined backend architecture with clear separation of concerns
4. **Research Summary**: Documented key architectural decisions and their rationale
5. **Data Model**: Defined entities for BookContent, UserQuery, RetrievedContext, ConversationSession, GeneratedResponse, and ContentChunk
6. **API Contracts**: Specified endpoints for chat, content ingestion, conversation history, and health checks
7. **Quickstart Guide**: Provided overview of system components and usage examples
8. **Agent Context Update**: Updated CLAUDE.md with new technology stack information

The plan establishes a clear backend-first architecture with proper separation between vector data (Qdrant) and relational state (PostgreSQL), with all RAG operations handled server-side for security and performance.

## Outcome

- ✅ Impact: Comprehensive RAG chatbot workflow plan created with all required components
- 🧪 Tests: Data models and API contracts validated against requirements
- 📁 Files: Multiple planning artifacts generated (plan.md, research.md, data-model.md, api-contracts.md)
- 🔁 Next prompts: Ready to proceed with implementation tasks
- 🧠 Reflection: Architecture properly separates concerns with backend handling all RAG operations

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementation with content ingestion pipeline