import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { PulseState, IntelligenceReport, PersonalizationData } from '@/types';

export const usePulseStore = create<PulseState>()(
  devtools(
    persist(
      (set) => ({
        // Initial State
        history: [],
        activeReport: null,
        isThinking: false,
        thinkingProgress: 0,
        currentQuery: '',
        isLoading: false,
        personalization: {
          objective: 'Sovereign Market Intelligence',
          region: 'NG',
          strategy: 'GROWTH'
        },

        // Actions
        setHistory: (history) => set({ history }),

        addReport: (report) => set((state) => ({
          history: [report, ...state.history.slice(0, 49)] // Keep last 50
        })),

        setActiveReport: (report) => set({ activeReport: report }),

        setIsThinking: (isThinking) => set({ isThinking }),

        setThinkingProgress: (thinkingProgress) => set({ thinkingProgress }),

        setCurrentQuery: (currentQuery) => set({ currentQuery }),

        setPersonalization: (personalization) => set({ personalization }),

        setIsLoading: (isLoading) => set({ isLoading }),
      }),
      { name: 'BizitPulseStore' }
    ),
    { name: 'PulseStore' }
  )
);
