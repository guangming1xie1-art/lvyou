/**
 * Authentication Hook
 * Provides authentication state and methods
 */

import { useAuth as useAuthContext } from '@/context/AuthContext';
import type { User, AuthContextType } from '@/types/auth';

export interface UseAuthReturn extends AuthContextType {}

/**
 * Hook to access authentication state and methods
 * 
 * @example
 * const { user, isAuthenticated, login, logout } = useAuth();
 */
export const useAuth = (): UseAuthReturn => {
  return useAuthContext();
};

export default useAuth;
