<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0
Modified principles: None (new constitution)
Added sections: All principles and sections added
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ✅ updated
Follow-up TODOs: None
-->
# Physical AI & Humanoid Robotics Interactive Textbook Constitution

## Core Principles

### Educational Excellence
Content must be accurate, comprehensive, and pedagogically sound. Complex concepts should be broken down into digestible sections. Progressive difficulty curve from fundamentals to advanced topics. Real-world examples and practical applications emphasized.

### Accessibility & Inclusivity
Multi-language support (English and Urdu) for broader reach. Content personalization based on user background and skill level. Responsive design for desktop, tablet, and mobile devices. Clear navigation and intuitive user interface.

### AI-First Development
Leverage Claude Code and Spec-Kit Plus for content generation. Use AI agents and subagents for reusable intelligence. Implement RAG chatbot for interactive learning assistance. Employ Gemini API for natural language understanding and generation.

### Open & Transparent
Open source deployment on GitHub Pages. Clear documentation of architecture and implementation. MIT License principles followed where applicable. Community-driven improvements encouraged.

### Privacy & Security
User data protected with industry-standard practices. Authentication handled securely through Better Auth. No unnecessary data collection. Transparent data usage policies.

### Technical Excellence
All code must adhere to PEP 8 for Python code, ESLint/Prettier for TypeScript/JavaScript, meaningful variable and function names, comprehensive tests and error handling. Implementation constraints: Response time < 3 seconds for 90% of queries, accurate retrieval from vector database, maximum context window of 8K tokens, graceful degradation if API fails.

## Architecture Standards and Technical Mandates

Frontend Requirements: Docusaurus as the primary framework, TypeScript for type safety, React for interactive components, responsive design with mobile-first approach. Backend Requirements: FastAPI as the API framework, Python 3.10+ for backend services, RESTful API design principles, Async/await for performance, Proper error handling and logging. Database Requirements: Neon Serverless Postgres for relational data, Qdrant Cloud for vector storage, efficient indexing strategies, regular backups and data integrity checks. AI Integration Requirements: Google Gemini API as primary LLM, OpenAI SDK configured for Gemini compatibility, Google text-embedding-004 for embeddings, rate limiting and cost optimization, caching strategies for repeated queries.

## Development Process and Workflow

Phase-Based Development: Foundation (set up repos, Docusaurus, Spec-Kit Plus), Core Content (write chapters with Claude Code), RAG Integration (FastAPI, Neon Postgres, Qdrant), User Management (Better Auth), Intelligence Layer (Claude Code subagents), Personalization (content adaptation), Localization (Urdu translation), Testing & Optimization. Git Workflow: Use conventional commits format, code review with minimum 1 approval, automated testing on pull requests, continuous deployment via GitHub Actions.

## Governance

All code changes must follow the established architecture standards. Amendments require documentation and approval. All features must pass comprehensive testing before merging. User data privacy must be maintained at all times. AI-generated content must be verified for accuracy. Deployment follows a continuous integration pipeline with automated testing.

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09