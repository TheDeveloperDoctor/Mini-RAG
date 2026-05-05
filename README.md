# Mini RAG (Done Properly)

A small, honest retrieval-augmented generation system built as a **comparison lab**: upload text, ask questions, and see four retrievers race head-to-head with real latency, real recall, and real receipts.

> Most portfolio RAGs ship as "look, it answers questions." This one ships as **"look at the tradeoffs."** The whole point is to make the cost of retrieval choices visible.

## What it does

- Upload `.txt` / `.md` files (or seed the Paul Graham essay corpus).
- Ask a question. The system runs the same query through **four retrievers in parallel**:
  1. **Naive cosine** — `numpy` loop over every chunk (exact, O(n))
  2. **FAISS Flat** — exact, SIMD-accelerated
  3. **FAISS IVF** — approximate nearest neighbour, tunable `nlist` / `nprobe`
  4. **Hybrid (BM25 + dense, RRF fusion)** — sparse + dense reranked
- Each retriever reports **latency, retrieved chunks, and similarity scores**.
- A latency chart accumulates per-query points across methods. Slide the corpus size from 100 → 50 000 chunks and watch the **crossover point** where naive collapses and FAISS pulls away.
- Every answer cites its sources. No hidden chunks, no vibes.

## Why it isn't boring

Three things separate this from a weekend tutorial:

1. **Comparison is the product**, not a footnote — the homepage is a side-by-side benchmark.
2. **An eval harness** (`make eval`) reports `Recall@5`, `Recall@10`, `MRR`, and `p50/p95` latency against a hand-written gold set. Numbers, not vibes.
3. **Local-only embeddings** (`bge-small-en-v1.5`) — no API key required to demo retrieval. Anthropic key is only needed for answer synthesis.

## Quickstart

```bash
cp .env.example .env
# (optional) put your ANTHROPIC_API_KEY in .env for answer synthesis
make install
make seed       # loads Paul Graham essays
make dev-api    # in one terminal
make dev-web    # in another
```

Open http://localhost:3000.

Or with Docker:

```bash
make docker-build
make docker-up
```

## Eval

```bash
make eval
```

Runs all retrievers against `apps/api/src/eval/gold.jsonl`. Writes JSON to `eval_results/` and prints a comparison table.

## Architecture

```
apps/
  api/           FastAPI + SQLite + FAISS + sentence-transformers
    src/
      api/         thin routers
      services/    ingestion, retrieval, answer, benchmark
      retrievers/  naive | faiss_flat | faiss_ivf | bm25 | hybrid
      chunking/    recursive char split with overlap
      embeddings/  bge-small wrapper
      repositories/ document, chunk, eval_run
      eval/        harness + gold set
      core/        config, logger, errors, db
    tests/         mirrors src/
  web/           Next.js + Tailwind + shadcn
    app/         comparison lab + eval results page
    components/  upload, query box, answer columns, latency chart
    lib/api/     repository pattern, no raw fetch in components
```

## Tradeoffs called out

- **`bge-small` over MiniLM** — slightly slower, meaningfully better retrieval.
- **FAISS IVF over HNSW** — IVF has the cleaner `nlist` / `nprobe` story to explain in a portfolio piece.
- **Synthetic corpus expansion for the slider** — chunks are duplicated and lightly perturbed to hit 50 k for the crossover demo. Honest about it in the UI.
- **No reranker in v1** — adds a model download and complicates the comparison story. Easy to bolt on as v2.

## Branching

See [`rules.md`](./rules.md). All work goes through `feat/*` branches into `dev`. `dev` is always green.

## License

MIT.
