const {
  time,
  loadFixture,
} = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { expect } = require("chai");

describe("AirVault", function () {
  async function deployTokensAndVault() {
    const [owner, minter, winner1, winner2] = await ethers.getSigners();

    const FudToken = await ethers.getContractFactory("Fud");
    const fud = await FudToken.deploy();

    const WinToken = await ethers.getContractFactory("Win");
    const win = await WinToken.deploy();
    win.connect(owner).setMinter(minter.address, true);

    const AirVault = await ethers.getContractFactory("AirVault");
    const airVault = await AirVault.deploy(fud.target);

    // Give the winners some FUD tokens to play with
    fud.connect(owner).transfer(winner1.address, ethers.parseEther('100'))
    fud.connect(owner).transfer(winner2.address, ethers.parseEther('100'))

    // Give the vault approval to send away tokens
    fud.connect(winner1).approve(airVault.getAddress(), ethers.parseEther('100'))
    fud.connect(winner2).approve(airVault.getAddress(), ethers.parseEther('100'))

    return { fud, win, airVault, owner, minter, winner1, winner2 };
  }

  describe("Win Token", function () {
    describe("Mint", function () {
      it("Should allow mints from designated address", async function () {
        const { win, minter, winner1 } = await loadFixture(
          deployTokensAndVault
        );

        // Check if the minter can make new tokens
        await win.connect(minter).bulkMint([winner1.address], [1000n])
        await expect(await win.connect(minter).balanceOf(winner1.address)).to.equal(1000n)

        // Check if noone else can
        await expect(win.connect(winner1).mint(winner1.address, 1000n)).to.be.revertedWith('WIN: Sender is not allowed to mint')
        await expect(win.connect(winner1).bulkMint([winner1.address], [1000n])).to.be.revertedWith('WIN: Sender is not allowed to mint')
      });
    });
  });


  describe("AirVault", function () {
    describe("Deposits", function () {
      it("Should emit event on deposit", async function () {
        const { airVault, winner1 } = await loadFixture(
          deployTokensAndVault
        );

        const amount = 1000
        await expect(airVault.connect(winner1).deposit(amount))
          .to.emit(airVault, "AirVaultDeposit")
          .withArgs(winner1.address, amount, amount);
      });

      it("Should store locked balance", async function () {
        const { airVault, winner1 } = await loadFixture(
          deployTokensAndVault
        );

        const amount = 1000n
        await airVault.connect(winner1).deposit(amount)
        expect(await airVault.lockedBalanceOf(winner1.address)).to.be.equal(amount)
      });

      it("Should tranfer token balance", async function () {
        const { airVault, fud, winner1 } = await loadFixture(
          deployTokensAndVault
        );

        const startingBalance = ethers.parseEther('100')
        const amount = 1000n

        await airVault.connect(winner1).deposit(amount)
        expect(await fud.balanceOf(airVault.target)).to.be.equal(amount)
        expect(await fud.balanceOf(winner1)).to.be.equal(startingBalance - amount)
      });
    });

    describe("Withdraws", function () {
      it("Should emit event on withdraw & update balance", async function () {
        const { airVault, winner1 } = await loadFixture(
          deployTokensAndVault
        );

        const amount = 1000n

        // Deposit first
        await airVault.connect(winner1).deposit(amount)

        const withdrawAmount = 500n

        await expect(airVault.connect(winner1).withdraw(withdrawAmount))
          .to.emit(airVault, "AirVaultWithdraw")
          .withArgs(winner1.address, withdrawAmount, amount - withdrawAmount);

          expect(await airVault.lockedBalanceOf(winner1)).to.be.equal(amount - withdrawAmount)
      });

      it("Should should not allow high withdraws", async function () {
        const { airVault, winner1 } = await loadFixture(
          deployTokensAndVault
        );

        const amount = 1000n
        await  expect(
            airVault.connect(winner1).withdraw(amount)
          ).to.be.revertedWith('AirVault: Not enough tokens locked')
      });
    });
  });
});
