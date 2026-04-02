'use client';

import React from 'react';
import { ShieldCheck, Info, ExternalLink, Scale, CheckCircle2 } from 'lucide-react';
import { IntelligenceReport } from '@/types';

interface VeracityMatrixProps {
    report: IntelligenceReport;
}

const VeracityMatrix = ({ report }: VeracityMatrixProps) => {
    return (
        <div className="bg-white rounded-3xl p-8 border border-bizit-dark/5 shadow-sm space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-2 text-bizit-dark text-lg font-bold">
                        <ShieldCheck size={24} className="text-bizit-green" />
                        <h3>Intelligence Veracity Matrix</h3>
                    </div>
                    <p className="text-bizit-gray/60 text-sm">Cross-referenced verification from multiple sovereign nodes.</p>
                </div>
                <div className="flex items-center gap-2 text-[10px] font-bold text-bizit-green uppercase tracking-widest bg-bizit-green/5 px-3 py-1.5 rounded-full border border-bizit-green/10">
                    <Scale size={14} />
                    Credibility Weighted
                </div>
            </div>

            {/* Sources List */}
            <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {report.sources.map((source, i) => (
                        <div key={i} className="group p-5 rounded-2xl bg-bizit-light hover:bg-white transition-all border border-transparent hover:border-bizit-green/10 hover:shadow-md">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <div className="h-2 w-2 rounded-full bg-bizit-green" />
                                    <span className="text-sm font-bold text-bizit-dark truncate max-w-[150px]">
                                        {source.title}
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="text-[10px] font-bold text-bizit-green bg-bizit-green/10 px-2 py-0.5 rounded">
                                        {Math.round(source.trust * 100)}% Match
                                    </span>
                                </div>
                            </div>

                            <p className="text-xs text-bizit-gray/80 leading-relaxed min-h-[40px]">
                                "{source.reason}"
                            </p>

                            <div className="mt-4 pt-4 border-t border-bizit-dark/5 flex items-center justify-between text-[10px] font-bold uppercase tracking-widest text-bizit-gray/40">
                                <span className="flex items-center gap-1.5">
                                    <CheckCircle2 size={12} className="text-bizit-green" />
                                    Verified Source
                                </span>
                                {source.url && (
                                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="hover:text-bizit-green flex items-center gap-1">
                                        View Data <ExternalLink size={10} />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
                {report.sources.length === 0 && (
                    <div className="p-12 rounded-3xl border-2 border-dashed border-bizit-dark/5 flex flex-col items-center justify-center text-bizit-gray/40 text-sm italic">
                        No external nodes synthesized for this query.
                    </div>
                )}
            </div>
        </div>
    );
};

export default VeracityMatrix;
