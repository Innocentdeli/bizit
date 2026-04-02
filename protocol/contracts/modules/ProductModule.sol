// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/IExecutionModule.sol";

/**
 * @title ProductModule
 * @notice Execution module for physical and digital products
 * @dev Handles one-time payments with delivery confirmation
 */
contract ProductModule is IExecutionModule {
    // ============ STATE VARIABLES ============
    
    address public immutable marketplaceKernel;
    address public immutable escrowCore;
    
    mapping(uint256 => PurchaseData) public purchases;
    
    struct PurchaseData {
        address buyer;
        address seller;
        uint256 amount;
        bool delivered;
        uint256 purchasedAt;
    }
    
    // ============ EVENTS ============
    
    event ProductPurchased(uint256 indexed listingId, address indexed buyer, uint256 amount);
    event ProductDelivered(uint256 indexed listingId);
    
    // ============ ERRORS ============
    
    error Unauthorized();
    error AlreadyDelivered();
    
    // ============ MODIFIERS ============
    
    modifier onlyKernel() {
        if (msg.sender != marketplaceKernel) revert Unauthorized();
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor(address _marketplaceKernel, address _escrowCore) {
        marketplaceKernel = _marketplaceKernel;
        escrowCore = _escrowCore;
    }
    
    // ============ IMPLEMENTATION ============
    
    function validate(
        uint256,
        address,
        string calldata
    ) external pure override returns (bool) {
        // Products have minimal validation - just need valid metadata
        return true;
    }
    
    function onPurchase(
        uint256 listingId,
        address buyer,
        address seller,
        uint256 amount
    ) external override onlyKernel {
        purchases[listingId] = PurchaseData({
            buyer: buyer,
            seller: seller,
            amount: amount,
            delivered: false,
            purchasedAt: block.timestamp
        });
        
        emit ProductPurchased(listingId, buyer, amount);
    }
    
    function onDelivery(uint256 listingId) external override {
        PurchaseData storage purchase = purchases[listingId];
        
        // Only seller can mark as delivered
        if (msg.sender != purchase.seller) revert Unauthorized();
        if (purchase.delivered) revert AlreadyDelivered();
        
        purchase.delivered = true;
        
        emit ProductDelivered(listingId);
        
        // Buyer has 48 hours to dispute, otherwise auto-release
        // This would trigger escrow release logic
    }
}
