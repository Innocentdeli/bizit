'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { CheckCircle, MapPin, Star, Share2, Phone, Globe } from 'lucide-react';
import BizitButton from '@/components/common/BizitButton';
import ClaimModal from '@/components/modules/ClaimModal';
import ReviewSection from '@/components/modules/ReviewSection';
import { fetchAPI } from '@/lib/api';

export default function BusinessProfilePage() {
    const params = useParams();
    const id = params?.id as string || 'unknown';
    const [isClaimModalOpen, setIsClaimModalOpen] = useState(false);
    const [business, setBusiness] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        async function loadBusiness() {
            setLoading(true);
            const data = await fetchAPI(`/business/${id}`);
            if (data && data.data) {
                setBusiness(data.data);
            }
            setLoading(false);
        }
        loadBusiness();
    }, [id]);

    if (loading) return <div className="p-20 text-center">Loading Business Profile...</div>;
    if (!business) return <div className="p-20 text-center">Business Not Found</div>;

    return (
        <div className="max-w-4xl mx-auto pb-20">
            {/* Header Image */}
            <div className="h-48 md:h-64 bg-slate-200 rounded-3xl w-full mb-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-6 left-6 md:left-10 text-white">
                    <h1 className="text-3xl md:text-4xl font-bold">{business.name}</h1>
                    <div className="flex items-center gap-2 mt-2 text-sm opacity-90">
                        <span>{business.category}</span>
                        <span>•</span>
                        <div className="flex items-center gap-1 text-yellow-400">
                            <Star size={14} fill="currentColor" />
                            <span>{business.rating} ({business.review_count || 0} reviews)</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Main Content */}
                <div className="md:col-span-2 space-y-8">
                    <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                        <div className="flex items-start justify-between">
                            <h2 className="font-bold text-lg text-bizit-dark">About</h2>
                            {business.verified && (
                                <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-bizit-green bg-bizit-green/10 px-2 py-1 rounded-full">
                                    <CheckCircle size={12} /> Verified Owner
                                </span>
                            )}
                        </div>
                        <p className="text-bizit-gray leading-relaxed text-sm md:text-base">
                            {business.description}
                        </p>
                    </div>

                    {business.services && (
                        <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-4">
                            <h2 className="font-bold text-lg text-bizit-dark">Services & Amenities</h2>
                            <div className="grid grid-cols-2 gap-3">
                                {business.services.map((s: string) => (
                                    <div key={s} className="flex items-center gap-2 text-sm text-bizit-gray">
                                        <div className="w-1.5 h-1.5 rounded-full bg-bizit-green" />
                                        {s}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Module 5: Reviews */}
                    <ReviewSection businessId={id} />
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-6">
                        <div className="space-y-4">
                            <div className="flex items-center gap-3 text-sm text-bizit-dark">
                                <MapPin className="text-bizit-gray" size={18} />
                                <span>{business.location}</span>
                            </div>
                            {business.phone && (
                                <div className="flex items-center gap-3 text-sm text-bizit-dark">
                                    <Phone className="text-bizit-gray" size={18} />
                                    <span>{business.phone}</span>
                                </div>
                            )}
                            {business.website && (
                                <div className="flex items-center gap-3 text-sm text-bizit-dark">
                                    <Globe className="text-bizit-gray" size={18} />
                                    <a href={`http://${business.website}`} target="_blank" className="text-bizit-green hover:underline">{business.website}</a>
                                </div>
                            )}
                        </div>

                        <div className="pt-4 border-t">
                            <p className="text-xs font-bold text-green-600 mb-4">{business.hours || 'Open Now'}</p>
                            <div className="grid grid-cols-2 gap-2">
                                <BizitButton variant="primary" className="w-full">Contact</BizitButton>
                                <BizitButton variant="outline" className="w-full"><Share2 size={16} /></BizitButton>
                            </div>
                        </div>
                    </div>

                    <div className="bg-bizit-gold/10 p-6 rounded-2xl border border-bizit-gold/20">
                        <h3 className="font-bold text-bizit-gold text-sm mb-2">Claim This Business?</h3>
                        <p className="text-xs text-bizit-dark/70 mb-4">Manage this profile, respond to reviews, and track analytics.</p>
                        <BizitButton
                            variant="secondary"
                            size="sm"
                            className="w-full bg-white border-none text-bizit-dark"
                            onClick={() => setIsClaimModalOpen(true)}
                        >
                            Manage Listing
                        </BizitButton>
                    </div>
                </div>
            </div>

            <ClaimModal
                isOpen={isClaimModalOpen}
                onClose={() => setIsClaimModalOpen(false)}
                businessName={business.name}
            />
        </div>
    );
}
