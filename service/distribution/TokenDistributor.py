import os
from dotenv import load_dotenv

load_dotenv()

# Load the configured interval
AirdropInterval = int(os.getenv('AIRDROP_INTERVAL'))

## Vault transaction class
# Stores individual deposits/withdraws to loop over at a later stage
class VaultTransaction:
    TX_TYPE_DEPOSIT = "Deposit"
    TX_TYPE_WITHDRAW = "Withdraw"
    
    def __init__(self, block, winner, amount, newBalance, type):
        self.block = block
        self.winner = winner
        self.amount = amount
        self.newBalance = newBalance
        self.type = type
    
    # Checks whether the transaction is within the provided epoch
    def isWithinEpoch(self, epoch):
        currentEpoch = self.block // AirdropInterval
        return epoch == currentEpoch

## Store individual winner information per epoch
class Winner:
    def __init__(self, winner, epoch):
        self.winner = winner
        self.epoch = epoch
        self.lastBlock = 0
        self.balance = 0
        self.earned = 0.0
        
    ## Push an update to the current user, which will update the last block and earnings up until this point in time
    def pushUpdate(self, block, type, amount):
        if block < self.lastBlock:
            raise Exception('Block cannot be earlier')
        
        if self.balance > 0 and self.lastBlock > 0:
            blockAmount = (block - self.lastBlock)
            
            # WIN tokens in airdrop = 0.05 * (# FUD tokens deposited) * (# blocks deposited) / ( total # blocks)
            self.earned += (0.05 * self.balance * blockAmount) / AirdropInterval
        
        match type:
            case VaultTransaction.TX_TYPE_DEPOSIT:
                self.balance += amount
                
            case VaultTransaction.TX_TYPE_WITHDRAW:
                self.balance -= amount
                
            case _:
                raise Exception('Transaction type seems to be undefined')
        
        self.lastBlock = block

## Token distributor class
# Methods to record new transactions and process winnings for each epoch
class TokenDistributor:
    def __init__(self):
        self.currentBlock = 0
        
        # Store initial handled epoch as -1, so epoch 0 can still be handled first
        self.handledEpoch = -1
        self.state = {}
    
    # Returns the epoch based on block
    def calculateEpochForBlock(self, block):
        return block // AirdropInterval
    
    # Checks if we are in a new epoch
    def isInNewEpoch(self):
        currentEpoch = self.calculateEpochForBlock(self.currentBlock)
        
        # Do nothing if epoch is the same
        return (currentEpoch > self.handledEpoch + 1)
    
    # Get the first epoch that needs to be handled
    def getFirstUnhandledEpoch(self):
        if not self.isInNewEpoch():
            return None
        
        return self.handledEpoch + 1
    
    # Marks the epoch as handled
    # Throws an exception if you're handling the wrong one
    def markAsHandled(self, epoch):
        if self.getFirstUnhandledEpoch() != epoch:
            raise Exception('Please handle earliest unhandled epoch first')
        
        self.handledEpoch = epoch
        
    # Method to add a new withdraw to the records
    def recordWithdraw(self, txHash, block, winner, amount, newBalance):
         # Already registered
        if txHash in self.state:
            return;
        
        self.state[txHash] = VaultTransaction(
            block, 
            winner, 
            amount, 
            newBalance, 
            VaultTransaction.TX_TYPE_WITHDRAW
        )
       
    # Method to add a new deposit to the records
    def recordDeposit(self, txHash, block, winner, amount, newBalance):
        # Already registered
        if txHash in self.state:
            return;
        
        self.state[txHash] = VaultTransaction(
            block, 
            winner, 
            amount, 
            newBalance, 
            VaultTransaction.TX_TYPE_DEPOSIT
        )
    
    # Loop through every change within an epoch and process earnings
    def processWinnings(self, epoch):
        ## Sort method for VaultTransactions
        def sortByBlock(e):
            return e.block
        
        # Sort transactions by block ID - since transactions might not have been read in order
        transactions = list(self.state.values()) 
        transactions.sort(key=sortByBlock)
        
        winners = {}
        for tx in transactions:
            # Check if the transaction is within current epoch to process - skip otherwise
            if not tx.isWithinEpoch(epoch):
                continue
            
            # Push an object if it does not exist yet
            if tx.winner not in winners:
                winners[tx.winner] = Winner(tx, epoch)
            
            currentWinner = winners[tx.winner]
            currentWinner.pushUpdate(tx.block, tx.type, tx.amount)
        
        ## Loop through winners and finish setting rewards for last block in epoch
        for winner in winners:
            lastBlockInEpoch = (epoch * AirdropInterval) + AirdropInterval
            winners[winner].pushUpdate(lastBlockInEpoch, VaultTransaction.TX_TYPE_DEPOSIT, 0)
        
        return winners