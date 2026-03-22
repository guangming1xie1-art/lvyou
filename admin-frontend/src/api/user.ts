import request from './request';
import type { User, UserRequest, UserQueryParams, PageResponse } from '@/types';

export function getUsers(params: UserQueryParams = {}): Promise<PageResponse<User>> {
  return request.get('/admin/users', { params });
}

export function getUser(id: number): Promise<User> {
  return request.get(`/admin/users/${id}`);
}

export function createUser(data: UserRequest): Promise<User> {
  return request.post('/admin/users', data);
}

export function updateUser(id: number, data: UserRequest): Promise<User> {
  return request.put(`/admin/users/${id}`, data);
}

export function deleteUser(id: number): Promise<void> {
  return request.delete(`/admin/users/${id}`);
}
