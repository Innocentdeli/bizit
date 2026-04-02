'use client';

import React from 'react';
import { Activity, Building2, User } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import { signIn } from 'next-auth/react';

export default function LoginPage() {

    const handleLogin = (role: 'USER' | 'BUSINESS') => {
        // Pre-fill credentials for the prototype demo
        if (role === 'USER') {
            signIn('credentials', { username: 'consumer', password: 'password', role: 'USER', callbackUrl: '/market' });
        } else {
            signIn('credentials', { username: 'business', password: 'password', role: 'BUSINESS', callbackUrl: '/dashboard' });
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] bg-bizit-light">
            <div className="bg-white p-8 rounded-3xl shadow-xl border border-bizit-dark/5 w-full max-w-md text-center space-y-8">
                <div>
                    <div className="h-12 w-12 bg-bizit-green text-white rounded-xl flex items-center justify-center mx-auto mb-4">
                        <Activity size={24} />
                    </div>
                    <h1 className="text-2xl font-bold text-bizit-dark">Welcome to Bizit Pulse</h1>
                    <p className="text-bizit-gray text-sm mt-2">Choose your persona to explore the platform.</p>
                </div>

                <div className="space-y-4">
                    <button
                        onClick={() => handleLogin('USER')}
                        className="w-full flex items-center gap-4 p-4 rounded-xl border border-bizit-dark/10 hover:border-bizit-green hover:bg-bizit-green/5 transition-all text-left group"
                    >
                        <div className="h-10 w-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <User size={20} />
                        </div>
                        <div>
                            <p className="font-bold text-bizit-dark">Consumer / Explorer</p>
                            <p className="text-xs text-bizit-gray">I want to find services and insights.</p>
                        </div>
                    </button>

                    <button
                        onClick={() => handleLogin('BUSINESS')}
                        className="w-full flex items-center gap-4 p-4 rounded-xl border border-bizit-dark/10 hover:border-bizit-dark hover:bg-bizit-dark/5 transition-all text-left group"
                    >
                        <div className="h-10 w-10 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <Building2 size={20} />
                        </div>
                        <div>
                            <p className="font-bold text-bizit-dark">Business Owner</p>
                            <p className="text-xs text-bizit-gray">I want to manage my listing and grow.</p>
                        </div>
                    </button>
                </div>

                <div className="pt-6 border-t border-gray-100">
                    <p className="text-xs text-bizit-gray">
                        This is a <span className="font-bold text-bizit-dark">Prototype Environment</span>.
                        No password required.
                    </p>
                </div>
            </div>
        </div>
    );
}
