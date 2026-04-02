'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, ArrowRight } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import UploadSuccess from '@/components/upload/UploadSuccess';
import { clsx } from 'clsx';

export default function UploadPage() {
    const router = useRouter();
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [fileName, setFileName] = useState<string | null>(null);
    const [fileObj, setFileObj] = useState<File | null>(null);
    const [uploadResponse, setUploadResponse] = useState<any>(null);

    const handleUpload = async () => {
        if (!fileObj) return;

        setIsUploading(true);
        setUploadStatus('idle');

        try {
            const formData = new FormData();
            formData.append('file', fileObj);

            const response = await fetch('http://localhost:8002/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setUploadResponse(data);
                setUploadStatus('success');
            } else {
                setUploadStatus('error');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            setUploadStatus('error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleSearch = (query: string) => {
        router.push(`/?q=${encodeURIComponent(query)}`);
    };

    const handleClose = () => {
        setUploadStatus('idle');
        setFileName(null);
        setFileObj(null);
        setUploadResponse(null);
    };

    const handleViewLibrary = () => {
        router.push('/documents');
    };

    return (
        <div className="max-w-2xl mx-auto py-12 space-y-12">
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-bold text-bizit-dark tracking-tight">Intelligence Ingestion</h1>
                <p className="text-bizit-gray text-sm">
                    Upload PDF, DOCX, or CSV files for deep crossover analysis by the Sovereign Kernel.
                </p>
            </div>

            <div
                className={clsx(
                    "relative group border-2 border-dashed rounded-3xl p-12 transition-all flex flex-col items-center justify-center space-y-4",
                    uploadStatus === 'success' ? "border-bizit-green/40 bg-bizit-green/5" : "border-bizit-dark/10 hover:border-bizit-green/40 bg-white"
                )}
            >
                {uploadStatus === 'idle' && (
                    <>
                        <div className="h-16 w-16 rounded-2xl bg-bizit-light flex items-center justify-center text-bizit-gray group-hover:text-bizit-green transition-colors">
                            <Upload size={32} />
                        </div>
                        <div className="text-center">
                            <p className="font-semibold text-bizit-dark">Drag & drop market files here</p>
                            <p className="text-xs text-bizit-gray/50 mt-1">Maximum file size: 25MB</p>
                        </div>
                        <input
                            type="file"
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            onChange={(e) => {
                                const file = e.target.files?.[0] || null;
                                setFileName(file?.name || null);
                                setFileObj(file);
                            }}
                        />
                    </>
                )}

                {isUploading && (
                    <div className="text-center space-y-4">
                        <Loader2 className="animate-spin text-bizit-green mx-auto" size={40} />
                        <div className="space-y-1">
                            <p className="font-bold text-bizit-dark">Ingesting Documents...</p>
                            <p className="text-xs text-bizit-gray/60 animate-pulse">Scanning for strategic vectors & market signals</p>
                        </div>
                    </div>
                )}

                {uploadStatus === 'success' && uploadResponse && (
                    <UploadSuccess
                        filename={uploadResponse.filename || fileName || 'Unknown file'}
                        batchSize={uploadResponse.batch_size || 1}
                        summary={uploadResponse.summary || 'File processed successfully.'}
                        suggestedQueries={uploadResponse.suggested_queries || []}
                        onSearch={handleSearch}
                        onClose={handleClose}
                        onViewLibrary={handleViewLibrary}
                    />
                )}

                {uploadStatus === 'success' && !uploadResponse && (
                    <div className="text-center space-y-4 animate-in fade-in zoom-in duration-500">
                        <div className="h-16 w-16 rounded-full bg-bizit-green/10 text-bizit-green flex items-center justify-center mx-auto">
                            <CheckCircle2 size={32} />
                        </div>
                        <div className="space-y-1">
                            <p className="font-bold text-bizit-dark">Ingestion Complete</p>
                            <p className="text-xs text-bizit-gray/60">{fileName || "document_analysis.pdf"} is now parsed.</p>
                        </div>
                        <BizitButton className="gap-2 px-8" onClick={() => router.push('/')}>
                            Generate Analysis Report <ArrowRight size={18} />
                        </BizitButton>
                    </div>
                )}
            </div>

            {fileName && uploadStatus === 'idle' && !isUploading && (
                <div className="flex items-center justify-between p-4 bg-white rounded-2xl border border-bizit-green/20 shadow-sm animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-bizit-green/10 text-bizit-green">
                            <FileText size={20} />
                        </div>
                        <span className="text-sm font-medium text-bizit-dark truncate max-w-xs">{fileName}</span>
                    </div>
                    <BizitButton size="sm" onClick={handleUpload}>Process</BizitButton>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-8">
                <div className="p-4 rounded-2xl bg-white border border-bizit-dark/5 space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-bizit-dark">Security Protocol</h4>
                    <p className="text-[11px] text-bizit-gray leading-relaxed">
                        All files are processed in a sovereign sandbox and encrypted at rest. No data is used for public model training.
                    </p>
                </div>
                <div className="p-4 rounded-2xl bg-white border border-bizit-dark/5 space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-bizit-dark">AI Capabilities</h4>
                    <p className="text-[11px] text-bizit-gray leading-relaxed">
                        Sovereign Kernel parses tables, legal nuances, and pricing trends with 99.2% accuracy.
                    </p>
                </div>
            </div>
        </div>
    );
}
