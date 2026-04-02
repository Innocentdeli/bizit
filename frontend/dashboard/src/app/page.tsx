"use client";

import React from "react";
import { Providers } from "@/components/protocol-ui/Providers";
import MarketplaceFeed from "@/components/protocol-ui/MarketplaceFeed";

export default function Home() {
  return (
    <Providers>
      <div className="flex h-screen overflow-hidden bg-[#020202] text-white font-mono p-10">
        <div className="max-w-[1920px] mx-auto w-full">
          <MarketplaceFeed />
        </div>
      </div>
    </Providers>
  );
}
