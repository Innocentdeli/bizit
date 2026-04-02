// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IExecutionModule
 * @notice Interface that all execution modules must implement
 * @dev This allows the protocol to be infinitely extensible
 */
interface IExecutionModule {
    /**
     * @notice Validate a listing before creation
     * @param listingId The listing ID
     * @param seller The seller address
     * @param metadataURI The IPFS metadata URI
     */
    function validate(
        uint256 listingId,
        address seller,
        string calldata metadataURI
    ) external view returns (bool);
    
    /**
     * @notice Called when a purchase is initiated
     * @param listingId The listing being purchased
     * @param buyer The buyer address
     * @param seller The seller address
     * @param amount The purchase amount
     */
    function onPurchase(
        uint256 listingId,
        address buyer,
        address seller,
        uint256 amount
    ) external;
    
    /**
     * @notice Called when delivery is confirmed
     * @param listingId The listing ID
     */
    function onDelivery(uint256 listingId) external;
}
