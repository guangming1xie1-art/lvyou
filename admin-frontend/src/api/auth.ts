import request from './request';
import type { LoginRequest, LoginResponse, User } from '@/types';

export function login(data: LoginRequest): Promise<LoginResponse> {
  return request.post('/auth/login', data);
}

export function getCurrentUser(): Promise<User> {
  return request.get('/auth/me');
}

export function logout(): Promise<void> {
  return request.post('/auth/logout');
}
