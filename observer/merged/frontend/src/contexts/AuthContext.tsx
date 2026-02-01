import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode
} from 'react';
import type { AuthState, AuthContextValue, AuthResponse } from '@/types';

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    token: null,
    error: null,
    loading: true
  });

  // Verify session on mount
  useEffect(() => {
    verify();
  }, []);

  const verify = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch('/auth/verify', {
        credentials: 'include'
      });
      const data: AuthResponse = await response.json();

      setState({
        isAuthenticated: data.authenticated,
        token: data.token ?? null,
        error: data.error ?? null,
        loading: false
      });

      return data.authenticated;
    } catch (error) {
      setState({
        isAuthenticated: false,
        token: null,
        error: 'Failed to verify session',
        loading: false
      });
      return false;
    }
  }, []);

  const login = useCallback(async (): Promise<void> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch('/auth/biometric', {
        method: 'POST',
        credentials: 'include'
      });
      const data: AuthResponse = await response.json();

      setState({
        isAuthenticated: data.authenticated,
        token: data.token ?? null,
        error: data.error ?? null,
        loading: false
      });
    } catch (error) {
      setState({
        isAuthenticated: false,
        token: null,
        error: 'Authentication request failed',
        loading: false
      });
    }
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    try {
      await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch {
      // Ignore logout errors
    }

    setState({
      isAuthenticated: false,
      token: null,
      error: null,
      loading: false
    });
  }, []);

  const value: AuthContextValue = {
    ...state,
    login,
    logout,
    verify
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
