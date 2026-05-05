export type DocumentDTO = {
  id: number;
  name: string;
  byte_size: number;
  created_at: string;
};

export type IngestResponse = {
  document: DocumentDTO;
  chunks: number;
};

export type RetrievedChunk = {
  chunk_id: number;
  document_id: number;
  ord: number;
  text: string;
  score: number;
};

export type MethodResult = {
  method: string;
  latency_ms: number;
  build_ms: number;
  index_size_bytes: number;
  n_items: number;
  chunks: RetrievedChunk[];
  answer: string | null;
};

export type QueryResponse = {
  question: string;
  top_k: number;
  results: MethodResult[];
};

export type EvalMethodMetrics = {
  method: string;
  recall_at_5: number;
  recall_at_10: number;
  mrr: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  build_ms: number;
  index_size_bytes: number;
};

export type EvalRunDTO = {
  id: number;
  corpus_size: number;
  created_at: string;
  methods: EvalMethodMetrics[];
};
