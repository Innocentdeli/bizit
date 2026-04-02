'use client';

import React from 'react';

export default function ReportSkeleton() {
    return (
        <div className="max-w-4xl mx-auto space-y-12 pb-20 animate-pulse">
            {/* Navigation Skeleton */}
            <div className="flex items-center justify-between border-b pb-4">
                <div className="h-4 w-24 bg-gray-200 rounded" />
                <div className="flex items-center gap-2">
                    <div className="h-8 w-20 bg-gray-200 rounded-lg" />
                    <div className="h-8 w-20 bg-gray-200 rounded-lg" />
                </div>
            </div>

            {/* Summary Skeleton */}
            <div className="space-y-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-3">
                        <div className="flex items-center gap-2">
                            <div className="h-4 w-16 bg-bizit-green/10 rounded" />
                            <div className="h-4 w-20 bg-gray-100 rounded" />
                        </div>
                        <div className="h-8 w-64 bg-gray-200 rounded-lg" />
                    </div>
                    <div className="h-16 w-32 bg-gray-100 rounded-2xl" />
                </div>
                <div className="h-32 w-full bg-gray-50 rounded-2xl border border-gray-100" />
            </div>

            {/* Grid Content Skeleton */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="h-64 bg-gray-50 rounded-3xl border border-gray-100" />
                <div className="h-64 bg-gray-900/5 rounded-3xl border border-gray-100" />
            </div>

            {/* Matrix Skeleton */}
            <div className="h-48 w-full bg-gray-50 rounded-3xl border border-gray-100" />
        </div>
    );
}
