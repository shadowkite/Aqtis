// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * Win Token
 * When you own these tokens, you're a winner
 */
contract Win is ERC20, Ownable {

    /**
     * Store a list with addresses who can mint (or not)
     */
    mapping(address => bool) minters;

    // onlyMinter modifier - Checks whether an address is allowed to mint
    modifier onlyMinter() {
        require(minters[msg.sender], 'WIN: Sender is not allowed to mint');
        _;
    }

    // Constructor
    constructor() ERC20('Win', 'WIN') Ownable(msg.sender) {
       
    }

    /**
     * Mint new tokens - only by allowed addresses
     * @param account Address to mint tokens to
     * @param amount The amount to mint
     */
    function mint(address account, uint256 amount) public onlyMinter returns (bool) {
        _mint(account, amount);
        return true;
    }

    /**
     * Bulk mint new tokens - only by allowed addresses
     * @param accounts List of accounts to mint to
     * @param amounts List of amounts to give away
     */
    function bulkMint(address[] calldata accounts, uint256[] calldata amounts) public onlyMinter returns(bool) {
        require(accounts.length == amounts.length, 'WIN: Length mismatch');
        for(uint256 i = 0; i < accounts.length; i++) {
            _mint(accounts[i], amounts[i]);
        }
        return true;
    } 

    /** Admin functions */
    
    /**
     * Changes whether an address can mint or not
     * @param minter Address to give/remove mint rights
     * @param allowed True/false
     */
    function setMinter(address minter, bool allowed) public onlyOwner {
        minters[minter] = allowed;
    }
}