'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { usePulseStore } from '@/store/usePulseStore';
import { History, Search, ArrowRight, Calendar, Target, ShieldCheck } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import { formatDistanceToNow } from 'date-fns';

export default function HistoryPage() {
    const router = useRouter();
    const { history, setActiveReport } = usePulseStore();

    const handleRevisit = (report: any) => {
        setActiveReport(report);
        router.push(`/answer/${report.id}`);
    };

    return (
        <div className="max-w-4xl mx-auto py-12 space-y-10">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-2">
                    <div className="flex items-center gap-2 text-bizit-green">
                        <History size={24} />
                        <h1 className="text-3xl font-bold text-bizit-dark tracking-tight">Intelligence Repository</h1>
                    </div>
                    <p className="text-bizit-gray text-sm">
                        Revisit past market digests, strategic analyses, and trade signals.
                    </p>
                </div>
                <div className="flex items-center gap-4 text-[10px] font-bold uppercase tracking-widest text-bizit-gray/40">
                    <span>Active Nodes: {history.length}</span>
                    <span className="h-4 w-px bg-bizit-dark/10" />
                    <span>Storage: Local Substrate</span>
                </div>
            </div>

            <div className="space-y-4">
                {history.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-24 text-center space-y-4 bg-white rounded-3xl border border-dashed border-bizit-dark/10">
                        <div className="h-16 w-16 bg-bizit-light rounded-2xl flex items-center justify-center text-bizit-gray/30">
                            <Search size={32} />
                        </div>
                        <div className="space-y-1">
                            <p className="font-semibold text-bizit-dark">No intelligence logged yet</p>
                            <p className="text-xs text-bizit-gray/60">Start a search to build your sovereign repository.</p>
                        </div>
                        <BizitButton onClick={() => router.push('/')} variant="primary">New Search</BizitButton>
                    </div>
                ) : (
                    history.map((report) => (
                        <div
                            key={report.id}
                            onClick={() => handleRevisit(report)}
                            className="group glass-card p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 hover:border-bizit-green/40 hover:shadow-md transition-all cursor-pointer border-bizit-dark/5"
                        >
                            <div className="flex-1 space-y-3 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest border ${report.urgency === 'ACT' ? "bg-red-50 text-urgency-red border-urgency-red/20" : "bg-bizit-light text-bizit-gray border-bizit-dark/10"
                                        }`}>
                                        {report.urgency}
                                    </span>
                                    <div className="flex items-center gap-1.5 text-xs text-bizit-gray/40 font-medium">
                                        <Calendar size={12} />
                                        {formatDistanceToNow(report.timestamp)} ago
                                    </div>
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-bizit-dark truncate group-hover:text-bizit-green transition-colors">
                                        {report.headline}
                                    </h3>
                                    <p className="text-xs text-bizit-gray/60 italic truncate mt-1">
                                        Query: "{report.query}"
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-6 shrink-0 w-full md:w-auto justify-between md:justify-end">
                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <p className="text-[10px] uppercase font-bold text-bizit-gray/40">Confidence</p>
                                        <div className="flex items-center gap-1.5 justify-end">
                                            <span className="text-sm font-bold text-bizit-green">{Math.round(report.confidence * 100)}%</span>
                                            <Target size={14} className="text-bizit-green" />
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[10px] uppercase font-bold text-bizit-gray/40">Nodes</p>
                                        <div className="flex items-center gap-1.5 justify-end">
                                            <span className="text-sm font-bold text-bizit-dark">{report.sources.length}</span>
                                            <ShieldCheck size={14} className="text-bizit-dark" />
                                        </div>
                                    </div>
                                </div>
                                <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-bizit-green/10 text-bizit-green group-hover:bg-bizit-green group-hover:text-white transition-all">
                                    <ArrowRight size={20} />
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
