'use client';

import React from 'react';
import { usePulseStore } from '@/store/usePulseStore';
import { User, Settings, Globe, Zap, Shield, CreditCard, Bell } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

export default function ProfilePage() {
    const { personalization, setPersonalization } = usePulseStore();

    const handleStrategyChange = (strategy: any) => {
        setPersonalization({ ...personalization, strategy });
    };

    return (
        <div className="max-w-4xl mx-auto py-12 space-y-12 pb-24">
            <div className="flex flex-col md:flex-row items-center gap-6 p-8 bg-white rounded-3xl border border-bizit-dark/5 shadow-sm">
                <div className="h-24 w-24 rounded-full bg-bizit-green/10 flex items-center justify-center text-bizit-green border-4 border-white shadow-xl">
                    <User size={48} />
                </div>
                <div className="space-y-1 text-center md:text-left">
                    <h1 className="text-2xl font-bold text-bizit-dark tracking-tight">Sovereignty Profile</h1>
                    <p className="text-bizit-gray text-sm font-medium">active_node_id: africa_west_01</p>
                    <div className="flex items-center gap-2 mt-2 justify-center md:justify-start">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-bizit-green/10 text-bizit-green border border-bizit-green/20">
                            Pro Tier
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-bizit-gold/10 text-bizit-gold border border-bizit-gold/20">
                            Founder Mode
                        </span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Strategic Mandate */}
                <div className="bg-white rounded-3xl p-6 border border-bizit-dark/5 space-y-6">
                    <div className="flex items-center gap-2 text-bizit-dark">
                        <Zap size={20} className="text-bizit-green" />
                        <h3 className="font-semibold">Strategic Mandate</h3>
                    </div>
                    <div className="space-y-3">
                        {[
                            { id: 'GROWTH', label: 'GROWTH', desc: 'Prioritize expansion and market capture.' },
                            { id: 'PRESERVE', label: 'PRESERVE', desc: 'Focus on risk mitigation and stability.' },
                            { id: 'ARBITRAGE', label: 'ARBITRAGE', desc: 'Identify and exploit market gaps quickly.' }
                        ].map((strategy) => (
                            <button
                                key={strategy.id}
                                onClick={() => handleStrategyChange(strategy.id)}
                                className={`w-full text-left p-4 rounded-2xl border transition-all ${personalization.strategy === strategy.id
                                        ? "border-bizit-green bg-bizit-green/5 ring-1 ring-bizit-green"
                                        : "border-bizit-dark/5 hover:border-bizit-dark/10"
                                    }`}
                            >
                                <p className="text-xs font-bold text-bizit-dark uppercase tracking-widest">{strategy.label}</p>
                                <p className="text-[11px] text-bizit-gray mt-1">{strategy.desc}</p>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Global Context */}
                <div className="space-y-8">
                    <div className="bg-white rounded-3xl p-6 border border-bizit-dark/5 space-y-4">
                        <div className="flex items-center gap-2 text-bizit-dark">
                            <Globe size={20} className="text-bizit-green" />
                            <h3 className="font-semibold">Geographic Context</h3>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-bizit-gray uppercase tracking-widest">Primary Market</label>
                            <select className="w-full bg-bizit-light border-none rounded-xl text-sm focus:ring-bizit-green">
                                <option>Nigeria (West Africa)</option>
                                <option>Kenya (East Africa)</option>
                                <option>South Africa (Southern Africa)</option>
                                <option>Egypt (MENA)</option>
                                <option>Global Markets</option>
                            </select>
                        </div>
                    </div>

                    <div className="bg-white rounded-3xl p-6 border border-bizit-dark/5 space-y-4">
                        <div className="flex items-center gap-2 text-bizit-dark">
                            <Shield size={20} className="text-bizit-green" />
                            <h3 className="font-semibold">Privacy & Security</h3>
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-xs font-bold text-bizit-dark">Incognito Reasoning</p>
                                    <p className="text-[10px] text-bizit-gray">Don't store search history locally.</p>
                                </div>
                                <div className="h-5 w-10 bg-bizit-dark/10 rounded-full cursor-pointer relative">
                                    <div className="absolute left-1 top-1 h-3 w-3 bg-white rounded-full" />
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-xs font-bold text-bizit-dark">Zero-Knowledge Reports</p>
                                    <p className="text-[10px] text-bizit-gray">Encrypt report IDs for sharing.</p>
                                </div>
                                <div className="h-5 w-10 bg-bizit-green rounded-full cursor-pointer relative">
                                    <div className="absolute right-1 top-1 h-3 w-3 bg-white rounded-full" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex items-center justify-center gap-4">
                <BizitButton variant="primary" className="px-12">Save Configuration</BizitButton>
                <BizitButton variant="outline">Reset Defaults</BizitButton>
            </div>
        </div>
    );
}
