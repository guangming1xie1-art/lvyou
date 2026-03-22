import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  RagDocument,
  RagDocumentRequest,
  RagQueryParams,
  PageResponse,
  DashboardStats
} from '@/types';
import {
  getDocuments,
  getDocument,
  createDocument,
  updateDocument,
  deleteDocument,
  syncDocuments,
  previewSplit,
  getDashboardStats
} from '@/api/rag';

export const useRagStore = defineStore('rag', () => {
  // State
  const documents = ref<RagDocument[]>([]);
  const total = ref(0);
  const currentDocument = ref<RagDocument | null>(null);
  const dashboardStats = ref<DashboardStats | null>(null);
  const loading = ref(false);
  const splitPreview = ref<any>(null);

  // Actions
  async function fetchDocuments(params: RagQueryParams = {}) {
    loading.value = true;
    try {
      const response: PageResponse<RagDocument> = await getDocuments(params);
      documents.value = response.content;
      total.value = response.totalElements;
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDocument(id: string) {
    loading.value = true;
    try {
      const document = await getDocument(id);
      currentDocument.value = document;
      return document;
    } finally {
      loading.value = false;
    }
  }

  async function create(documentData: RagDocumentRequest) {
    loading.value = true;
    try {
      const document = await createDocument(documentData);
      return document;
    } finally {
      loading.value = false;
    }
  }

  async function update(id: string, documentData: RagDocumentRequest) {
    loading.value = true;
    try {
      const document = await updateDocument(id, documentData);
      return document;
    } finally {
      loading.value = false;
    }
  }

  async function remove(id: string) {
    loading.value = true;
    try {
      await deleteDocument(id);
      documents.value = documents.value.filter(d => d.id !== id);
    } finally {
      loading.value = false;
    }
  }

  async function sync(documentIds?: string[]) {
    loading.value = true;
    try {
      const result = await syncDocuments(documentIds);
      return result;
    } finally {
      loading.value = false;
    }
  }

  async function preview(documentContent: string, chunkSize?: number, chunkOverlap?: number) {
    loading.value = true;
    try {
      const result = await previewSplit([{ content: documentContent }], chunkSize, chunkOverlap);
      splitPreview.value = result;
      return result;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDashboardStats() {
    loading.value = true;
    try {
      const stats = await getDashboardStats();
      dashboardStats.value = stats;
      return stats;
    } finally {
      loading.value = false;
    }
  }

  return {
    documents,
    total,
    currentDocument,
    dashboardStats,
    splitPreview,
    loading,
    fetchDocuments,
    fetchDocument,
    create,
    update,
    remove,
    sync,
    preview,
    fetchDashboardStats
  };
});
