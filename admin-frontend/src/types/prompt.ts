// 提示词相关类型定义

export interface Prompt {
  id: string;
  name: string;
  category: string;
  content: string;
  variables: string[];
  description?: string;
  version: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PromptRequest {
  name: string;
  category: string;
  content: string;
  variables?: string[];
  description?: string;
  version?: string;
  isActive?: boolean;
}

export interface PromptTestRequest {
  variables: Record<string, any>;
}

export interface PromptTestResponse {
  renderedPrompt: string;
  result: string;
}

export interface PromptQueryParams {
  page?: number;
  size?: number;
  category?: string;
}

export const PROMPT_CATEGORIES = [
  { label: '查询重写', value: 'query_rewrite' },
  { label: '记忆管理', value: 'memory_management' },
  { label: 'RAG检索', value: 'rag_retrieval' },
  { label: '对话生成', value: 'response_generation' },
  { label: '意图识别', value: 'intent_recognition' },
  { label: '其他', value: 'other' }
];
