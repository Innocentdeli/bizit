'use client';

import React from 'react';
import { AlertCircle, Target, TrendingUp } from 'lucide-react';
import { IntelligenceReport } from '@/types';
import { clsx } from 'clsx';

interface SummaryBlockProps {
    report: IntelligenceReport;
}

const SummaryBlock = ({ report }: SummaryBlockProps) => {
    const isUrgent = report.urgency === 'ACT';

    return (
        <div className="space-y-6">
            {/* Strategic Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <span className={clsx(
                            "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest border",
                            isUrgent ? "bg-red-50 text-urgency-red border-urgency-red/20" : "bg-bizit-green/10 text-bizit-green border-bizit-green/20"
                        )}>
                            {report.urgency} Mandate
                        </span>
                        <span className="text-bizit-gray/40 text-[10px] font-mono">ID: {report.id}</span>
                    </div>
                    <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-bizit-dark leading-tight">
                        {report.headline}
                    </h1>
                </div>

                <div className="flex items-center gap-3 bg-white p-3 rounded-2xl border border-bizit-dark/5 shadow-sm">
                    <div className="text-right">
                        <p className="text-[10px] uppercase tracking-wider text-bizit-gray/50 font-bold">Confidence</p>
                        <p className="text-lg font-bold text-bizit-green">{(report.confidence * 100).toFixed(1)}%</p>
                    </div>
                    <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-bizit-green/10 text-bizit-green">
                        <Target size={20} />
                    </div>
                </div>
            </div>

            {/* Primary Signal Card */}
            <div className="glass-card p-6 border-bizit-green/10">
                <div className="flex items-start gap-4">
                    <div className="mt-1 h-8 w-8 flex items-center justify-center rounded-lg bg-bizit-green text-white shadow-lg shadow-bizit-green/20">
                        <AlertCircle size={18} />
                    </div>
                    <div className="flex-1 space-y-2">
                        <h3 className="font-semibold text-bizit-dark">Market Verdict: {report.signal}</h3>
                        <p className="text-bizit-gray leading-relaxed text-sm md:text-base">
                            {report.impact}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SummaryBlock;
