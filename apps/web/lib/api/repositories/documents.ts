import { request } from "@/lib/api/client";
import type { DocumentDTO, IngestResponse } from "@/lib/types";

export const documentsRepo = {
  async list(): Promise<DocumentDTO[]> {
    return request<DocumentDTO[]>("/v1/documents");
  },

  async upload(file: File, name?: string): Promise<IngestResponse> {
    const fd = new FormData();
    fd.append("file", file);
    if (name) fd.append("name", name);
    return request<IngestResponse>("/v1/documents", {
      method: "POST",
      formData: fd,
    });
  },
};
