import unittest
from distribution.TokenDistributor import TokenDistributor

class TokenDistributorTestCase(unittest.TestCase):
    def setUp(self):
        self.tokenDistributor = TokenDistributor();
    
    ## Let's make sure there's a new epoch to handle every 100 blocks
    def test_epoch_calculation(self):
        # Distributor starts in Epoch -1
        self.tokenDistributor.currentBlock = 0
        
        # No epoch to handle yet
        self.assertFalse(self.tokenDistributor.isInNewEpoch())
        
        self.tokenDistributor.currentBlock = 50
        self.assertFalse(self.tokenDistributor.isInNewEpoch())
        
        # Go into next Epoch
        self.tokenDistributor.currentBlock = 100
        self.assertTrue(self.tokenDistributor.isInNewEpoch())
        
        # Let's handle epoch 0
        self.assertEqual(0, self.tokenDistributor.getFirstUnhandledEpoch())
        self.tokenDistributor.markAsHandled(0);
        self.assertFalse(self.tokenDistributor.isInNewEpoch())
        
        # No epoch to handle
        self.assertEqual(None, self.tokenDistributor.getFirstUnhandledEpoch())
        
        # Some block far into the future - we still need to handle epoch 1!
        self.tokenDistributor.currentBlock = 1000
        self.assertEqual(1, self.tokenDistributor.getFirstUnhandledEpoch())
        
        # Expect an exception if we handle the wrong epochs
        with self.assertRaises(Exception):
            self.tokenDistributor.markAsHandled(0)
            
        with self.assertRaises(Exception):
            self.tokenDistributor.markAsHandled(10)
        
    ## Test a simple deposit
    def test_single_deposit_within_epoch(self):
        # Record deposit in Epoch 1
        self.tokenDistributor.recordDeposit('0x01', 100, '0xWINNER01', 100, 100);
        
        # Get winners for Epoch 1
        winnings = self.tokenDistributor.processWinnings(1)
        
        # Expect only 1 record
        self.assertEqual(1, len(winnings.values()))
        
        # Should have earned 0.05 * 100 for 100 blocks
        self.assertEqual(5, winnings['0xWINNER01'].earned)
        
    def test_multiple_deposits_within_epoch(self):
        
        # Record winner01 for 100 blocks
        self.tokenDistributor.recordDeposit('0x01', 100, '0xWINNER01', 250, 250);
        
        # Record winner01 for 50 blocks
        self.tokenDistributor.recordDeposit('0x02', 150, '0xWINNER02', 250, 250);
        
        # Calculate earnings
        winnings = self.tokenDistributor.processWinnings(1)
        self.assertEqual(12.5, winnings['0xWINNER01'].earned) # 250 * 1.00 * 0.05 
        self.assertEqual(6.25, winnings['0xWINNER02'].earned) # 250 * 0.50 * 0.05
        
    def test_predefined_testcase_epoch_1(self):
        ## ((10 FUD)*(40 blocks) + (20 FUD)*(60 blocks))*0.05/(100 blocks) = 0.8 WIN
        self.tokenDistributor.recordDeposit('0x01', 100, '0xWINNER01', 10, 10);
        self.tokenDistributor.recordDeposit('0x02', 140, '0xWINNER01', 10, 20);
        
        # Calculate earnings
        winnings = self.tokenDistributor.processWinnings(1)
        self.assertEqual(0.8, winnings['0xWINNER01'].earned)