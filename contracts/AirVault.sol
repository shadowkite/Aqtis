// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/interfaces/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Import token
import "./Fud.sol";
import "./Win.sol";

/**
 * AirVault
 * Stake FUD to get WIN. Easy right? 
 */
contract AirVault is Ownable {

    /** Events */
    event AirVaultDeposit(address winner, uint256 amountDeposited, uint256 newBalance);
    event AirVaultWithdraw(address winner, uint256 amountWithdrawn, uint256 newBalance);

    /** Balance storage */
    mapping(address => uint256) lockedBalance;

    /** Token addresses */
    Win winToken;
    Fud fudToken;

    /** Constructor; Requires token addresses */
    constructor(address fud, address win) Ownable(msg.sender) {
        fudToken = Fud(fud);
        winToken = Win(win);
    }
    
    /**
     * Deposit method
     * @param amount Amount to deposit
     * @return bool
     */
    function deposit(uint256 amount) public returns(bool) {
        // Try transfer - should revert
        bool transferred = fudToken.transferFrom(msg.sender, address(this), amount);
        require(transferred, 'AirVault: Unable to deposit');

        // Register new balance amount
        lockedBalance[msg.sender] += amount;

        // Emit event
        emit AirVaultDeposit(msg.sender, amount, lockedBalance[msg.sender]);

        return true;
    }

    /**
     * Withdraws locked balance
     * @param amount Amount to withdraw
     */
	function withdraw(uint256 amount) public returns(bool) {
        // Check locked balance first
        require(lockedBalance[msg.sender] <= amount, 'AirVault: Not enough tokens locked');

        // Deduct balance
        lockedBalance[msg.sender] -= amount;

        // Attempt transfer - should revert
        bool transferred = fudToken.transferFrom(msg.sender, address(this), amount);
        require(transferred, 'AirVault: Unable to withdraw');

        // Emit event
        emit AirVaultWithdraw(msg.sender, amount, lockedBalance[msg.sender]);

        return true;
    }
	
    /**
     * Returns the current locked balance
     * @param account Winner :)
     */
	function lockedBalanceOf(address account) external view returns(uint256) {
        return lockedBalance[account];
    }
}