'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile, UserRole, DemoAccount } from '@/types';
import { api } from '@/services/api';

interface AuthContextType {
  user: UserProfile | null;
  role: UserRole | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  quickDemoLogin: (email: string, password?: string) => Promise<void>;
  isAdmin: boolean;
  isStateOfficer: boolean;
  isDistrictOfficer: boolean;
  isFieldOfficer: boolean;
  isAnalyst: boolean;
  demoAccounts: DemoAccount[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [demoAccounts, setDemoAccounts] = useState<DemoAccount[]>([]);

  // Load demo accounts on mount
  useEffect(() => {
    api.getDemoAccounts()
      .then(setDemoAccounts)
      .catch(() => []);
  }, []);

  // Check stored token and resolve officer profile on load
  useEffect(() => {
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('jaldrishti_token') : null;
    if (storedToken) {
      setToken(storedToken);
      api.getMe()
        .then((profile) => {
          setUser(profile);
          setIsLoading(false);
        })
        .catch(() => {
          // Token expired or invalid
          if (typeof window !== 'undefined') {
            localStorage.removeItem('jaldrishti_token');
          }
          setToken(null);
          setUser(null);
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string, rememberMe: boolean = false) => {
    setIsLoading(true);
    try {
      const res = await api.login(email, password, rememberMe);
      if (typeof window !== 'undefined') {
        localStorage.setItem('jaldrishti_token', res.access_token);
      }
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch {
      // Ignore network error on logout
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('jaldrishti_token');
      }
      setToken(null);
      setUser(null);
    }
  };

  const quickDemoLogin = async (email: string, password: string = 'JalDrishti@2026') => {
    await login(email, password, false);
  };

  const role = user?.role || null;

  const value: AuthContextType = {
    user,
    role,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
    logout,
    quickDemoLogin,
    isAdmin: role === 'ADMIN',
    isStateOfficer: role === 'STATE_OFFICER',
    isDistrictOfficer: role === 'DISTRICT_OFFICER',
    isFieldOfficer: role === 'FIELD_OFFICER',
    isAnalyst: role === 'ANALYST',
    demoAccounts
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
