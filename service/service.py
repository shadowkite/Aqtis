from web3 import Web3
import json

import time
import os
from distribution.TokenDistributor import TokenDistributor

## Process blockchain logs
def processLogs(distributor, airVault, pastBlock):
    deposits = airVault.events.AirVaultDeposit().get_logs(fromBlock=pastBlock)
    for deposit in deposits:
        distributor.recordDeposit(
            deposit.transactionHash.hex(),
            deposit.blockNumber,
            deposit.args.winner,
            deposit.args.amountDeposited,
            deposit.args.newBalance
        )
        
    withdraws = airVault.events.AirVaultWithdraw().get_logs(fromBlock=pastBlock)
    for withdraw in withdraws:
        distributor.recordWithdraw(
            withdraw.transactionHash.hex(),
            withdraw.blockNumber,
            withdraw.args.winner,
            withdraw.args.amountDeposited,
            withdraw.args.newBalance
        )

## Gather rewards and send them out
def sendRewards(w3, distributor, winToken):
    # Do a safety check first
    if not distributor.isInNewEpoch():
        raise Exception('Epoch is already handled')
    
    # Get winnings for epoch
    newEpoch = distributor.getFirstUnhandledEpoch()
    winnings = distributor.processWinnings(newEpoch)
    
    # Build winner list
    addresses = []
    earnings = []
    for winner in winnings:
        info = winnings[winner]
        earned = int(info.earned)
        print(f'Send {earned} WIN to {winner}')
        
        if earned > 0:
            addresses.append(winner)
            earnings.append(earned)
        
    # If there are tokens to distribute...
    if len(addresses) > 0:
        # Mint winTokens
        account = w3.eth.account.from_key(os.getenv('MINTER_WALLET'))
        tx = winToken.functions.bulkMint(addresses, earnings).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        signedTx = w3.eth.account.sign_transaction(tx, account.key)
        
        # Send TX and wait
        sentTx = w3.eth.send_raw_transaction(signedTx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(sentTx)
        
        print(receipt)
        print('New WIN distributed')
        
    else:    
        print('Nothing to distribute')
        
    # Set epoch as handled
    distributor.markAsHandled(newEpoch)

## Main method
def main():
    rpcServer = os.getenv('RPC')
    print(f'Connecting to {rpcServer}')
    w3 = Web3(Web3.HTTPProvider(rpcServer))
    
    # Load ABIs
    with open('./artifacts/contracts/AirVault.sol/Airvault.json') as airVaultArtifact:
        airVaultABI = json.load(airVaultArtifact)
        
    with open('./artifacts/contracts/Win.sol/Win.json') as winTokenArtifact:
        winTokenABI = json.load(winTokenArtifact)
    
    # Initiate contracts for interactions
    airVault = w3.eth.contract(address=os.getenv('AIRVAULT_ADDRESS'), abi=airVaultABI['abi'])
    winToken = w3.eth.contract(address=os.getenv('WIN_ADDRESS'), abi=winTokenABI['abi'])
    
    # Create the distribution calculator
    distributor = TokenDistributor()
    
    ## Initiate current block
    # TODO Make a nice way to handle blocks if the service crashed at some point
    newBlock = w3.eth.get_block_number()
    distributor.currentBlock = newBlock
    distributor.handledEpoch = distributor.calculateEpochForBlock(newBlock) - 1
    
    try:
        # Loop infinitely
        while True:
            newBlock = w3.eth.get_block_number()
            print(f'Checking... current block: {newBlock}')
            
            # Pick up new logs if new blocks were mined
            if newBlock > distributor.currentBlock:
                distributor.currentBlock = newBlock
                
                # Process event logs; look 10 blocks in the past
                processLogs(distributor, airVault, newBlock - 10)
            
            # Attempt to send rewards if we're in a new epoch
            if distributor.isInNewEpoch():
                sendRewards(w3, distributor, winToken)
            
            ## Look for new blocks every 10 seconds
            time.sleep(10)
            
    except Exception as e:
        print(f'Something went terribly wrong, process stopped! - @TODO Handle this in a nice way; send devs a notification or something :)')
        print(e)
    
if __name__ == '__main__':
    main();