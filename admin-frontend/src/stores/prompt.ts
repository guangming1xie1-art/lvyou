import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Prompt, PromptRequest, PromptQueryParams, PageResponse } from '@/types';
import {
  getPrompts,
  getPrompt,
  createPrompt,
  updatePrompt,
  deletePrompt,
  testPrompt
} from '@/api/prompt';

export const usePromptStore = defineStore('prompt', () => {
  // State
  const prompts = ref<Prompt[]>([]);
  const total = ref(0);
  const currentPrompt = ref<Prompt | null>(null);
  const loading = ref(false);

  // Actions
  async function fetchPrompts(params: PromptQueryParams = {}) {
    loading.value = true;
    try {
      const response: PageResponse<Prompt> = await getPrompts(params);
      prompts.value = response.content;
      total.value = response.totalElements;
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPrompt(id: string) {
    loading.value = true;
    try {
      const prompt = await getPrompt(id);
      currentPrompt.value = prompt;
      return prompt;
    } finally {
      loading.value = false;
    }
  }

  async function create(promptData: PromptRequest) {
    loading.value = true;
    try {
      const prompt = await createPrompt(promptData);
      return prompt;
    } finally {
      loading.value = false;
    }
  }

  async function update(id: string, promptData: PromptRequest) {
    loading.value = true;
    try {
      const prompt = await updatePrompt(id, promptData);
      return prompt;
    } finally {
      loading.value = false;
    }
  }

  async function remove(id: string) {
    loading.value = true;
    try {
      await deletePrompt(id);
      prompts.value = prompts.value.filter(p => p.id !== id);
    } finally {
      loading.value = false;
    }
  }

  async function test(id: string, variables: Record<string, any>) {
    loading.value = true;
    try {
      const result = await testPrompt(id, variables);
      return result;
    } finally {
      loading.value = false;
    }
  }

  return {
    prompts,
    total,
    currentPrompt,
    loading,
    fetchPrompts,
    fetchPrompt,
    create,
    update,
    remove,
    test
  };
});
