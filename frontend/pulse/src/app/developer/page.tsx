'use client';

import React, { useState } from 'react';
import { Terminal, Copy, Check, Webhook, Key } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

export default function DeveloperPage() {
    const [apiKey, setApiKey] = useState('pk_live_bk...');
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        setApiKey('pk_live_8f92a3b4c5d6e7f8g9h0i1j2k3l4'); // Reveal full key mock
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="max-w-4xl mx-auto pb-20 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-bizit-dark flex items-center gap-2">
                        <Terminal className="text-bizit-green" />
                        Developer Portal
                    </h1>
                    <p className="text-bizit-gray text-sm">Manage API keys, webhooks, and integrations.</p>
                </div>
                <BizitButton variant="outline" size="sm">Read Documentation</BizitButton>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* API Keys */}
                <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                    <div className="flex items-center gap-2 text-bizit-dark font-bold">
                        <Key size={18} className="text-bizit-gold" /> API Access
                    </div>
                    <p className="text-sm text-bizit-gray">Use this key to authenticate requests to the Bizit Pulse API.</p>

                    <div className="bg-gray-900 rounded-lg p-4 flex items-center justify-between group">
                        <code className="text-green-400 font-mono text-sm truncate mr-4">{apiKey}</code>
                        <button onClick={handleCopy} className="text-gray-400 hover:text-white transition-colors">
                            {copied ? <Check size={16} /> : <Copy size={16} />}
                        </button>
                    </div>
                    <div className="flex gap-2">
                        <BizitButton variant="primary" size="sm">Roll Key</BizitButton>
                        <BizitButton variant="secondary" size="sm" className="bg-gray-100 text-bizit-dark border-none">Create Scoped Key</BizitButton>
                    </div>
                </div>

                {/* Webhooks */}
                <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                    <div className="flex items-center gap-2 text-bizit-dark font-bold">
                        <Webhook size={18} className="text-blue-500" /> Webhooks
                    </div>
                    <p className="text-sm text-bizit-gray">Receive real-time events for reviews, claims, and market alerts.</p>

                    <div className="space-y-2">
                        <div className="p-3 border rounded-xl flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500" />
                                <span className="text-sm font-mono text-bizit-dark">https://api.myapp.com/events</span>
                            </div>
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-500">review.created</span>
                        </div>
                        <div className="p-3 border rounded-xl flex items-center justify-between opacity-50">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-gray-300" />
                                <span className="text-sm font-mono text-bizit-dark">.../webhooks/market</span>
                            </div>
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-500">market.alert</span>
                        </div>
                    </div>
                    <BizitButton variant="outline" size="sm" className="w-full">Add Endpoint</BizitButton>
                </div>
            </div>

            {/* Ingestion Status (Module 16) */}
            <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-lg">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold flex items-center gap-2">
                        <Activity className="text-bizit-green" /> Data Pipeline Status
                    </h3>
                    <span className="text-xs font-mono text-green-400 bg-green-400/10 px-2 py-1 rounded">SYSTEM HEALTHY</span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="p-4 bg-white/5 rounded-xl">
                        <p className="text-xs text-gray-400 uppercase">Records Processed</p>
                        <p className="text-2xl font-bold mt-1">1.4M</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                        <p className="text-xs text-gray-400 uppercase">API Latency</p>
                        <p className="text-2xl font-bold mt-1">45ms</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl">
                        <p className="text-xs text-gray-400 uppercase">Integrations</p>
                        <p className="text-2xl font-bold mt-1">12</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Activity({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
            width="18" height="18"
        >
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
    )
}
