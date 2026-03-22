import request from './request';
import type {
  RagDocument,
  RagDocumentRequest,
  RagQueryParams,
  RagSyncRequest,
  RagSyncResponse,
  SplitPreviewRequest,
  SplitPreviewResponse,
  DashboardStats,
  PageResponse
} from '@/types';

export function getDocuments(params: RagQueryParams = {}): Promise<PageResponse<RagDocument>> {
  return request.get('/admin/rag/documents', { params });
}

export function getDocument(id: string): Promise<RagDocument> {
  return request.get(`/admin/rag/documents/${id}`);
}

export function createDocument(data: RagDocumentRequest): Promise<RagDocument> {
  return request.post('/admin/rag/documents', data);
}

export function updateDocument(id: string, data: RagDocumentRequest): Promise<RagDocument> {
  return request.put(`/admin/rag/documents/${id}`, data);
}

export function deleteDocument(id: string): Promise<void> {
  return request.delete(`/admin/rag/documents/${id}`);
}

export function syncDocuments(documentIds?: string[]): Promise<RagSyncResponse> {
  const data: RagSyncRequest = documentIds ? { documentIds } : {};
  return request.post('/admin/rag/sync', data);
}

export function previewSplit(
  documents: { content: string; metadata?: Record<string, any> }[],
  chunkSize?: number,
  chunkOverlap?: number
): Promise<SplitPreviewResponse> {
  const data: SplitPreviewRequest = {
    documents,
    chunkSize,
    chunkOverlap
  };
  return request.post('/admin/rag/split/preview', data);
}

export function getDashboardStats(): Promise<DashboardStats> {
  return request.get('/admin/dashboard/stats');
}
