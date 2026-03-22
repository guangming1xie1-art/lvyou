import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { User, UserRequest, UserQueryParams, PageResponse } from '@/types';
import {
  getUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser
} from '@/api/user';

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([]);
  const total = ref(0);
  const currentUser = ref<User | null>(null);
  const loading = ref(false);

  // Actions
  async function fetchUsers(params: UserQueryParams = {}) {
    loading.value = true;
    try {
      const response: PageResponse<User> = await getUsers(params);
      users.value = response.content;
      total.value = response.totalElements;
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUser(id: number) {
    loading.value = true;
    try {
      const user = await getUser(id);
      currentUser.value = user;
      return user;
    } finally {
      loading.value = false;
    }
  }

  async function create(userData: UserRequest) {
    loading.value = true;
    try {
      const user = await createUser(userData);
      return user;
    } finally {
      loading.value = false;
    }
  }

  async function update(id: number, userData: UserRequest) {
    loading.value = true;
    try {
      const user = await updateUser(id, userData);
      return user;
    } finally {
      loading.value = false;
    }
  }

  async function remove(id: number) {
    loading.value = true;
    try {
      await deleteUser(id);
      users.value = users.value.filter(u => u.id !== id);
    } finally {
      loading.value = false;
    }
  }

  return {
    users,
    total,
    currentUser,
    loading,
    fetchUsers,
    fetchUser,
    create,
    update,
    remove
  };
});
