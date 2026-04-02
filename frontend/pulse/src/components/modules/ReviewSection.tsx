'use client';

import React, { useState } from 'react';
import { Star, ThumbsUp, MessageSquare } from 'lucide-react';
import BizitButton from '../common/BizitButton';

interface Review {
    id: string;
    user_name: string;
    rating: number;
    comment: string;
    timestamp: number;
    helpful_count: number;
}

interface ReviewSectionProps {
    businessId: string;
}

const ReviewSection = ({ businessId }: ReviewSectionProps) => {
    // Mock initial state (In real app, fetch from API)
    const [reviews, setReviews] = useState<Review[]>([
        {
            id: 'r1',
            user_name: 'Emeka O.',
            rating: 5,
            comment: 'Excellent internet speed and great community vibe. Highly recommend for startups.',
            timestamp: Date.now() - 86400000 * 2,
            helpful_count: 12
        },
        {
            id: 'r2',
            user_name: 'Sarah J.',
            rating: 4,
            comment: 'Good facilities but the coffee machine is often broken. Otherwise perfect.',
            timestamp: Date.now() - 86400000 * 5,
            helpful_count: 3
        }
    ]);

    const [newComment, setNewComment] = useState('');
    const [newRating, setNewRating] = useState(5);

    const handleSubmit = () => {
        if (!newComment) return;
        const newReview: Review = {
            id: `new-${Date.now()}`,
            user_name: 'You',
            rating: newRating,
            comment: newComment,
            timestamp: Date.now(),
            helpful_count: 0
        };
        setReviews([newReview, ...reviews]);
        setNewComment('');
    };

    return (
        <div className="bg-white p-6 rounded-2xl border border-bizit-dark/5 shadow-sm space-y-6">
            <h2 className="font-bold text-lg text-bizit-dark flex items-center gap-2">
                <Star className="text-bizit-green" fill="currentColor" size={20} />
                Reviews & Ratings
            </h2>

            {/* Submission Form */}
            <div className="p-4 bg-gray-50 rounded-xl space-y-3">
                <h3 className="text-sm font-bold text-bizit-dark">Write a Review</h3>
                <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map(r => (
                        <button key={r} onClick={() => setNewRating(r)}>
                            <Star size={20} className={r <= newRating ? 'text-yellow-400' : 'text-gray-300'} fill={r <= newRating ? 'currentColor' : 'none'} />
                        </button>
                    ))}
                </div>
                <textarea
                    className="w-full p-3 text-sm border rounded-lg outline-none focus:border-bizit-green bg-white"
                    rows={3}
                    placeholder="Share your experience..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                />
                <BizitButton variant="primary" size="sm" onClick={handleSubmit}>Post Review</BizitButton>
            </div>

            {/* Review List */}
            <div className="space-y-4">
                {reviews.map(review => (
                    <div key={review.id} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0 animate-in fade-in slide-in-from-bottom-2">
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2">
                                <div className="w-8 h-8 rounded-full bg-bizit-dark/10 flex items-center justify-center font-bold text-xs text-bizit-dark">
                                    {review.user_name[0]}
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-bizit-dark">{review.user_name}</p>
                                    <div className="flex text-yellow-400">
                                        {[...Array(5)].map((_, i) => (
                                            <Star key={i} size={10} fill={i < review.rating ? 'currentColor' : 'none'} className={i < review.rating ? '' : 'text-gray-200'} />
                                        ))}
                                    </div>
                                </div>
                            </div>
                            <span className="text-[10px] text-bizit-gray">{new Date(review.timestamp).toLocaleDateString()}</span>
                        </div>
                        <p className="text-sm text-bizit-gray mt-2 pl-10">{review.comment}</p>
                        <div className="flex items-center gap-4 mt-2 pl-10">
                            <button className="flex items-center gap-1 text-[10px] text-bizit-gray hover:text-bizit-green transition-colors">
                                <ThumbsUp size={12} /> Helpful ({review.helpful_count})
                            </button>
                            <button className="flex items-center gap-1 text-[10px] text-bizit-gray hover:text-bizit-dark transition-colors">
                                <MessageSquare size={12} /> Reply
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReviewSection;
