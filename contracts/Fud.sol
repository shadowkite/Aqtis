// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * Fud Token
 */
contract Fud is ERC20 {
    constructor() ERC20('Fud', 'FUD') {
        // Give the deployer everything
        _mint(msg.sender, 1_500_000 ether);
    }
}