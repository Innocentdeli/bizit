// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title EscrowCore
 * @notice Universal trust layer for all marketplace transactions
 * @dev Handles fund locking, timeouts, release conditions, and disputes
 */
contract EscrowCore is ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    // ============ ENUMS ============
    
    enum EscrowState {
        PENDING,
        FUNDED,
        RELEASED,
        REFUNDED,
        DISPUTED
    }
    
    // ============ STRUCTS ============
    
    struct Escrow {
        uint256 listingId;
        address buyer;
        address seller;
        address paymentToken;
        uint256 amount;
        uint256 releaseTime;
        EscrowState state;
        uint256 createdAt;
    }
    
    // ============ STATE VARIABLES ============
    
    uint256 private _escrowIdCounter;
    address public marketplaceKernel;
    address public arbitrator;
    
    uint256 public constant DEFAULT_TIMEOUT = 7 days;
    
    mapping(uint256 => Escrow) public escrows;
    mapping(uint256 => uint256) public listingToEscrow; // listingId => escrowId
    
    // ============ EVENTS ============
    
    event EscrowCreated(uint256 indexed escrowId, uint256 indexed listingId, address buyer, uint256 amount);
    event EscrowFunded(uint256 indexed escrowId);
    event EscrowReleased(uint256 indexed escrowId, address indexed seller, uint256 amount);
    event EscrowRefunded(uint256 indexed escrowId, address indexed buyer, uint256 amount);
    event DisputeRaised(uint256 indexed escrowId);
    
    // ============ ERRORS ============
    
    error Unauthorized();
    error InvalidState();
    error InsufficientFunds();
    error TimeoutNotReached();
    
    // ============ MODIFIERS ============
    
    modifier onlyKernel() {
        if (msg.sender != marketplaceKernel) revert Unauthorized();
        _;
    }
    
    modifier onlyArbitrator() {
        if (msg.sender != arbitrator) revert Unauthorized();
        _;
    }
    
    // ============ CONSTRUCTOR ============
    
    constructor(address _marketplaceKernel, address _arbitrator) {
        marketplaceKernel = _marketplaceKernel;
        arbitrator = _arbitrator;
    }
    
    // ============ CORE FUNCTIONS ============
    
    /**
     * @notice Create and fund an escrow
     * @param listingId The listing being purchased
     * @param seller The seller address
     * @param paymentToken The payment token (address(0) for native)
     * @param amount The escrow amount
     */
    function createEscrow(
        uint256 listingId,
        address seller,
        address paymentToken,
        uint256 amount
    ) external payable onlyKernel returns (uint256) {
        uint256 escrowId = ++_escrowIdCounter;
        
        escrows[escrowId] = Escrow({
            listingId: listingId,
            buyer: tx.origin, // Original buyer
            seller: seller,
            paymentToken: paymentToken,
            amount: amount,
            releaseTime: block.timestamp + DEFAULT_TIMEOUT,
            state: EscrowState.PENDING,
            createdAt: block.timestamp
        });
        
        listingToEscrow[listingId] = escrowId;
        
        // Handle funding
        if (paymentToken == address(0)) {
            // Native currency
            if (msg.value < amount) revert InsufficientFunds();
        } else {
            // ERC20
            IERC20(paymentToken).safeTransferFrom(tx.origin, address(this), amount);
        }
        
        escrows[escrowId].state = EscrowState.FUNDED;
        
        emit EscrowCreated(escrowId, listingId, tx.origin, amount);
        emit EscrowFunded(escrowId);
        
        return escrowId;
    }
    
    /**
     * @notice Release funds to seller (called by buyer or after timeout)
     * @param escrowId The escrow to release
     */
    function releaseFunds(uint256 escrowId) external nonReentrant {
        Escrow storage escrow = escrows[escrowId];
        
        if (escrow.state != EscrowState.FUNDED) revert InvalidState();
        
        // Only buyer can release before timeout
        if (msg.sender != escrow.buyer && block.timestamp < escrow.releaseTime) {
            revert Unauthorized();
        }
        
        escrow.state = EscrowState.RELEASED;
        
        // Transfer funds to seller
        if (escrow.paymentToken == address(0)) {
            payable(escrow.seller).transfer(escrow.amount);
        } else {
            IERC20(escrow.paymentToken).safeTransfer(escrow.seller, escrow.amount);
        }
        
        emit EscrowReleased(escrowId, escrow.seller, escrow.amount);
    }
    
    /**
     * @notice Refund to buyer (dispute resolution)
     * @param escrowId The escrow to refund
     */
    function refundBuyer(uint256 escrowId) external onlyArbitrator nonReentrant {
        Escrow storage escrow = escrows[escrowId];
        
        if (escrow.state != EscrowState.FUNDED && escrow.state != EscrowState.DISPUTED) {
            revert InvalidState();
        }
        
        escrow.state = EscrowState.REFUNDED;
        
        // Transfer funds back to buyer
        if (escrow.paymentToken == address(0)) {
            payable(escrow.buyer).transfer(escrow.amount);
        } else {
            IERC20(escrow.paymentToken).safeTransfer(escrow.buyer, escrow.amount);
        }
        
        emit EscrowRefunded(escrowId, escrow.buyer, escrow.amount);
    }
    
    /**
     * @notice Raise a dispute
     * @param escrowId The escrow in dispute
     */
    function raiseDispute(uint256 escrowId) external {
        Escrow storage escrow = escrows[escrowId];
        
        if (msg.sender != escrow.buyer && msg.sender != escrow.seller) {
            revert Unauthorized();
        }
        
        if (escrow.state != EscrowState.FUNDED) revert InvalidState();
        
        escrow.state = EscrowState.DISPUTED;
        
        emit DisputeRaised(escrowId);
    }
    
    // ============ VIEW FUNCTIONS ============
    
    function getEscrow(uint256 escrowId) external view returns (Escrow memory) {
        return escrows[escrowId];
    }
    
    function getEscrowByListing(uint256 listingId) external view returns (Escrow memory) {
        uint256 escrowId = listingToEscrow[listingId];
        return escrows[escrowId];
    }
}
