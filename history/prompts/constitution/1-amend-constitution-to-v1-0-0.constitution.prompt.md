---
id: 1
title: amend-constitution-to-v1-0-0
stage: constitution
date: 2025-12-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: claude
command: /sp.constitution
labels: [constitution, governance, project-setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

i am giving you a document read this and generate the best constitution for this project "# Project Constitution: Physical AI & Humanoid Robotics Textbook

## Project Identity

**Project Name**: Physical AI & Humanoid Robotics Interactive Textbook
**Project Type**: AI-Enhanced Educational Platform
**Primary Goal**: Create a comprehensive, adaptive, and intelligent digital textbook for teaching Physical AI and Humanoid Robotics that provides personalized learning experiences through advanced AI capabilities.

## Core Principles

### 1. Educational Excellence
- Content must be accurate, comprehensive, and pedagogically sound
- Complex concepts should be broken down into digestible sections
- Progressive difficulty curve from fundamentals to advanced topics
- Real-world examples and practical applications emphasized

### 2. Accessibility & Inclusivity
- Multi-language support (English and Urdu) for broader reach
- Content personalization based on user background and skill level
- Responsive design for desktop, tablet, and mobile devices
- Clear navigation and intuitive user interface

### 3. AI-First Development
- Leverage Claude Code and Spec-Kit Plus for content generation
- Use AI agents and subagents for reusable intelligence
- Implement RAG chatbot for interactive learning assistance
- Employ Gemini API for natural language understanding and generation

### 4. Open & Transparent
- Open source deployment on GitHub Pages
- Clear documentation of architecture and implementation
- MIT License principles followed where applicable
- Community-driven improvements encouraged

### 5. Privacy & Security
- User data protected with industry-standard practices
- Authentication handled securely through Better Auth
- No unnecessary data collection
- Transparent data usage policies

## Technical Mandates

### Architecture Standards

**Frontend Requirements**:
- Docusaurus as the primary framework
- TypeScript for type safety
- React for interactive components
- Responsive design with mobile-first approach
- Artifacts embedded where appropriate

**Backend Requirements**:
- FastAPI as the API framework
- Python 3.10+ for backend services
- RESTful API design principles
- Async/await for performance
- Proper error handling and logging

**Database Requirements**:
- Neon Serverless Postgres for relational data
- Qdrant Cloud for vector storage
- Efficient indexing strategies
- Regular backups and data integrity checks

**AI Integration Requirements**:
- Google Gemini API as primary LLM
- OpenAI SDK configured for Gemini compatibility
- Google text-embedding-004 for embeddings
- Rate limiting and cost optimization
- Caching strategies for repeated queries

### Code Quality Standards

**All code must adhere to**:
- PEP 8 for Python code
- ESLint/Prettier for TypeScript/JavaScript
- Meaningful variable and function names
- Comprehensive tates and error handling

**Implementation Constraints**:
- Response time < 3 seconds for 90% of queries
- Accurate retrieval from vector database
- Maximum context window of 8K tokens
- Graceful degradation if API fails

#### 3. Deployment
- **Must Have**:
  - GitHub Pages for frontend
  - Continuous deployment via GitHub Actions
  - Environment-based configuration
  - SSL/HTTPS enabled
  - CDN for static assets

### Advanced Features (Enhanced Experience)

#### 1. Claude Code Intelligence
- **Guidelines**:
  - Create minimum 3 reusable subagents
  - Document each subagent's purpose and usage
  - Implement at least 5 agent skills
  - Skills should be modular and composable
  - Store in `/docs/claude-intelligence/` directory

**Recommended Subagents**:
- Content Generator Subagent
- Code Example Validator
- Quiz Generator
- Concept Explainer

#### 2. Authentication System (Better Auth)
- **Requirements**:
  - Email/password authentication
  - Secure password hashing (bcrypt/argon2)
  - JWT token-based sessions
  - Password reset functionality
  - Email verification (optional but recommended)

**User Profile Collection**:
- Software background questionnaire (5-7 questions)
- Hardware background questionnaire (Urdu Translation
- **Requirements**:
  - "Translate to Urdu" toggle on each chapter
  - High-quality translation using Gemini API
  - Preserve technical terms in English
  - Keep code blocks untranslated
  - Maintain formatting and structure

**RTL Support**:
- Proper text direction for Urdu
- UI elements adjusted for RTL
- Maintain readability and aesthetics

**Optimization**:
- Cache translations in database
- Progressive translation (translate as user scrolls)
- Option to download translated chapter as PDF

## Development Process

### Phase-Based Development

**Phase 1: Foundation**
- Set up repositories and development environment
- Initialize Docusaurus project
- Configure Spec-Kit Plus integration
- Create basic book structure and outline
- Deploy initial version to GitHub Pages

**Phase 2: Core Content**
- Write chapters using Claude Code
- Add diagrams and visualizations
- Include code examples and exercises
- Implement search functionality
- Add table of contents and navigation

**Phase 3: RAG Integration**
- Set up FastAPI backend
- Configure Neon Postgres and Qdrant
- Implement embedding pipeline for content
- Build chatbot API endpoints
- Create frontend chatbot widget
- Embed in Docusaurus

**Phase 4: User Management**
- Integrate Better Auth
- Design signup/signin flows
- Create profile questionnaire UI
- Implement profile storage
- Add authentication middleware

**Phase 5: Intelligence Layer**
- Create Claude Code subagents
- Develop reusable agent skills
- Document agent architecture
- Implement content generation workflows

**Phase 6: Personalization**
- Build personalization API
- Implement content adaptation logic
- Add "Personalize" button to chapters
- Test with different user profiles

**Phase 7: Localization**
- Integrate translation API
- Implement Urdu translation
- Add RTL support
- Create language toggle UI
- Test translations for accuracy

**Phase 8: Testing & Optimization**
- Comprehensive testing of all features
- Performance optimization
- Bug fixes and refinements
- Documentation completion
- User acceptance testing

### Git Workflow

**Branch Strategy**:
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Individual features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Emergency fixes

**Commit Standards**:
- Use conventional commits format
- Examples:
  - `feat: add Urdu translation feature`
  - `fix: resolve chatbot timeout issue`
  - `docs: update API documentation`
  - `refactor: optimize vector search query`

**Code Review Process**:
- All code must be reviewed before merging
- Minimum 1 approval required
- Address all review comments
- Ensure tests pass before merge

### Continuous Integration/Deployment

**CI/CD Pipeline**:
- Automated testing on pull requests
- Build verification for Docusaurus
- Deploy to staging on `develop` merge
- Deploy to production on `main` merge
- Automatet sanitization)
- CORS configuration

**DUtilization

**Services on Free Tier**:
- GitHub Pages (unlimited for publi
**Quarterly**:
- Major feature additions
- Comprehensive security audit
- Userished on GitHub Pages
- [x] Comprehensive course content on s

**Technical Decisions**:
- Difeatures
- Achieve 1000+ registered users
- Gather user feedback and iterate
- Add 5+ more ucation, one intelligent page at a time."*

## Response snapshot

I've successfully created a comprehensive constitution for the Physical AI & Humanoid Robotics Interactive Textbook project. The constitution includes:

- **Educational Excellence**: Content must be accurate, comprehensive, and pedagogically sound with progressive difficulty
- **Accessibility & Inclusivity**: Multi-language support (English and Urdu), content personalization, responsive design
- **AI-First Development**: Leverage Claude Code and Spec-Kit Plus, implement RAG chatbot, use Gemini API
- **Open & Transparent**: Open source deployment, clear documentation, community-driven improvements
- **Privacy & Security**: Industry-standard practices, secure authentication, transparent data usage
- **Technical Excellence**: Code quality standards, performance constraints, error handling

The constitution also defines architecture standards for frontend (Docusaurus, TypeScript), backend (FastAPI, Python), databases (Neon Postgres, Qdrant), and AI integration (Gemini API). It outlines the development process with 8 phases from Foundation to Testing & Optimization.

The constitution has been written to `.specify/memory/constitution.md` with version 1.0.0, ratified on 2025-12-09.

## Outcome

- ✅ Impact: Created comprehensive project constitution with 6 core principles and technical mandates
- 🧪 Tests: No tests required for constitution creation
- 📁 Files: Updated .specify/memory/constitution.md with complete constitution
- 🔁 Next prompts: Project can now proceed with spec-driven development using new constitution
- 🧠 Reflection: Constitution provides clear governance framework for the AI-enhanced educational platform project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A