import request from './request';
import type {
  Prompt,
  PromptRequest,
  PromptQueryParams,
  PromptTestRequest,
  PromptTestResponse,
  PageResponse
} from '@/types';

export function getPrompts(params: PromptQueryParams = {}): Promise<PageResponse<Prompt>> {
  return request.get('/admin/prompts', { params });
}

export function getActivePrompts(): Promise<Prompt[]> {
  return request.get('/admin/prompts/active');
}

export function getPrompt(id: string): Promise<Prompt> {
  return request.get(`/admin/prompts/${id}`);
}

export function createPrompt(data: PromptRequest): Promise<Prompt> {
  return request.post('/admin/prompts', data);
}

export function updatePrompt(id: string, data: PromptRequest): Promise<Prompt> {
  return request.put(`/admin/prompts/${id}`, data);
}

export function deletePrompt(id: string): Promise<void> {
  return request.delete(`/admin/prompts/${id}`);
}

export function testPrompt(id: string, data: PromptTestRequest): Promise<PromptTestResponse> {
  return request.post(`/admin/prompts/${id}/test`, data);
}
