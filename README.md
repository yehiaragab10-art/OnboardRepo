![CI](https://github.com/yehiaragab10-art/onboardrepo/actions/workflows/ci.yml/badge.svg)
# OnboardRepo

OnboardRepo is a local-first AI codebase onboarding assistant. It is a command-line application that indexes a local Git repository, including both its source code and documentation. It exposes this index through a multi-agent LangGraph runtime to answer questions or guide engineers through structured onboarding journeys directly from the terminal.

Designed to accelerate the time-to-productivity for new hires, OnboardRepo combines the curated structure of a senior-engineer-led code tour with the always-available responsiveness of an AI assistant.

## Key Features

* **Strictly Local-First & Secure**: All code, documents, embeddings, and conversation data remain entirely on the user's machine. The only network egress is to an explicitly configured LLM provider, ensuring enterprise-grade security for proprietary code.
* **Provider-Agnostic LLM Routing**: Users can seamlessly choose between OpenAI, Anthropic, Gemini, or a local Ollama model. Conversations can even continue uninterrupted if the provider is switched mid-session.
* **Hybrid Mixed-Corpus RAG**: The system treats code and documentation as distinct corpora feeding into a unified retriever. 
  * **Code**: Processed via AST-aware chunking (using `tree-sitter` and the cAST algorithm) to preserve syntactic boundaries, alongside LLM-generated summary embeddings and a deterministic symbol graph.
  * **Documents**: Processed via structural, heading-based chunking (e.g., Markdown, reStructuredText) for direct dense embedding.
* **Structured Onboarding Journeys**: Tech leads can author onboarding journeys as YAML files committed alongside the repository. This allows the onboarding path to live and evolve directly with the code.
* **Adaptive Mentee Modeling**: OnboardRepo utilizes a lightweight, interpretable Bayesian Knowledge Tracing (BKT) model to track what the user knows. By modeling the user's "Knowledge Components" (KCs), the system calibrates the difficulty of AI probes, questions, and explanations to maximize learning.
* **Multi-Tiered Memory**: The system features a sophisticated memory subsystem comprising working, episodic, semantic, and procedural tiers to remember facts about the user and context across sessions.

## Architecture Overview

OnboardRepo v1.0 is built as a single-process Python CLI to ensure simple installation and snappy performance. The application is built on a front-end-agnostic core library, enabling future expansion to a Tauri 2 desktop GUI.

**Core Stack:**
* **Frontend**: `Typer`, `Rich`, and `Textual` for terminal rendering and streaming.
* **Agent Orchestration**: A 5-agent `LangGraph` runtime governing planning, retrieval, and verification.
* **ML & Indexing Pipeline**:
  * `tree-sitter` for multi-language AST extraction (Python, TypeScript, JavaScript, Go).
  * `sentence-transformers` for local embedding generation.
  * `LanceDB` for fast vector and payload storage.
  * `rank-bm25` combined with an active reranker for lexical and hybrid search.
  * `SQLite` for local storage of memory states and symbol graphs.

## Developer Notes

### API Key Management

* Store all API keys exclusively in the `.env` file.
* The `.env` file is included in `.gitignore` and must never be committed to the repository.
* Do not hardcode API keys in source code, configuration files, tests, or documentation.

### Local Development


GEMINI_API_KEY=your_key_here


### GitHub Actions

For CI/CD workflows, configure the Gemini API key as a repository secret named:


GEMINI_API_KEY


The secret will be injected into workflows as an environment variable during execution.

## Getting Started

*(Setup instructions, installation commands, and complete documentation are coming soon.)*
