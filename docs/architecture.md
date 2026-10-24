# Architecture

Provena answers questions from a document collection and **proves** each answer:
every claim in the response is checked against a specific source span before it is returned.

## Request flow (target)

1. **Plan:** the query planner splits the question into sub-questions.
2. **Retrieve:** each sub-question runs against several retrievers in parallel:
   dense vectors (Qdrant), BM25 keyword, late interaction, and the knowledge graph.
3. **Fuse and rerank:** Reciprocal Rank Fusion, then a cross-encoder reranker.
4. **Generate:** the model answers using only the retrieved passages.
5. **Verify:** each claim is matched to the span that supports it. Unsupported claims
   trigger another retrieval round (bounded) or are dropped and reported.
6. **Respond:** the answer, plus span-level citations built from stored metadata.

## Code layout

```text
src/provena/
├── __main__.py      # `provena` command: runs the API server
├── config.py        # typed settings (PROVENA_* environment variables)
├── logs.py          # console / JSON logging with request-ID correlation
├── probes.py        # readiness checks for external services
└── api/
    ├── app.py       # FastAPI application factory
    ├── middleware.py # request IDs and access logging
    ├── errors.py    # uniform {"error": {...}} responses
    └── health.py    # /health and /ready
```

New subsystems (`ingest/`, `retrieve/`, `verify/`, ...) are added as sibling packages.
Each one sits behind a small protocol so that backends can be swapped and faked in tests.

## Principles

- **Evidence before eloquence.** An answer with no supporting span is not returned as fact.
- **Citations come from metadata, never from the model.**
- **Every feature ships with tests and an evaluation case.** CI blocks quality regressions.
- **Dependencies are optional at the edges.** Heavy models and services live behind
  interfaces, so the core runs and tests without a GPU or network.

## Operational endpoints

| Endpoint  | Purpose | Touches dependencies |
|-----------|---------|----------------------|
| `/health` | Liveness: the process is running | No |
| `/ready`  | Readiness: every probe passes, else HTTP 503 | Yes |

Every response carries an `X-Request-ID` header. A caller-supplied ID is reused if it is
safe (1–128 characters of `A-Z a-z 0-9 . _ -`), otherwise a new one is generated.
