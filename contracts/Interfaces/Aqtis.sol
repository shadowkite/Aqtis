// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

/**
 * Provided interfaces by Aqtis challenge for quick access
 */

interface IFudToken {
	// ... standard ERC20 interface
}

interface IWinToken {
	// ... standard ERC20 interface
	
	// the WIN token is also mintable, so we include the following with the onlyMinter modifier
	function mint(address account, uint256 amount) external returns(bool);
}

interface IAirVault {
	// lock tokens in the AirVault contract
	function deposit(uint256 amount) external returns(bool);

	// withdraw deposited tokens
	function withdraw(uint256 amount) external returns(bool);
	
	// provides how many tokens a specific address has deposited
	function lockedBalanceOf(address account) external view returns(uint256);
}