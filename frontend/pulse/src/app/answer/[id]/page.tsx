'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { usePulseStore } from '@/store/usePulseStore';
import ReportEngine from '@/components/report/ReportEngine';
import ReportSkeleton from '@/components/report/ReportSkeleton';
import BizitButton from '@/components/common/BizitButton';
import { ShieldAlert } from 'lucide-react';

export default function AnswerPage() {
    const { id } = useParams();
    const router = useRouter();
    const { history, activeReport, setActiveReport } = usePulseStore();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Find report in history if not active
        const report = history.find(r => r.id === id);
        if (report) {
            setActiveReport(report);
        } else if (!activeReport) {
            setError("Intelligence report not found in local cache.");
        }
    }, [id, history, activeReport, setActiveReport]);

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
                <div className="h-16 w-16 bg-red-50 text-urgency-red rounded-full flex items-center justify-center">
                    <ShieldAlert size={32} />
                </div>
                <div className="space-y-2">
                    <h2 className="text-xl font-bold text-bizit-dark tracking-tight">Record Desync</h2>
                    <p className="text-bizit-gray text-sm max-w-xs mx-auto">
                        The intelligence report you are looking for is no longer in the active pulse substrate.
                    </p>
                </div>
                <BizitButton onClick={() => router.push('/')} variant="primary">
                    Return to Search
                </BizitButton>
            </div>
        );
    }

    if (!activeReport) {
        return <ReportSkeleton />;
    }

    return (
        <div className="py-8">
            <ReportEngine report={activeReport} />
        </div>
    );
}
