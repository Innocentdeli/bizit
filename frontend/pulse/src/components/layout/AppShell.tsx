import React from 'react';
import Navbar from './Navbar';

interface AppShellProps {
    children: React.ReactNode;
}

const AppShell = ({ children }: AppShellProps) => {
    return (
        <div className="min-h-screen bg-bizit-light flex flex-col">
            <Navbar />
            <main className="flex-1 pt-4 pb-20 md:pt-20 md:pb-8">
                <div className="mx-auto max-w-5xl px-4 md:px-8">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default AppShell;
