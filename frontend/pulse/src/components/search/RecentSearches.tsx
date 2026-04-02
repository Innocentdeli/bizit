'use client';

import React from 'react';
import { useSession } from 'next-auth/react';
import { History, Search } from 'lucide-react';

interface RecentSearchesProps {
    onSelect: (query: string) => void;
}

export default function RecentSearches({ onSelect }: RecentSearchesProps) {
    const { data: session } = useSession();
    const [history, setHistory] = React.useState<string[]>([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const fetchHistory = async () => {
            if (!session?.user) return;
            try {
                const res = await fetch(`http://localhost:8002/search/history?user_id=${session.user.email || 'anonymous'}`);
                if (res.ok) {
                    const data = await res.json();
                    setHistory(data.history || []);
                }
            } catch (err) {
                console.error("Failed to fetch search intelligence history:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [session]);

    if (!session || history.length === 0) return null;

    return (
        <div className="mt-8 w-full max-w-2xl animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex items-center gap-2 mb-3 text-bizit-gray px-4">
                <History size={14} />
                <span className="text-xs font-bold uppercase tracking-widest">Your Recent Intelligence</span>
            </div>

            <div className="bg-white rounded-2xl border border-bizit-dark/5 shadow-sm overflow-hidden">
                {history.map((query, idx) => (
                    <button
                        key={idx}
                        onClick={() => onSelect(query)}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-bizit-light transition-colors text-left border-b last:border-0 border-gray-50"
                    >
                        <div className="h-8 w-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400">
                            <Search size={14} />
                        </div>
                        <span className="text-sm text-bizit-dark font-medium">{query}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
