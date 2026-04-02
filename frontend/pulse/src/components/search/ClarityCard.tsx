'use client';

import React from 'react';
import { HelpCircle, ArrowRight, Activity, Zap, Compass } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

interface ClarityCardProps {
    question: string;
    options: string[];
    onClarify: (choice: string) => void;
    context?: any;
}

const ClarityCard = ({ question, options, onClarify, context }: ClarityCardProps) => {
    return (
        <div className="w-full max-w-2xl mx-auto glass-card p-8 space-y-6 animate-in zoom-in-95 duration-500 border-bizit-green/20 shadow-xl shadow-bizit-green/5">
            <div className="flex items-start gap-4">
                <div className="p-3 rounded-2xl bg-bizit-green/10 text-bizit-green shrink-0">
                    <HelpCircle size={28} className="animate-pulse" />
                </div>
                <div className="space-y-1">
                    <div className="inline-flex items-center gap-2 px-2 py-0.5 rounded-full bg-bizit-green/10 text-bizit-green text-[10px] font-bold uppercase tracking-wider border border-bizit-green/20 mb-2">
                        Dynamic Clarity Check
                    </div>
                    <h2 className="text-xl font-bold text-bizit-dark leading-tight">
                        {question}
                    </h2>
                    <p className="text-sm text-bizit-gray">
                        I've detected your query deviates from your **{context?.persona?.sector || 'current'}** business profile. How should I ground this research?
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-3">
                {options.map((option, idx) => (
                    <button
                        key={idx}
                        onClick={() => onClarify(option)}
                        className="group flex items-center justify-between p-4 rounded-xl bg-white border border-bizit-dark/5 hover:border-bizit-green/40 hover:bg-bizit-green/5 transition-all text-left"
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-bizit-dark/5 flex items-center justify-center text-bizit-gray group-hover:bg-bizit-green/10 group-hover:text-bizit-green transition-colors">
                                {idx === 0 ? <Compass size={16} /> : idx === 1 ? <Zap size={16} /> : <Activity size={16} />}
                            </div>
                            <span className="text-sm font-semibold text-bizit-dark group-hover:text-bizit-green transition-colors">
                                {option}
                            </span>
                        </div>
                        <ArrowRight size={16} className="text-bizit-gray group-hover:text-bizit-green group-hover:translate-x-1 transition-all" />
                    </button>
                ))}
            </div>

            {context?.vitals && (
                <div className="pt-4 border-t border-bizit-dark/5 flex items-center gap-6 justify-center">
                    <div className="text-center">
                        <div className="text-[10px] uppercase text-bizit-gray font-bold tracking-widest">Liquid Cash</div>
                        <div className="text-sm font-mono font-bold text-bizit-dark">${context.vitals.liquid_cash.toLocaleString()}</div>
                    </div>
                    <div className="text-center">
                        <div className="text-[10px] uppercase text-bizit-gray font-bold tracking-widest">Growth Loop</div>
                        <div className="text-sm font-mono font-bold text-bizit-dark">VERIFIED</div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClarityCard;
