'use client';

import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Search, Send, Loader2, CheckCircle2 } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';

interface Document {
    id: string;
    filename: string;
    type: string;
    timestamp: number;
    summary: string;
}

interface Message {
    query: string;
    answer: string;
    cited_docs?: string[];
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isQuerying, setIsQuerying] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            const response = await fetch('http://localhost:8002/documents');
            const data = await response.json();
            setDocuments(data.documents || []);
        } catch (error) {
            console.error('Failed to fetch documents:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (docId: string) => {
        try {
            await fetch(`http://localhost:8002/documents/${docId}`, { method: 'DELETE' });
            setDocuments(docs => docs.filter(d => d.id !== docId));
            setSelectedDocs(sel => sel.filter(id => id !== docId));
        } catch (error) {
            console.error('Failed to delete document:', error);
        }
    };

    const handleQuery = async () => {
        if (!query.trim()) return;

        setIsQuerying(true);
        try {
            const response = await fetch('http://localhost:8002/documents/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    doc_ids: selectedDocs,
                    history: messages
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                setMessages([...messages, { query, answer: data.answer, cited_docs: data.cited_docs }]);
                setQuery('');
            }
        } catch (error) {
            console.error('Query failed:', error);
        } finally {
            setIsQuerying(false);
        }
    };

    const toggleDoc = (docId: string) => {
        setSelectedDocs(prev =>
            prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]
        );
    };

    return (
        <div className="max-w-7xl mx-auto py-8 px-4">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-bizit-dark">Document Library</h1>
                <p className="text-bizit-gray text-sm mt-1">
                    Query your uploaded documents interactively
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Document Library */}
                <div className="lg:col-span-1 space-y-4">
                    <div className="glass-card p-4">
                        <h2 className="text-sm font-bold uppercase tracking-wider text-bizit-gray mb-3">
                            Your Documents ({documents.length})
                        </h2>

                        {loading ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="animate-spin text-bizit-gray" size={24} />
                            </div>
                        ) : documents.length === 0 ? (
                            <p className="text-sm text-bizit-gray/60 text-center py-8">
                                No documents uploaded yet
                            </p>
                        ) : (
                            <div className="space-y-2 max-h-[600px] overflow-y-auto">
                                {documents.map(doc => (
                                    <div
                                        key={doc.id}
                                        className={`p-3 rounded-xl border transition-all cursor-pointer ${selectedDocs.includes(doc.id)
                                                ? 'bg-bizit-green/10 border-bizit-green/40'
                                                : 'bg-white border-bizit-dark/5 hover:border-bizit-green/20'
                                            }`}
                                        onClick={() => toggleDoc(doc.id)}
                                    >
                                        <div className="flex items-start justify-between gap-2">
                                            <div className="flex items-start gap-2 flex-1 min-w-0">
                                                <div className={`p-1.5 rounded-lg shrink-0 ${selectedDocs.includes(doc.id) ? 'bg-bizit-green/20 text-bizit-green' : 'bg-bizit-light text-bizit-gray'
                                                    }`}>
                                                    {selectedDocs.includes(doc.id) ? (
                                                        <CheckCircle2 size={14} />
                                                    ) : (
                                                        <FileText size={14} />
                                                    )}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-xs font-medium text-bizit-dark truncate">
                                                        {doc.filename}
                                                    </p>
                                                    <p className="text-[10px] text-bizit-gray/60 mt-0.5">
                                                        {doc.type.toUpperCase()}
                                                    </p>
                                                </div>
                                            </div>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDelete(doc.id);
                                                }}
                                                className="p-1 hover:bg-red-50 rounded text-bizit-gray hover:text-red-600 transition-colors"
                                            >
                                                <Trash2 size={12} />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Query Interface */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="glass-card p-6 min-h-[600px] flex flex-col">
                        <h2 className="text-sm font-bold uppercase tracking-wider text-bizit-gray mb-4">
                            Ask Your Documents
                        </h2>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                            {messages.length === 0 ? (
                                <div className="flex items-center justify-center h-full text-center">
                                    <div className="space-y-2">
                                        <Search className="mx-auto text-bizit-gray/40" size={32} />
                                        <p className="text-sm text-bizit-gray/60">
                                            Select documents and ask questions
                                        </p>
                                        <p className="text-xs text-bizit-gray/40">
                                            {selectedDocs.length > 0
                                                ? `${selectedDocs.length} document${selectedDocs.length > 1 ? 's' : ''} selected`
                                                : 'No documents selected'}
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                messages.map((msg, idx) => (
                                    <div key={idx} className="space-y-3">
                                        <div className="flex justify-end">
                                            <div className="bg-bizit-green/10 border border-bizit-green/20 rounded-2xl px-4 py-2 max-w-[80%]">
                                                <p className="text-sm text-bizit-dark">{msg.query}</p>
                                            </div>
                                        </div>
                                        <div className="flex justify-start">
                                            <div className="bg-white border border-bizit-dark/5 rounded-2xl px-4 py-3 max-w-[80%]">
                                                <p className="text-sm text-bizit-dark leading-relaxed whitespace-pre-wrap">
                                                    {msg.answer}
                                                </p>
                                                {msg.cited_docs && msg.cited_docs.length > 0 && (
                                                    <div className="mt-2 pt-2 border-t border-bizit-dark/5">
                                                        <p className="text-[10px] text-bizit-gray/60 uppercase tracking-wider font-bold mb-1">
                                                            Sources
                                                        </p>
                                                        <div className="flex flex-wrap gap-1">
                                                            {msg.cited_docs.map((doc, i) => (
                                                                <span
                                                                    key={i}
                                                                    className="text-[10px] px-2 py-0.5 rounded-full bg-bizit-light text-bizit-gray"
                                                                >
                                                                    {doc}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                            {isQuerying && (
                                <div className="flex justify-start">
                                    <div className="bg-white border border-bizit-dark/5 rounded-2xl px-4 py-3">
                                        <Loader2 className="animate-spin text-bizit-gray" size={16} />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Query Input */}
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                                placeholder={selectedDocs.length > 0 ? "Ask your documents..." : "Select documents first..."}
                                disabled={selectedDocs.length === 0 || isQuerying}
                                className="flex-1 px-4 py-3 rounded-xl border border-bizit-dark/10 focus:border-bizit-green/40 focus:outline-none text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <BizitButton
                                onClick={handleQuery}
                                disabled={!query.trim() || selectedDocs.length === 0 || isQuerying}
                                className="px-4"
                            >
                                <Send size={16} />
                            </BizitButton>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
