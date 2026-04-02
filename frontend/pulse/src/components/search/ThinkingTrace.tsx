'use client';

import React from 'react';
import { Activity, Search, ShieldCheck, Zap, BrainCircuit, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { ThinkingStep } from '@/types';

interface ThinkingTraceProps {
    isVisible: boolean;
    steps: ThinkingStep[];
    currentQuery: string;
}

const ThinkingTrace = ({ isVisible, steps, currentQuery }: ThinkingTraceProps) => {
    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="fixed inset-x-4 top-24 z-40 mx-auto max-w-2xl"
                >
                    <div className="glass-card p-6 border-bizit-green/20 ring-1 ring-bizit-green/10 shadow-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-bizit-green/10 text-bizit-green">
                                    <Activity className="animate-pulse" size={24} />
                                </div>
                                <div>
                                    <h3 className="bizit-heading text-lg">Thinking Trace</h3>
                                    <p className="text-xs text-bizit-gray/60 font-mono truncate max-w-[200px] md:max-w-xs">
                                        Digest: "{currentQuery}"
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 rounded-full bg-bizit-dark/5 px-2.5 py-1 text-[10px] font-bold uppercase tracking-widest text-bizit-gray">
                                Frontier Pro 2.5 Active
                            </div>
                        </div>

                        <div className="space-y-4">
                            {steps.map((step, index) => (
                                <div key={step.id} className="relative flex items-center gap-4">
                                    {/* Connector Line */}
                                    {index < steps.length - 1 && (
                                        <div className="absolute left-5 top-8 w-0.5 h-6 bg-bizit-dark/5" />
                                    )}

                                    <div className={`flex h-10 w-10 items-center justify-center rounded-xl transition-colors duration-500 ${step.status === 'complete' ? 'bg-bizit-green text-white' :
                                        step.status === 'loading' ? 'bg-bizit-green/10 text-bizit-green' :
                                            'bg-bizit-dark/5 text-bizit-gray/40'
                                        }`}>
                                        {step.status === 'loading' ? (
                                            <Loader2 size={18} className="animate-spin" />
                                        ) : (
                                            <step.icon size={18} />
                                        )}
                                    </div>

                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <span className={`text-sm font-semibold transition-colors duration-500 ${step.status === 'pending' ? 'text-bizit-gray/40' : 'text-bizit-dark'
                                                }`}>
                                                {step.label}
                                            </span>
                                            {step.status === 'complete' && (
                                                <motion.span
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    className="text-[10px] font-bold text-bizit-green bg-bizit-green/10 px-1.5 py-0.5 rounded"
                                                >
                                                    VERIFIED
                                                </motion.span>
                                            )}
                                        </div>
                                        {step.status === 'loading' && (
                                            <motion.div
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                className="text-[10px] text-bizit-green font-medium animate-pulse mt-1"
                                            >
                                                Deep reasoning in progress...
                                            </motion.div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default ThinkingTrace;
