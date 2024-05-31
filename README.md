# Aqtis Solidity Challenge
Let's start with a new Hardhat project, which gives me some guidelines already. 
I guess there are two ways to interpret token distribution, either fully on-contract, or let the backend script decide.. Or maybe some way in-between. Let's write the basic token contracts and vault for now, after that I'll figure out how to implement the airdrop.

## Contracts
The contracts for this project are pretty straightforward. ```Fud``` is just a simple token, ```Win``` a token with some logic to mint, ```AirVault``` contains methods to deposit and withdraw ```Fud```. 
I decided to build the token distribution mechanism into a solid backend, otherwise the contract would need to record the average deposit, calculate earnings, etc. and the backend calls to payout should be very precise, if it misses blocks or is down for a bit, it might give users too many tokens. (Although I understand it's just a test-project, but I want it to be solid).

Important to note, I split up the deployer and minter wallet. The minter wallet (just a single private key - not a phrase) will be stored on a server that will run the service. If the server might get hacked, illigitimate tokens might be minted by the hacker - but at least we don't lose control over the contract.

Also, instead of using ```mint```, I added a ```bulkMint``` method which can mint everything at once.

## The service
For this challenge I'd like to show some Python skills as well, although I could do this in NodeJS by using ```provider.on('block', () => {})``` for blocks, and the contract by using ```contract.on('AirVaultDeposit', () => {})``` etc. just add the latest state to user objects and loop through them when the block number passes a certain point.

The problem though with python-web3 are the event handlers, because there aren't any, or at least I can't listen to them in the same way. So I'll have to make some logic to make it work and make sure events aren't handled twice. Besides that, it would be nice to have a way to read events in the past, since, say, there's an unhandled exception somewhere and the service crashes. Or, we picked an unreliable RPC which misses events every once in a while. We'll want to make sure the socials aren't filled with... well... FUD.

So I'll start with a ```TokenDistributor``` class that handles all the logic, and we can hook the calculator into the blockchain-read/write service. Meanwhile, the calculator can be unit-tested seperately, but also get expanded when more requirements are added in the future.

Imagine we have another locker that locks an NFT, which would double your rewards, we could tell the ```TokenDistributor``` the state of the new locker, and it could handle the new calculation from there, without impacting any other parts of the service.

## Epochs
The ```TokenDistributor``` class will work with 100-block (configurable, of course) epochs, simply using ```floor( block / interval )```, so blocks within a certain range to make calculations easier, but also to trigger a payout when a new epoch arises on the chain. When a deposit is made within an epoch, it'll be recorded, and handled after the epoch ends. Even deposits outside the epoch stay recorded, or can be added to the state later, but will not be handled since they don't fall within the current range.

## Running the service
```python service/service.py```

## Solidity Unit tests
```npx hardhat test```

## Python Unit tests
```cd service && python -m unittest service_test.py```

## Hindsight
In the end, I took a bit more time to make a solid handler in Python, but I think it's looks nice and is very expendable by using an Object-oriented way of setting it up. Which could feel over-engineered by some, which I get. However, when a new user steps into your project and buys tokens, and notices something wrong they might sell and never come back, so I prefer making the kinds of services almost foolproof :)