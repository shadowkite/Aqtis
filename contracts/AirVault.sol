// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/interfaces/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Import token
import "./Fud.sol";

/**
 * AirVault
 * Stake FUD to get WIN. Easy right? 
 */
contract AirVault is Ownable {

    /** Events */
    event AirVaultDeposit(
        address winner, 
        uint256 amountDeposited, 
        uint256 newBalance
    );

    event AirVaultWithdraw(
        address winner, 
        uint256 amountWithdrawn, 
        uint256 newBalance
    );

    /** Balance storage */
    mapping(address => uint256) lockedBalance;

    /** Token address */
    Fud fudToken;

    /** Constructor; Requires token address */
    constructor(address fud) Ownable(msg.sender) {
        fudToken = Fud(fud);
    }
    
    /**
     * Deposit method
     * @param amount Amount to deposit
     * @return bool
     */
    function deposit(uint256 amount) public returns(bool) {
        // Try transfer - should revert
        fudToken.transferFrom(msg.sender, address(this), amount);

        // Register new balance amount
        lockedBalance[msg.sender] += amount;

        // Emit event
        emit AirVaultDeposit(msg.sender, amount, lockedBalance[msg.sender]);

        return true;
    }

    /**
     * Withdraws locked balance
     * @param amount Amount to withdraw
     * @return bool
     */
	function withdraw(uint256 amount) public returns(bool) {
        // Check locked balance first
        require(lockedBalance[msg.sender] >= amount, 'AirVault: Not enough tokens locked');

        // Deduct balance first
        lockedBalance[msg.sender] -= amount;

        // Send tokens
        fudToken.transfer(msg.sender, amount);

        // Emit event
        emit AirVaultWithdraw(msg.sender, amount, lockedBalance[msg.sender]);

        return true;
    }
	
    /**
     * Returns the current locked balance
     * @param account Winner :)
     * @return uint256 Balance
     */
	function lockedBalanceOf(address account) external view returns(uint256) {
        return lockedBalance[account];
    }
}