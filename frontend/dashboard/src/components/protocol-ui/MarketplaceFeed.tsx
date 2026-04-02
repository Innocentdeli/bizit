import React, { useState, useEffect } from "react";
import { useAccount, useReadContract, useReadContracts } from "wagmi";
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { Search, Filter, TrendingUp, Package, Briefcase, Gem } from "lucide-react";
import { MARKETPLACE_KERNEL_ABI } from "../../constants/abis";
import addresses from "../../constants/addresses.json";

interface Listing {
    id: string;
    seller: string;
    category: number;
    basePrice: string;
    metadataURI: string;
    active: boolean;
    metadata?: {
        title: string;
        description: string;
        category: string;
        [key: string]: any;
    };
}

export default function MarketplaceFeed() {
    const { address, isConnected } = useAccount();
    const [listings, setListings] = useState<Listing[]>([]);
    const [filter, setFilter] = useState<"ALL" | "PRODUCTS" | "SERVICES" | "ASSETS">("ALL");

    // 1. Fetch Total Listings Count
    const { data: totalListingsCount, refetch: refetchCount } = useReadContract({
        address: addresses.kernel as `0x${string}`,
        abi: MARKETPLACE_KERNEL_ABI,
        functionName: 'totalListings',
    });

    // 2. Prepare Multi-Read for Listings
    const listingCount = Number(totalListingsCount || 0n);
    const listingsToFetch = Array.from({ length: listingCount }, (_, i) => i + 1);

    const { data: rawListings, isLoading } = useReadContracts({
        contracts: listingsToFetch.map(id => ({
            address: addresses.kernel as `0x${string}`,
            abi: MARKETPLACE_KERNEL_ABI,
            functionName: 'getListing',
            args: [BigInt(id)],
        }))
    });

    // 3. Process Raw Blockchain Data
    useEffect(() => {
        if (!rawListings) return;

        const processedListings = rawListings.map((res: any, idx: number) => {
            const data = res.result;
            if (!data) return null;

            return {
                id: data.id.toString(),
                seller: data.seller,
                category: data.category,
                basePrice: data.basePrice.toString(),
                metadataURI: data.metadataURI,
                active: data.active,
                metadata: {
                    title: `Listing #${data.id}`,
                    description: data.metadataURI.includes("ipfs")
                        ? "Protocol Listing stored on IPFS."
                        : "Marketplace Kernel Listing.",
                    category: ["product", "service", "asset"][data.category % 3]
                }
            };
        }).filter(Boolean) as Listing[];

        setListings(processedListings.reverse()); // Newest first
    }, [rawListings]);

    const getCategoryIcon = (category: number) => {
        switch (category) {
            case 0: return <Package className="w-5 h-5" />;
            case 1: return <Briefcase className="w-5 h-5" />;
            case 2: return <Gem className="w-5 h-5" />;
            default: return <TrendingUp className="w-5 h-5" />;
        }
    };

    const getCategoryColor = (category: number) => {
        switch (category) {
            case 0: return "emerald";
            case 1: return "blue";
            case 2: return "purple";
            default: return "gray";
        }
    };

    const filteredListings = listings.filter(listing => {
        if (filter === "ALL") return true;
        if (filter === "PRODUCTS") return listing.category === 0;
        if (filter === "SERVICES") return listing.category === 1;
        if (filter === "ASSETS") return listing.category === 2;
        return true;
    });

    return (
        <div className="flex flex-col h-full gap-8">
            {/* Header */}
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-black italic tracking-tighter text-white">
                        UNIVERSAL MARKETPLACE
                    </h1>
                    <p className="text-[10px] text-white/40 uppercase tracking-widest mt-1">
                        Protocol-First Decentralized Commerce
                    </p>
                </div>
                <ConnectButton />
            </header>

            {/* Stats Bar */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 border border-white/10 bg-white/5 rounded-xl">
                    <div className="text-[8px] uppercase tracking-widest text-white/40 mb-1">Total Listings</div>
                    <div className="text-2xl font-black text-white">{listings.length}</div>
                </div>
                <div className="p-4 border border-emerald-500/20 bg-emerald-500/5 rounded-xl">
                    <div className="text-[8px] uppercase tracking-widest text-emerald-400/60 mb-1">Products</div>
                    <div className="text-2xl font-black text-emerald-400">
                        {listings.filter(l => l.category === 0).length}
                    </div>
                </div>
                <div className="p-4 border border-blue-500/20 bg-blue-500/5 rounded-xl">
                    <div className="text-[8px] uppercase tracking-widest text-blue-400/60 mb-1">Services</div>
                    <div className="text-2xl font-black text-blue-400">
                        {listings.filter(l => l.category === 1).length}
                    </div>
                </div>
                <div className="p-4 border border-purple-500/20 bg-purple-500/5 rounded-xl">
                    <div className="text-[8px] uppercase tracking-widest text-purple-400/60 mb-1">Assets</div>
                    <div className="text-2xl font-black text-purple-400">
                        {listings.filter(l => l.category === 2).length}
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="flex bg-black/40 p-1 rounded-xl border border-white/10">
                    {(["ALL", "PRODUCTS", "SERVICES", "ASSETS"] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setFilter(tab)}
                            className={`px-4 py-2 rounded-lg text-[9px] font-bold tracking-widest uppercase transition-all ${filter === tab
                                ? 'bg-white/10 text-white border border-white/20'
                                : 'text-white/40 hover:text-white'
                                }`}
                        >
                            {tab}
                        </button>
                    ))}
                </div>
                <div className="flex-1" />
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-white/40" />
                    <input
                        placeholder="Search marketplace..."
                        className="bg-black/40 border border-white/10 rounded-lg py-2 pl-9 pr-4 text-[10px] text-white focus:outline-none focus:border-white/30"
                    />
                </div>
            </div>

            {/* Listings Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 flex-1 overflow-y-auto">
                {filteredListings.map((listing) => {
                    const color = getCategoryColor(listing.category);
                    return (
                        <div
                            key={listing.id}
                            className="group p-6 border border-white/10 bg-white/5 rounded-2xl hover:bg-white/10 transition-all cursor-pointer"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className={`p-3 rounded-xl border border-${color}-500/20 bg-${color}-500/10 text-${color}-400`}>
                                    {getCategoryIcon(listing.category)}
                                </div>
                                <div className="text-[8px] uppercase tracking-widest text-white/40">
                                    #{listing.id}
                                </div>
                            </div>

                            <h3 className="text-sm font-bold text-white mb-2 group-hover:text-white/90">
                                {listing.metadata?.title || "Untitled Listing"}
                            </h3>

                            <p className="text-[10px] text-white/60 mb-4 line-clamp-2">
                                {listing.metadata?.description || "No description available"}
                            </p>

                            <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                <div>
                                    <div className="text-[8px] uppercase tracking-widest text-white/40 mb-1">Price</div>
                                    <div className="text-sm font-bold text-white">
                                        {(parseInt(listing.basePrice) / 1e18).toFixed(2)} ETH
                                    </div>
                                </div>
                                <button className={`px-4 py-2 rounded-lg bg-${color}-500/20 border border-${color}-500/30 text-${color}-400 text-[9px] font-bold uppercase tracking-widest hover:bg-${color}-500/30 transition-all`}>
                                    View
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
