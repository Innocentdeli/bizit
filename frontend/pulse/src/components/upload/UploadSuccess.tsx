'use client';

import React from 'react';
import { CheckCircle2, Sparkles, Search, FileCheck } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

interface UploadSuccessProps {
    filename: string;
    batchSize: number;
    summary: string;
    suggestedQueries: string[];
    onSearch: (query: string) => void;
    onClose: () => void;
    onViewLibrary?: () => void;
}

const UploadSuccess = ({
    filename,
    batchSize,
    summary,
    suggestedQueries,
    onSearch,
    onClose,
    onViewLibrary
}: UploadSuccessProps) => {
    return (
        <div className="w-full max-w-2xl mx-auto glass-card p-8 space-y-6 animate-in zoom-in-95 duration-500">
            {/* Success Header */}
            <div className="flex items-start gap-4">
                <div className="p-3 rounded-2xl bg-bizit-green/10 text-bizit-green shrink-0">
                    <CheckCircle2 size={28} />
                </div>
                <div className="space-y-1 flex-1">
                    <div className="inline-flex items-center gap-2 px-2 py-0.5 rounded-full bg-bizit-green/10 text-bizit-green text-[10px] font-bold uppercase tracking-wider border border-bizit-green/20 mb-2">
                        <FileCheck size={10} /> Ingestion Complete
                    </div>
                    <h2 className="text-xl font-bold text-bizit-dark leading-tight">
                        {filename}
                    </h2>
                    <p className="text-sm text-bizit-gray">
                        Successfully processed <span className="font-bold text-bizit-dark">{batchSize}</span> file{batchSize !== 1 ? 's' : ''} into your Sovereign Knowledge Base.
                    </p>
                </div>
            </div>

            {/* Collective Summary */}
            <div className="p-4 rounded-xl bg-bizit-light border border-bizit-dark/5">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles size={14} className="text-bizit-green" />
                    <span className="text-xs font-bold uppercase tracking-wider text-bizit-gray">Collective Intelligence</span>
                </div>
                <p className="text-sm text-bizit-dark leading-relaxed">
                    {summary}
                </p>
            </div>

            {/* Suggested Queries */}
            {suggestedQueries && suggestedQueries.length > 0 && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <Search size={14} className="text-bizit-gray" />
                        <span className="text-xs font-bold uppercase tracking-wider text-bizit-gray">Suggested Queries</span>
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                        {suggestedQueries.map((query, idx) => (
                            <button
                                key={idx}
                                onClick={() => {
                                    onSearch(query);
                                    onClose();
                                }}
                                className="group flex items-center justify-between p-3 rounded-xl bg-white border border-bizit-dark/5 hover:border-bizit-green/40 hover:bg-bizit-green/5 transition-all text-left"
                            >
                                <span className="text-sm font-medium text-bizit-dark group-hover:text-bizit-green transition-colors">
                                    {query}
                                </span>
                                <Search size={14} className="text-bizit-gray group-hover:text-bizit-green group-hover:translate-x-1 transition-all" />
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-bizit-dark/5">
                <BizitButton
                    onClick={onClose}
                    variant="outline"
                    className="flex-1"
                >
                    Upload More
                </BizitButton>
                <BizitButton
                    onClick={onViewLibrary || onClose}
                    className="flex-1"
                >
                    View Library
                </BizitButton>
            </div>
        </div>
    );
};

export default UploadSuccess;
