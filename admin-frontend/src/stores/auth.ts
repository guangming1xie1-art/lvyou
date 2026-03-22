import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, LoginRequest, LoginResponse } from '@/types';
import { login as loginApi, getCurrentUser } from '@/api/auth';

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string>(localStorage.getItem('token') || '');
  const user = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.roles.includes('ADMIN') || false);

  // Actions
  async function login(credentials: LoginRequest) {
    loading.value = true;
    try {
      const response: LoginResponse = await loginApi(credentials);
      token.value = response.token;
      user.value = response.user;
      localStorage.setItem('token', response.token);
      return response;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return;
    try {
      const userInfo = await getCurrentUser();
      user.value = userInfo;
    } catch (error) {
      logout();
    }
  }

  function logout() {
    token.value = '';
    user.value = null;
    localStorage.removeItem('token');
  }

  function setToken(newToken: string) {
    token.value = newToken;
    localStorage.setItem('token', newToken);
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    isAdmin,
    login,
    fetchUserInfo,
    logout,
    setToken
  };
});
