import { request } from "@/lib/api/client";
import type { EvalRunDTO } from "@/lib/types";

export const evalRepo = {
  async run(): Promise<EvalRunDTO> {
    return request<EvalRunDTO>("/v1/eval/run", { method: "POST" });
  },

  async latest(): Promise<EvalRunDTO | null> {
    return request<EvalRunDTO | null>("/v1/eval/latest");
  },

  async history(): Promise<EvalRunDTO[]> {
    return request<EvalRunDTO[]>("/v1/eval/history");
  },
};
