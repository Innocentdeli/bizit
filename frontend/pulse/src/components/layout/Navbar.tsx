'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Upload, History, User, Activity, FileText, Map, Building2, BarChart3, LayoutDashboard, Terminal, Megaphone, PlusCircle, Settings, LogOut } from 'lucide-react';
import { clsx } from 'clsx';
import BizitButton from '@/components/common/BizitButton';
import { useSession, signOut } from 'next-auth/react';

// Group 1: Discovery (Consumer/Market View)
const discoveryNav = [
    { label: 'Search', href: '/', icon: Search },
    { label: 'Map', href: '/map', icon: Map },
    { label: 'Market', href: '/market', icon: BarChart3 },
    { label: 'Directory', href: '/business', icon: Building2 },
];

// Group 2: Business Management (Owner View)
const businessNav = [
    { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { label: 'Ads', href: '/ads', icon: Megaphone },
    { label: 'Dev', href: '/developer', icon: Terminal },
];

// Group 3: Tools & Profile
const toolsNav = [
    { label: 'Alerts', href: '/notifications', icon: Activity },
    { label: 'Library', href: '/documents', icon: FileText },
];

const Navbar = () => {
    const pathname = usePathname();
    const { data: session } = useSession();
    const user: any = session?.user;

    // Hide Navbar on Login page
    if (pathname === '/login') return null;

    const NavItem = ({ item, minimal = false }: { item: any, minimal?: boolean }) => {
        const isActive = pathname === item.href;
        const Icon = item.icon;
        return (
            <Link
                href={item.href}
                className={clsx(
                    'flex items-center gap-2 px-3 py-2 rounded-lg transition-all',
                    isActive
                        ? 'bg-bizit-green/10 text-bizit-green font-medium'
                        : 'text-bizit-gray hover:bg-gray-50 hover:text-bizit-dark'
                )}
            >
                <Icon size={20} />
                {!minimal && <span className="text-sm">{item.label}</span>}
            </Link>
        );
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200">
            <div className="mx-auto max-w-7xl px-4 h-16 flex items-center justify-between">

                {/* 1. Logo & Discovery */}
                <div className="flex items-center gap-8">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bizit-green text-white">
                            <Activity size={20} />
                        </div>
                        <span className="text-lg font-bold tracking-tight text-bizit-dark hidden md:block">
                            Bizit<span className="text-bizit-green">Pulse</span>
                        </span>
                    </Link>

                    {/* Desktop Discovery Nav */}
                    <div className="hidden md:flex items-center gap-1 bg-gray-50/50 p-1 rounded-xl border border-gray-100">
                        {discoveryNav.map((item) => <NavItem key={item.href} item={item} />)}
                    </div>
                </div>

                {/* 2. Business Tools (Right Side) */}
                <div className="flex items-center gap-4">
                    {session ? (
                        <>
                            {/* Desktop Business Nav - Only if Business User */}
                            {user?.role === 'BUSINESS' && (
                                <div className="hidden md:flex items-center gap-1 pr-4 border-r border-gray-200">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mr-2">Business</span>
                                    {businessNav.map((item) => <NavItem key={item.href} item={item} minimal />)}
                                </div>
                            )}

                            {/* Alert & Profile */}
                            <div className="flex items-center gap-2">
                                <Link href="/notifications" className="relative p-2 text-bizit-gray hover:text-bizit-dark hover:bg-gray-100 rounded-full transition-colors">
                                    <Activity size={20} />
                                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                                </Link>

                                <div
                                    className="h-8 w-8 rounded-full bg-slate-200 overflow-hidden border border-gray-200 cursor-pointer hover:ring-2 ring-bizit-green transition-all"
                                    onClick={() => signOut({ callbackUrl: '/' })}
                                    title="Click to Logout"
                                >
                                    {/* User Initials or Avatar */}
                                    <div className="w-full h-full bg-gradient-to-tr from-bizit-dark to-slate-500 flex items-center justify-center text-white text-xs font-bold">
                                        {user?.role === 'BUSINESS' ? 'B' : 'C'}
                                    </div>
                                </div>
                            </div>
                        </>
                    ) : (
                        <Link href="/login">
                            <BizitButton variant="primary" size="sm">Login / Join</BizitButton>
                        </Link>
                    )}
                </div>
            </div>

            {/* Mobile Bottom Nav (Simplified) */}
            <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 pb-safe">
                <div className="flex justify-around p-3">
                    <Link href="/" className={clsx('flex flex-col items-center gap-1', pathname === '/' ? 'text-bizit-green' : 'text-gray-400')}>
                        <Search size={22} />
                        <span className="text-[10px] font-medium">Explore</span>
                    </Link>
                    <Link href="/map" className={clsx('flex flex-col items-center gap-1', pathname === '/map' ? 'text-bizit-green' : 'text-gray-400')}>
                        <Map size={22} />
                        <span className="text-[10px] font-medium">Map</span>
                    </Link>
                    {user?.role === 'BUSINESS' ? (
                        <Link href="/dashboard" className={clsx('flex flex-col items-center gap-1', pathname === '/dashboard' ? 'text-bizit-green' : 'text-gray-400')}>
                            <LayoutDashboard size={22} />
                            <span className="text-[10px] font-medium">Manage</span>
                        </Link>
                    ) : (
                        <Link href={session ? "/profile" : "/login"} className={clsx('flex flex-col items-center gap-1', pathname === '/login' || pathname === '/profile' ? 'text-bizit-green' : 'text-gray-400')}>
                            <User size={22} />
                            <span className="text-[10px] font-medium">{session ? 'Profile' : 'Login'}</span>
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
