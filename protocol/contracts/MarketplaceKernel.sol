// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MarketplaceKernel
 * @notice The immutable core of the Universal Decentralized Marketplace
 * @dev This contract does NOT know what it's selling - it only manages listings and routes to execution modules
 */
contract MarketplaceKernel {
    // ============ STATE VARIABLES ============
    
    uint256 private _listingIdCounter;
    address public immutable moduleRegistry;
    address public immutable escrowCore;
    address public treasury;
    
    uint256 public protocolFeeBps = 250; // 2.5% default fee
    
    // ============ STRUCTS ============
    
    struct Listing {
        uint256 id;
        address seller;
        uint8 category;              // Dynamic category ID
        address executionModule;     // Which module handles this listing type
        address escrowModule;        // Which escrow variant to use
        address paymentToken;        // ERC20 token or address(0) for native
        uint256 basePrice;
        string metadataURI;          // IPFS schema-driven JSON
        bool active;
        uint256 createdAt;
    }
    
    // ============ MAPPINGS ============
    
    mapping(uint256 => Listing) public listings;
    mapping(address => uint256[]) public sellerListings;
    
    // ============ EVENTS ============
    
    event ListingCreated(
        uint256 indexed listingId,
        address indexed seller,
        uint8 category,
        address executionModule,
        string metadataURI
    );
    
    event ListingUpdated(uint256 indexed listingId, string newMetadataURI);
    event ListingDeactivated(uint256 indexed listingId);
    event PurchaseInitiated(uint256 indexed listingId, address indexed buyer, uint256 amount);
    
    // ============ ERRORS ============
    
    error InvalidModule();
    error ListingNotActive();
    error UnauthorizedSeller();
    error InvalidPrice();
    
    // ============ CONSTRUCTOR ============
    
    constructor(address _moduleRegistry, address _escrowCore, address _treasury) {
        moduleRegistry = _moduleRegistry;
        escrowCore = _escrowCore;
        treasury = _treasury;
    }
    
    // ============ CORE FUNCTIONS ============
    
    /**
     * @notice Create a new listing
     * @param category The marketplace category (0=Product, 1=Service, 2=Asset, etc.)
     * @param executionModule The approved module that will handle this listing's logic
     * @param paymentToken The token for payment (address(0) for native currency)
     * @param basePrice The base price in the smallest unit
     * @param metadataURI IPFS URI containing the schema-driven listing data
     */
    function createListing(
        uint8 category,
        address executionModule,
        address paymentToken,
        uint256 basePrice,
        string calldata metadataURI
    ) external returns (uint256) {
        // Validate module is approved
        if (!IModuleRegistry(moduleRegistry).isApproved(executionModule)) {
            revert InvalidModule();
        }
        
        if (basePrice == 0) revert InvalidPrice();
        
        uint256 listingId = ++_listingIdCounter;
        
        listings[listingId] = Listing({
            id: listingId,
            seller: msg.sender,
            category: category,
            executionModule: executionModule,
            escrowModule: escrowCore, // Default to core escrow
            paymentToken: paymentToken,
            basePrice: basePrice,
            metadataURI: metadataURI,
            active: true,
            createdAt: block.timestamp
        });
        
        sellerListings[msg.sender].push(listingId);
        
        emit ListingCreated(listingId, msg.sender, category, executionModule, metadataURI);
        
        return listingId;
    }
    
    /**
     * @notice Update listing metadata
     * @param listingId The listing to update
     * @param newMetadataURI New IPFS URI
     */
    function updateListing(uint256 listingId, string calldata newMetadataURI) external {
        Listing storage listing = listings[listingId];
        
        if (listing.seller != msg.sender) revert UnauthorizedSeller();
        if (!listing.active) revert ListingNotActive();
        
        listing.metadataURI = newMetadataURI;
        
        emit ListingUpdated(listingId, newMetadataURI);
    }
    
    /**
     * @notice Deactivate a listing
     * @param listingId The listing to deactivate
     */
    function deactivateListing(uint256 listingId) external {
        Listing storage listing = listings[listingId];
        
        if (listing.seller != msg.sender) revert UnauthorizedSeller();
        
        listing.active = false;
        
        emit ListingDeactivated(listingId);
    }
    
    /**
     * @notice Purchase a listing (routes to execution module)
     * @param listingId The listing to purchase
     */
    function purchase(uint256 listingId) external payable {
        Listing memory listing = listings[listingId];
        
        if (!listing.active) revert ListingNotActive();
        
        // Calculate protocol fee
        uint256 fee = (listing.basePrice * protocolFeeBps) / 10000;
        uint256 sellerAmount = listing.basePrice - fee;
        
        // Route to execution module for custom logic
        IExecutionModule(listing.executionModule).onPurchase(
            listingId,
            msg.sender,
            listing.seller,
            sellerAmount
        );
        
        emit PurchaseInitiated(listingId, msg.sender, listing.basePrice);
    }
    
    /**
     * @notice Get all listings by a seller
     * @param seller The seller address
     */
    function getSellerListings(address seller) external view returns (uint256[] memory) {
        return sellerListings[seller];
    }
    
    /**
     * @notice Get listing details
     * @param listingId The listing ID
     */
    function getListing(uint256 listingId) external view returns (Listing memory) {
        return listings[listingId];
    }
    
    /**
     * @notice Get total number of listings created
     */
    function totalListings() external view returns (uint256) {
        return _listingIdCounter;
    }
}

// ============ INTERFACES ============

interface IModuleRegistry {
    function isApproved(address module) external view returns (bool);
}

interface IExecutionModule {
    function onPurchase(
        uint256 listingId,
        address buyer,
        address seller,
        uint256 amount
    ) external;
}
