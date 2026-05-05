import { request } from "@/lib/api/client";
import type { QueryResponse } from "@/lib/types";

export type QueryInput = {
  question: string;
  top_k: number;
  methods?: string[];
  synthesize_answer: boolean;
};

export const queryRepo = {
  async run(input: QueryInput): Promise<QueryResponse> {
    return request<QueryResponse>("/v1/query", {
      method: "POST",
      body: input,
    });
  },
};
