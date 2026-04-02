'use client';

import React, { useState } from 'react';
import { X, ShieldCheck, Phone, Mail, FileText } from 'lucide-react';
import BizitButton from '../common/BizitButton';

interface ClaimModalProps {
    isOpen: boolean;
    onClose: () => void;
    businessName: string;
}

const ClaimModal = ({ isOpen, onClose, businessName }: ClaimModalProps) => {
    const [step, setStep] = useState(1);
    const [method, setMethod] = useState<'phone' | 'email' | 'doc' | null>(null);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl border border-bizit-dark/10 animate-in fade-in zoom-in duration-300">

                {/* Header */}
                <div className="bg-bizit-gold/10 p-6 border-b border-bizit-gold/20 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-bizit-gold">
                        <ShieldCheck size={24} />
                        <h2 className="font-bold text-lg">Claim {businessName}</h2>
                    </div>
                    <button onClick={onClose} className="text-bizit-dark/50 hover:text-bizit-dark transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {step === 1 && (
                        <div className="space-y-4">
                            <p className="text-sm text-bizit-gray text-center">
                                Select a verification method to prove ownership. We will send a code or request a document.
                            </p>
                            <div className="space-y-3">
                                <button
                                    onClick={() => setMethod('phone')}
                                    className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all ${method === 'phone' ? 'border-bizit-gold bg-bizit-gold/5 ring-1 ring-bizit-gold' : 'border-bizit-dark/10 hover:border-bizit-gold/50'}`}
                                >
                                    <div className="bg-white p-2 rounded-full shadow-sm"><Phone size={18} className="text-bizit-dark" /></div>
                                    <div className="text-left">
                                        <p className="text-sm font-bold text-bizit-dark">Phone Verification</p>
                                        <p className="text-xs text-bizit-gray">SMS to registered number •••• 88</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => setMethod('email')}
                                    className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all ${method === 'email' ? 'border-bizit-gold bg-bizit-gold/5 ring-1 ring-bizit-gold' : 'border-bizit-dark/10 hover:border-bizit-gold/50'}`}
                                >
                                    <div className="bg-white p-2 rounded-full shadow-sm"><Mail size={18} className="text-bizit-dark" /></div>
                                    <div className="text-left">
                                        <p className="text-sm font-bold text-bizit-dark">Email Verification</p>
                                        <p className="text-xs text-bizit-gray">Code to •••@domain.com</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => setMethod('doc')}
                                    className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all ${method === 'doc' ? 'border-bizit-gold bg-bizit-gold/5 ring-1 ring-bizit-gold' : 'border-bizit-dark/10 hover:border-bizit-gold/50'}`}
                                >
                                    <div className="bg-white p-2 rounded-full shadow-sm"><FileText size={18} className="text-bizit-dark" /></div>
                                    <div className="text-left">
                                        <p className="text-sm font-bold text-bizit-dark">Document Upload</p>
                                        <p className="text-xs text-bizit-gray">CAC Certificate or Utility Bill</p>
                                    </div>
                                </button>
                            </div>
                            <BizitButton
                                variant="primary"
                                className="w-full bg-bizit-gold text-white hover:bg-bizit-gold/90 border-none"
                                onClick={() => method && setStep(2)}
                                disabled={!method}
                            >
                                Continue to Verify
                            </BizitButton>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-6 text-center">
                            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center text-green-600 animate-pulse">
                                <ShieldCheck size={32} />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-bizit-dark">Verification Initiated</h3>
                                <p className="text-sm text-bizit-gray mt-2">
                                    We have sent a verification request via <strong>{method}</strong>.
                                    Check your inbox/SMS to complete the claiming process.
                                </p>
                            </div>
                            <BizitButton variant="outline" className="w-full" onClick={onClose}>
                                Close
                            </BizitButton>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ClaimModal;
