// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/IExecutionModule.sol";

/**
 * @title ServiceModule
 * @notice Execution module for freelance services and gigs
 * @dev Supports milestone-based payments and partial escrow releases
 */
contract ServiceModule is IExecutionModule {
    // ============ STATE VARIABLES ============
    
    address public immutable marketplaceKernel;
    address public immutable escrowCore;
    
    mapping(uint256 => ServiceData) public services;
    
    struct Milestone {
        string description;
        uint256 amount;
        bool completed;
        bool approved;
    }
    
    struct ServiceData {
        address buyer;
        address seller;
        uint256 totalAmount;
        Milestone[] milestones;
        uint256 completedMilestones;
        uint256 startedAt;
    }
    
    // ============ EVENTS ============
    
    event ServiceStarted(uint256 indexed listingId, address indexed buyer, uint256 totalAmount);
    event MilestoneCompleted(uint256 indexed listingId, uint256 milestoneIndex);
    event MilestoneApproved(uint256 indexed listingId, uint256 milestoneIndex, uint256 amount);
    
    // ============ ERRORS ============
    
    error Unauthorized();
    error InvalidMilestone();
    error MilestoneNotCompleted();
    
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
        // Services should have milestone data in metadata
        return true;
    }
    
    function onPurchase(
        uint256 listingId,
        address buyer,
        address seller,
        uint256 amount
    ) external override onlyKernel {
        // Initialize service with empty milestones
        // Milestones would be added separately based on metadata
        ServiceData storage service = services[listingId];
        service.buyer = buyer;
        service.seller = seller;
        service.totalAmount = amount;
        service.startedAt = block.timestamp;
        
        emit ServiceStarted(listingId, buyer, amount);
    }
    
    function onDelivery(uint256 listingId) external override {
        // For services, delivery is handled per milestone
        // This would be called when all milestones are complete
        ServiceData storage service = services[listingId];
        
        if (msg.sender != service.seller) revert Unauthorized();
        
        // Mark final delivery
    }
    
    // ============ SERVICE-SPECIFIC FUNCTIONS ============
    
    /**
     * @notice Mark a milestone as completed (seller)
     * @param listingId The service listing
     * @param milestoneIndex The milestone to mark complete
     */
    function completeMilestone(uint256 listingId, uint256 milestoneIndex) external {
        ServiceData storage service = services[listingId];
        
        if (msg.sender != service.seller) revert Unauthorized();
        if (milestoneIndex >= service.milestones.length) revert InvalidMilestone();
        
        Milestone storage milestone = service.milestones[milestoneIndex];
        milestone.completed = true;
        
        emit MilestoneCompleted(listingId, milestoneIndex);
    }
    
    /**
     * @notice Approve a milestone and release funds (buyer)
     * @param listingId The service listing
     * @param milestoneIndex The milestone to approve
     */
    function approveMilestone(uint256 listingId, uint256 milestoneIndex) external {
        ServiceData storage service = services[listingId];
        
        if (msg.sender != service.buyer) revert Unauthorized();
        if (milestoneIndex >= service.milestones.length) revert InvalidMilestone();
        
        Milestone storage milestone = service.milestones[milestoneIndex];
        if (!milestone.completed) revert MilestoneNotCompleted();
        
        milestone.approved = true;
        service.completedMilestones++;
        
        // Trigger partial escrow release for this milestone amount
        
        emit MilestoneApproved(listingId, milestoneIndex, milestone.amount);
    }
}
