import React, { createContext, useContext, useEffect, useState } from 'react';
import type { User, Session } from '@supabase/supabase-js';
import { supabase } from '../services/supabase';
import type { UserProfile } from '../types/database';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  loading: boolean;
  signInWithEmail: (email: string, password: string) => Promise<{ error: Error | null }>;
  signUpWithEmail: (email: string, password: string, fullName: string) => Promise<{ error: Error | null }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const isSupabaseConfigured = () => {
  const url = import.meta.env.VITE_SUPABASE_URL || '';
  return url && !url.includes('placeholder-project');
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async (userId: string) => {
    if (!isSupabaseConfigured()) {
      // Local profile fallback
      const storedUser = localStorage.getItem('ytber_current_user');
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser);
          setProfile({
            id: parsed.id,
            user_id: parsed.id,
            display_name: parsed.user_metadata?.full_name || parsed.email.split('@')[0],
            created_at: parsed.created_at || new Date().toISOString(),
          } as unknown as UserProfile);
        } catch {
          // ignore
        }
      }
      return;
    }

    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', userId)
        .single();
      if (!error && data) {
        setProfile(data as UserProfile);
      }
    } catch (err) {
      console.warn('Error fetching profile from Supabase:', err);
    }
  };

  useEffect(() => {
    // 1. Check local studio session first
    const storedUser = localStorage.getItem('ytber_current_user');
    const storedToken = localStorage.getItem('ytber_access_token');
    if (storedUser && storedToken) {
      try {
        const parsed = JSON.parse(storedUser);
        setUser(parsed);
        fetchProfile(parsed.id);
        setLoading(false);
        return;
      } catch {
        // proceed to supabase check
      }
    }

    if (isSupabaseConfigured()) {
      // Supabase initial session check
      supabase.auth.getSession().then(({ data: { session } }) => {
        setSession(session);
        setUser(session?.user ?? null);
        if (session?.user) {
          fetchProfile(session.user.id);
        }
        setLoading(false);
      }).catch(() => {
        setLoading(false);
      });

      // Listen for auth changes
      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        if (session?.user) {
          fetchProfile(session.user.id);
        } else {
          setProfile(null);
        }
        setLoading(false);
      });

      return () => {
        subscription.unsubscribe();
      };
    } else {
      setLoading(false);
    }
  }, []);

  const signInWithEmail = async (email: string, password: string) => {
    // Try Supabase if configured
    if (isSupabaseConfigured()) {
      try {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (!error && data.session) {
          return { error: null };
        }
        if (error && !error.message.includes('fetch')) {
          return { error: new Error(error.message) };
        }
      } catch {
        // Fallback to local auth
      }
    }

    // Local Studio Authentication Fallback (Guaranteed to work without network dependency)
    try {
      const cleanEmail = email.trim().toLowerCase();
      const localUsersRaw = localStorage.getItem('ytber_local_users');
      const localUsers = localUsersRaw ? JSON.parse(localUsersRaw) : [];
      const found = localUsers.find((u: any) => u.email === cleanEmail);

      if (found && found.password !== password) {
        return { error: new Error('Mật khẩu không chính xác, vui lòng thử lại.') };
      }

      // If user exists or create studio user on the fly
      const userId = found?.id || `user_${btoa(cleanEmail).replace(/=/g, '').slice(0, 16)}`;
      const fullName = found?.full_name || cleanEmail.split('@')[0];
      const localUser: any = {
        id: userId,
        email: cleanEmail,
        user_metadata: { full_name: fullName },
        created_at: found?.created_at || new Date().toISOString(),
      };

      const token = `guest-studio-token-${userId}`;
      localStorage.setItem('ytber_access_token', token);
      localStorage.setItem('ytber_current_user', JSON.stringify(localUser));

      setUser(localUser as User);
      setProfile({
        id: userId,
        user_id: userId,
        display_name: fullName,
        created_at: localUser.created_at,
      } as unknown as UserProfile);

      return { error: null };
    } catch (e: any) {
      return { error: new Error(e.message || 'Lỗi đăng nhập cục bộ') };
    }
  };

  const signUpWithEmail = async (email: string, password: string, fullName: string) => {
    // Try Supabase if configured
    if (isSupabaseConfigured()) {
      try {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: { data: { full_name: fullName } }
        });
        if (!error && data.user) {
          return { error: null };
        }
        if (error && !error.message.includes('fetch')) {
          return { error: new Error(error.message) };
        }
      } catch {
        // Fallback to local auth
      }
    }

    // Local Studio Registration Fallback
    try {
      const cleanEmail = email.trim().toLowerCase();
      const localUsersRaw = localStorage.getItem('ytber_local_users');
      const localUsers: any[] = localUsersRaw ? JSON.parse(localUsersRaw) : [];

      const exists = localUsers.some((u: any) => u.email === cleanEmail);
      if (exists) {
        return { error: new Error('Email này đã được đăng ký trong hệ thống Studio. Vui lòng chuyển sang Đăng nhập.') };
      }

      const userId = `user_${btoa(cleanEmail).replace(/=/g, '').slice(0, 16)}`;
      const newUser = {
        id: userId,
        email: cleanEmail,
        password: password,
        full_name: fullName.trim() || cleanEmail.split('@')[0],
        created_at: new Date().toISOString(),
      };

      localUsers.push(newUser);
      localStorage.setItem('ytber_local_users', JSON.stringify(localUsers));

      // Auto sign in
      const localUser: any = {
        id: userId,
        email: cleanEmail,
        user_metadata: { full_name: newUser.full_name },
        created_at: newUser.created_at,
      };
      const token = `guest-studio-token-${userId}`;
      localStorage.setItem('ytber_access_token', token);
      localStorage.setItem('ytber_current_user', JSON.stringify(localUser));

      setUser(localUser as User);
      setProfile({
        id: userId,
        user_id: userId,
        display_name: newUser.full_name,
        created_at: newUser.created_at,
      } as unknown as UserProfile);

      return { error: null };
    } catch (e: any) {
      return { error: new Error(e.message || 'Lỗi đăng ký cục bộ') };
    }
  };

  const signOut = async () => {
    if (isSupabaseConfigured()) {
      try {
        await supabase.auth.signOut();
      } catch {
        // ignore
      }
    }
    localStorage.removeItem('ytber_access_token');
    localStorage.removeItem('ytber_current_user');
    setUser(null);
    setSession(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    if (user) {
      await fetchProfile(user.id);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      session,
      profile,
      loading,
      signInWithEmail,
      signUpWithEmail,
      signOut,
      refreshProfile
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
