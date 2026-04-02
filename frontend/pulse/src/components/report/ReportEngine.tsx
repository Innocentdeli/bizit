'use client';

import React from 'react';
import { motion, Variants } from 'framer-motion';
import { IntelligenceReport } from '@/types';
import SummaryBlock from './SummaryBlock';
import ForecastBlock from './ForecastBlock';
import VeracityMatrix from './VeracityMatrix';
import BizitButton from '../common/BizitButton';
import { Download, Share2, MessageSquare, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface ReportEngineProps {
    report: IntelligenceReport;
}

const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.15,
            delayChildren: 0.1
        }
    }
};

const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
    }
};

const ReportEngine = ({ report }: ReportEngineProps) => {
    return (
        <motion.div
            className="max-w-4xl mx-auto space-y-12 pb-20"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
        >
            {/* Navigation & Actions */}
            <motion.div variants={itemVariants} className="flex items-center justify-between border-b pb-4">
                <Link href="/" className="flex items-center gap-2 text-bizit-gray hover:text-bizit-dark transition-colors">
                    <ArrowLeft size={18} />
                    <span className="text-sm font-medium">New Search</span>
                </Link>
                <div className="flex items-center gap-2">
                    <BizitButton variant="outline" size="sm" className="gap-2">
                        <Download size={16} /> Export
                    </BizitButton>
                    <BizitButton variant="outline" size="sm" className="gap-2">
                        <Share2 size={16} /> Share
                    </BizitButton>
                </div>
            </motion.div>

            {/* Main Content Sections */}
            <motion.section variants={itemVariants}>
                <SummaryBlock report={report} />
            </motion.section>

            <motion.section variants={itemVariants}>
                <ForecastBlock report={report} />
            </motion.section>

            <motion.section variants={itemVariants}>
                <VeracityMatrix report={report} />
            </motion.section>

            {/* Feedback / Interaction */}
            <motion.div
                variants={itemVariants}
                className="glass-card p-6 flex flex-col md:flex-row items-center justify-between gap-6 bg-bizit-green/5 border-bizit-green/20"
            >
                <div className="space-y-1 text-center md:text-left">
                    <h4 className="font-semibold text-bizit-dark text-sm md:text-base">Was this intelligence actionable?</h4>
                    <p className="text-xs text-bizit-gray/60">Your feedback calibrate the sovereign kernel.</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    <BizitButton variant="outline" size="sm" className="bg-white border-green-200">Yes, accurate</BizitButton>
                    <BizitButton variant="outline" size="sm" className="bg-white border-red-200">No, incorrect</BizitButton>
                    <BizitButton variant="secondary" size="sm" className="gap-2">
                        <MessageSquare size={16} /> Refine Digest
                    </BizitButton>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default ReportEngine;
