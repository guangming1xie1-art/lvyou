/**
 * Authentication Service
 * Handles user authentication, token management, and session persistence
 */

import type {
  User,
  TokenResponse,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
  AuthTokens,
  LoginResponse
} from '@/types/auth';

const API_BASE_URL = import.meta.env.VITE_AGENT_API_BASE_URL || 'http://localhost:8000';

class AuthService {
  private accessToken: string | null = null;
  private refreshTokenValue: string | null = null;
  private user: User | null = null;
  private tokenExpiry: number | null = null;
  private refreshPromise: Promise<void> | null = null;

  constructor() {
    this.loadFromStorage();
  }

  /**
   * Initialize the auth service with saved tokens
   */
  private loadFromStorage(): void {
    this.accessToken = sessionStorage.getItem('accessToken');
    this.refreshTokenValue = localStorage.getItem('refreshToken');
    this.tokenExpiry = parseInt(sessionStorage.getItem('tokenExpiry') || '0', 10);
    const userStr = sessionStorage.getItem('user');
    
    if (userStr) {
      try {
        this.user = JSON.parse(userStr);
      } catch {
        this.user = null;
      }
    }
  }

  /**
   * Save tokens to storage
   */
  private saveTokens(tokens: AuthTokens, user: User): void {
    this.accessToken = tokens.accessToken;
    this.refreshTokenValue = tokens.refreshToken;
    this.user = user;
    this.tokenExpiry = Date.now() + tokens.expiresIn * 1000;

    sessionStorage.setItem('accessToken', tokens.accessToken);
    localStorage.setItem('refreshToken', tokens.refreshToken);
    sessionStorage.setItem('user', JSON.stringify(user));
    sessionStorage.setItem('tokenExpiry', this.tokenExpiry.toString());
  }

  /**
   * Clear all tokens and user data
   */
  clearTokens(): void {
    this.accessToken = null;
    this.refreshTokenValue = null;
    this.user = null;
    this.tokenExpiry = null;

    sessionStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('tokenExpiry');
  }

  /**
   * Check if access token is valid (not expired)
   */
  private isAccessTokenValid(): boolean {
    if (!this.accessToken || !this.tokenExpiry) {
      return false;
    }
    // Add 30 second buffer
    return Date.now() < this.tokenExpiry - 30000;
  }

  /**
   * Register a new user
   */
  async register(username: string, email: string, password: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
        confirm_password: password,
      } as RegisterRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return await response.json();
  }

  /**
   * Login user
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password,
      } as LoginRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json() as LoginResponse;
    // const data = { user: { id: '1', username: 'test', email: 'test@example.com' }, tokens: { access_token: 'test', refresh_token: 'test', token_type: 'Bearer', expires_in: 3600 } } as LoginResponse;
    this.saveTokens(
      {
        accessToken: data.tokens.accessToken,
        refreshToken: data.tokens.refreshToken,
        expiresIn: data.tokens.expiresIn,
      },
      data.user
    );

    return data;
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<void> {
    // If a refresh is already in progress, return that promise
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this._performTokenRefresh();

    try {
      await this.refreshPromise;
    } finally {
      this.refreshPromise = null;
    }
  }

  /**
   * Perform the actual token refresh
   */
  private async _performTokenRefresh(): Promise<void> {
    if (!this.refreshTokenValue) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: this.refreshTokenValue,
      } as RefreshTokenRequest),
    });

    if (!response.ok) {
      this.clearTokens();
      throw new Error('Session expired. Please login again.');
    }

    const data = await response.json() as TokenResponse;
    
    this.saveTokens(
      {
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
        expiresIn: data.expiresIn,
      },
      this.user!
    );
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    if (!this.accessToken) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get user');
    }

    const user = await response.json() as User;
    this.user = user;
    return user;
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      if (this.accessToken) {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
          },
        });
      }
    } catch {
      // Ignore logout errors
    } finally {
      this.clearTokens();
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.user && !!this.accessToken && this.isAccessTokenValid();
  }

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return this.accessToken;
  }

  /**
   * Get current user
   */
  getUser(): User | null {
    return this.user;
  }

  /**
   * Get authorization header
   */
  getAuthHeader(): string | undefined {
    const token = this.getAccessToken();
    return token ? `Bearer ${token}` : undefined;
  }

  /**
   * Get tokens for API calls with automatic refresh
   */
  async getValidToken(): Promise<string> {
    if (this.isAccessTokenValid()) {
      return this.accessToken!;
    }

    if (this.refreshTokenValue) {
      await this.refreshToken();
      return this.accessToken!;
    }

    throw new Error('No valid token available');
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export axios interceptor setup
export const setupAxiosInterceptor = (axios: any): void => {
  axios.interceptors.request.use(
    async (config: any) => {
      const token = await authService.getValidToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: any) => Promise.reject(error)
  );

  axios.interceptors.response.use(
    (response: any) => response,
    async (error: any) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          await authService.refreshToken();
          const token = authService.getAccessToken();
          if (token) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return axios(originalRequest);
        } catch {
          // Refresh failed, redirect to login
          authService.clearTokens();
          window.location.href = '/login';
          return Promise.reject(error);
        }
      }

      return Promise.reject(error);
    }
  );
};

export default authService;
