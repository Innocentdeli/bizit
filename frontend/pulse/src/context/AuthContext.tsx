'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
    id: string;
    name: string;
    role: 'USER' | 'BUSINESS' | 'ADMIN';
    avatar?: string;
}

interface AuthContextType {
    user: User | null;
    login: (role: 'USER' | 'BUSINESS') => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const router = useRouter();

    // Check local storage on mount
    useEffect(() => {
        const stored = localStorage.getItem('bizit_user');
        if (stored) {
            setUser(JSON.parse(stored));
        }
    }, []);

    const login = (role: 'USER' | 'BUSINESS') => {
        const mockUser: User = role === 'BUSINESS'
            ? { id: 'u-biz', name: 'Lagos Tech Hub', role: 'BUSINESS', avatar: 'B' }
            : { id: 'u-cons', name: 'Chinedu O.', role: 'USER', avatar: 'C' };

        setUser(mockUser);
        localStorage.setItem('bizit_user', JSON.stringify(mockUser));

        if (role === 'BUSINESS') router.push('/dashboard');
        else router.push('/market');
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('bizit_user');
        router.push('/');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
