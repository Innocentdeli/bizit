// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ModuleRegistry
 * @notice DAO-controlled registry of approved execution modules
 * @dev Only approved modules can be used to create listings
 */
contract ModuleRegistry is Ownable {
    // ============ STATE VARIABLES ============
    
    mapping(address => bool) public approvedModules;
    mapping(address => string) public moduleMetadata; // IPFS URI describing the module
    
    address[] public allModules;
    
    // ============ EVENTS ============
    
    event ModuleApproved(address indexed module, string metadataURI);
    event ModuleRevoked(address indexed module);
    
    // ============ ERRORS ============
    
    error ModuleAlreadyApproved();
    error ModuleNotApproved();
    
    // ============ CONSTRUCTOR ============
    
    constructor() Ownable(msg.sender) {}
    
    // ============ ADMIN FUNCTIONS ============
    
    /**
     * @notice Approve a new execution module
     * @param module The module contract address
     * @param metadataURI IPFS URI describing the module's purpose and interface
     */
    function approveModule(address module, string calldata metadataURI) external onlyOwner {
        if (approvedModules[module]) revert ModuleAlreadyApproved();
        
        approvedModules[module] = true;
        moduleMetadata[module] = metadataURI;
        allModules.push(module);
        
        emit ModuleApproved(module, metadataURI);
    }
    
    /**
     * @notice Revoke an execution module
     * @param module The module to revoke
     */
    function revokeModule(address module) external onlyOwner {
        if (!approvedModules[module]) revert ModuleNotApproved();
        
        approvedModules[module] = false;
        
        emit ModuleRevoked(module);
    }
    
    // ============ VIEW FUNCTIONS ============
    
    /**
     * @notice Check if a module is approved
     * @param module The module address
     */
    function isApproved(address module) external view returns (bool) {
        return approvedModules[module];
    }
    
    /**
     * @notice Get all approved modules
     */
    function getAllModules() external view returns (address[] memory) {
        return allModules;
    }
    
    /**
     * @notice Get module metadata URI
     * @param module The module address
     */
    function getModuleMetadata(address module) external view returns (string memory) {
        return moduleMetadata[module];
    }
}
