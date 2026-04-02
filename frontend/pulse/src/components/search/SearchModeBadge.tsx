'use client';

import React from 'react';
import { Globe, FileText, Shuffle } from 'lucide-react';

interface SearchModeBadgeProps {
    mode: 'EXTERNAL' | 'INTERNAL' | 'HYBRID';
    docCount?: number;
    webSourceCount?: number;
}

const SearchModeBadge = ({ mode, docCount = 0, webSourceCount = 0 }: SearchModeBadgeProps) => {
    const configs = {
        EXTERNAL: {
            icon: Globe,
            label: 'Web Sources',
            color: 'text-blue-600',
            bg: 'bg-blue-50',
            border: 'border-blue-200',
            count: webSourceCount
        },
        INTERNAL: {
            icon: FileText,
            label: 'Your Documents',
            color: 'text-bizit-green',
            bg: 'bg-bizit-green/10',
            border: 'border-bizit-green/20',
            count: docCount
        },
        HYBRID: {
            icon: Shuffle,
            label: 'Web + Documents',
            color: 'text-purple-600',
            bg: 'bg-purple-50',
            border: 'border-purple-200',
            count: webSourceCount + docCount
        }
    };

    const config = configs[mode];
    const Icon = config.icon;

    return (
        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${config.bg} ${config.border} border text-[10px] font-bold uppercase tracking-wider ${config.color}`}>
            <Icon size={10} />
            <span>{config.label}</span>
            {config.count > 0 && (
                <span className="ml-0.5 opacity-70">({config.count})</span>
            )}
        </div>
    );
};

export default SearchModeBadge;
