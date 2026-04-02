export const MARKETPLACE_KERNEL_ABI = [
    {
        "inputs": [],
        "name": "totalListings",
        "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{ "internalType": "uint256", "name": "listingId", "type": "uint256" }],
        "name": "getListing",
        "outputs": [
            {
                "components": [
                    { "internalType": "uint256", "name": "id", "type": "uint256" },
                    { "internalType": "address", "name": "seller", "type": "address" },
                    { "internalType": "uint8", "name": "category", "type": "uint8" },
                    { "internalType": "address", "name": "executionModule", "type": "address" },
                    { "internalType": "address", "name": "escrowModule", "type": "address" },
                    { "internalType": "address", "name": "paymentToken", "type": "address" },
                    { "internalType": "uint256", "name": "basePrice", "type": "uint256" },
                    { "internalType": "string", "name": "metadataURI", "type": "string" },
                    { "internalType": "bool", "name": "active", "type": "bool" },
                    { "internalType": "uint256", "name": "createdAt", "type": "uint256" }
                ],
                "internalType": "struct MarketplaceKernel.Listing",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
] as const;
