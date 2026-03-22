// RAG文档相关类型定义

export interface RagDocument {
  id: string;
  entityType: string;
  entityId: string;
  content: string;
  contentHash: string;
  source: string;
  docType: string;
  chunkCount: number;
  metadata: Record<string, any>;
  status: 'PENDING' | 'SYNCED' | 'FAILED' | 'PROCESSING';
  errorMessage?: string;
  lastSyncTime?: string;
  createdAt: string;
  updatedAt: string;
}

export interface RagDocumentRequest {
  entityType: string;
  entityId: string;
  content: string;
  source: string;
  docType?: string;
  metadata?: Record<string, any>;
}

export interface RagSyncRequest {
  documentIds?: string[];
  autoSplit?: boolean;
  chunkSize?: number;
  chunkOverlap?: number;
}

export interface RagSyncResponse {
  status: string;
  message: string;
  syncedCount: number;
  failedCount: number;
}

export interface SplitPreviewRequest {
  documents: {
    content: string;
    metadata?: Record<string, any>;
  }[];
  chunkSize?: number;
  chunkOverlap?: number;
  docType?: string;
}

export interface SplitPreviewResponse {
  status: string;
  originalCount: number;
  chunkCount: number;
  chunks: {
    content: string;
    metadata: Record<string, any>;
  }[];
}

export interface RagQueryParams {
  page?: number;
  size?: number;
  status?: string;
  entityType?: string;
}

export interface DashboardStats {
  userCount: number;
  documentCount: number;
  syncedCount: number;
  pendingCount: number;
  failedCount: number;
  todayActiveUsers: number;
  todayApiCalls: number;
  services: {
    name: string;
    status: string;
    instances: number;
  }[];
}

export const ENTITY_TYPES = [
  { label: '目的地', value: 'destination' },
  { label: '攻略', value: 'guide' },
  { label: '问答', value: 'qa' },
  { label: '评价', value: 'review' },
  { label: '政策', value: 'policy' }
];

export const DOC_TYPES = [
  { label: '旅游攻略', value: 'travel_guide' },
  { label: '问答对', value: 'qa' },
  { label: '用户评价', value: 'review' },
  { label: '政策文档', value: 'policy' },
  { label: '默认', value: 'default' }
];

export const SYNC_STATUS = [
  { label: '待同步', value: 'PENDING', color: 'warning' },
  { label: '已同步', value: 'SYNCED', color: 'success' },
  { label: '同步失败', value: 'FAILED', color: 'danger' },
  { label: '处理中', value: 'PROCESSING', color: 'primary' }
];
