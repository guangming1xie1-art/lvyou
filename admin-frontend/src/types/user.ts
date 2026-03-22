// 用户相关类型定义

export interface User {
  id: number;
  username: string;
  email: string;
  realName?: string;
  phone?: string;
  avatar?: string;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
  roles: string[];
}

export interface UserRequest {
  email: string;
  username: string;
  password?: string;
  realName?: string;
  phone?: string;
  isActive?: boolean;
  roleIds?: number[];
}

export interface Role {
  id: number;
  name: string;
  code: string;
  description?: string;
  isActive: boolean;
  createdAt: string;
  permissions: string[];
}

export interface RoleRequest {
  name: string;
  code: string;
  description?: string;
  isActive?: boolean;
  permissionIds?: number[];
}

export interface Permission {
  id: number;
  name: string;
  code: string;
  type: 'MENU' | 'BUTTON' | 'API';
  parentId?: number;
  path?: string;
  icon?: string;
  sortOrder: number;
  isActive: boolean;
  createdAt: string;
}

export interface PermissionRequest {
  name: string;
  code: string;
  type: string;
  parentId?: number;
  path?: string;
  icon?: string;
  sortOrder?: number;
  isActive?: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  type: string;
  expiresIn: number;
  user: User;
}

export interface UserQueryParams {
  page?: number;
  size?: number;
  keyword?: string;
  status?: boolean;
}
