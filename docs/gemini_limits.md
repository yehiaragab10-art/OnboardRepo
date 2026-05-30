# Gemini Models for OnboardRepo

Last Updated: May 2026

## Development & Testing Ranking

Use these while building and debugging the system.

### 1. Gemini 3.1 Flash Lite

Best choice for development because of the large daily quota.

| Metric | Limit |
|----------|----------|
| RPM | 15 |
| TPM | 250,000 |
| RPD | 500 |

**Use for:**
- RAG pipeline testing
- Agent testing
- Prompt iteration
- Graph retrieval testing
- Integration testing
- Evaluation runs
- Debugging

**Why #1?**

500 requests/day is dramatically more useful during development than a slightly better model with only 20 requests/day.

---

### 2. Gemini 2.5 Flash Lite

| Metric | Limit |
|----------|----------|
| RPM | 10 |
| TPM | 250,000 |
| RPD | 20 |

**Use for:**
- Lightweight testing
- Simple summaries
- Backup development model

---

### 3. Gemini 2.5 Flash

| Metric | Limit |
|----------|----------|
| RPM | 5 |
| TPM | 250,000 |
| RPD | 20 |

**Use for:**
- Final evaluation
- Quality benchmarking
- Planner validation
- Demo preparation

---

### 4. Gemini 3 Flash

| Metric | Limit |
|----------|----------|
| RPM | 5 |
| TPM | 250,000 |
| RPD | 20 |

**Use for:**
- Fallback testing
- Comparative evaluation

---

### 5. Gemini 3.5 Flash

| Metric | Limit |
|----------|----------|
| RPM | 5 |
| TPM | 250,000 |
| RPD | 20 |

**Use for:**
- Comparative evaluation
- Final benchmarking

---

# Production Quality Ranking

If quotas were ignored and only answer quality mattered.

### 1. Gemini 2.5 Flash
Best overall reasoning and code understanding.

### 2. Gemini 3.5 Flash
Strong reasoning and architecture discussions.

### 3. Gemini 3 Flash
Good balance of speed and quality.

### 4. Gemini 3.1 Flash Lite
Good enough for many RAG tasks.

### 5. Gemini 2.5 Flash Lite
Primarily useful when cost or quotas are the main concern.

---

# Recommended OnboardRepo Setup

## Development Phase

Primary Model:
- Gemini 3.1 Flash Lite

Reason:
- 500 requests/day
- Fast iteration
- Enough quality for testing retrieval and agents

## Evaluation Phase

Primary Model:
- Gemini 2.5 Flash

Reason:
- Better reasoning
- Better repository understanding
- Better planner performance

## Final Demonstration

Primary Model:
- Gemini 2.5 Flash

Fallback:
- Gemini 3 Flash

Reason:
- Highest quality answers for showcasing the system