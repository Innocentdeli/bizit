'use client';

import React, { useState } from 'react';
import { Search, MapPin, Globe, Briefcase, Zap, FileUp, Filter } from 'lucide-react';
import BizitButton from '../common/BizitButton';
import { clsx } from 'clsx';

interface SearchBarProps {
    onSearch: (query: string, options: any) => void;
    isLoading?: boolean;
}

const SearchBar = ({ onSearch, isLoading }: SearchBarProps) => {
    const [query, setQuery] = useState('');
    const [showFilters, setShowFilters] = useState(false);
    const [domain, setDomain] = useState('All');
    const [region, setRegion] = useState('NG');
    const [urgency, setUrgency] = useState('Standard');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query, { domain, region, urgency });
        }
    };

    return (
        <div className="w-full max-w-3xl mx-auto space-y-4">
            <form onSubmit={handleSubmit} className="relative group">
                <div className="relative flex items-center bg-white rounded-2xl shadow-lg border border-bizit-dark/5 focus-within:border-bizit-green/40 focus-within:ring-4 focus-within:ring-bizit-green/5 transition-all">
                    <div className="pl-4 text-bizit-gray">
                        <Search size={22} />
                    </div>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search price trends, FX gaps, or specific market reports..."
                        className="flex-1 py-5 px-4 bg-transparent border-none focus:ring-0 text-base font-medium placeholder:text-bizit-gray/50"
                    />
                    <div className="pr-2 flex items-center gap-2">
                        <BizitButton
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => window.location.href = '/upload'}
                            className="hover:text-bizit-green"
                            title="Ingest Intelligence"
                        >
                            <FileUp size={20} />
                        </BizitButton>
                        <BizitButton
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => setShowFilters(!showFilters)}
                            className={clsx(showFilters && "bg-bizit-dark/5 text-bizit-green")}
                        >
                            <Filter size={20} />
                        </BizitButton>
                        <BizitButton
                            type="submit"
                            isLoading={isLoading}
                            className="rounded-xl px-6 h-12"
                        >
                            Digest
                        </BizitButton>
                    </div>
                </div>

                {/* Quick Suggestions */}
                <div className="mt-3 flex flex-wrap gap-2 text-xs font-medium">
                    <button
                        type="button"
                        onClick={() => setQuery("Latest NGN inflation rate")}
                        className="px-3 py-1.5 rounded-full bg-bizit-dark/5 text-bizit-gray hover:bg-bizit-dark/10 transition-colors"
                    >
                        "Latest NGN inflation rate"
                    </button>
                    <button
                        type="button"
                        onClick={() => setQuery("Lagos real estate forecast 2026")}
                        className="px-3 py-1.5 rounded-full bg-bizit-dark/5 text-bizit-gray hover:bg-bizit-dark/10 transition-colors"
                    >
                        "Lagos real estate forecast 2026"
                    </button>
                </div>
            </form>

            {/* Advanced Filters */}
            {showFilters && (
                <div className="glass-card p-4 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in fade-in slide-in-from-top-4 duration-300">
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-bizit-gray uppercase tracking-wider flex items-center gap-1.5">
                            <Briefcase size={12} /> Domain
                        </label>
                        <select
                            value={domain}
                            onChange={(e) => setDomain(e.target.value)}
                            className="w-full bg-bizit-light border-none rounded-xl text-sm focus:ring-bizit-green"
                        >
                            <option>All</option>
                            <option>Finance & Banking</option>
                            <option>Consumer Goods</option>
                            <option>Real Estate</option>
                            <option>Tech & Telecoms</option>
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-bizit-gray uppercase tracking-wider flex items-center gap-1.5">
                            <Globe size={12} /> Geography
                        </label>
                        <select
                            value={region}
                            onChange={(e) => setRegion(e.target.value)}
                            className="w-full bg-bizit-light border-none rounded-xl text-sm focus:ring-bizit-green"
                        >
                            <option value="NG">Nigeria (Local)</option>
                            <option value="AF">Pan-Africa</option>
                            <option value="GL">Global Market</option>
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-bizit-gray uppercase tracking-wider flex items-center gap-1.5">
                            <Zap size={12} /> Strategic Mandate
                        </label>
                        <select
                            value={urgency}
                            onChange={(e) => setUrgency(e.target.value)}
                            className="w-full bg-bizit-light border-none rounded-xl text-sm focus:ring-bizit-green"
                        >
                            <option>Standard</option>
                            <option>GROWTH (Expansion Focus)</option>
                            <option>PRESERVE (Risk Mitigation)</option>
                            <option>ARBITRAGE (High Velocity)</option>
                        </select>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SearchBar;
