const hre = require("hardhat");

async function main() {
  const fudToken = await hre.ethers.deployContract("Fud");
  await fudToken.waitForDeployment();

  const winToken = await hre.ethers.deployContract("Win");
  await winToken.waitForDeployment();

  const airVault = await hre.ethers.deployContract("AirVault", [fudToken.target]);
  await airVault.waitForDeployment();

  await winToken.setMinter('0xa1f9A2E3431e57014c8794b4cdc8718A657bB3Ef', true)
  await fudToken.transfer('0x56CE632320B8aF872b9ef5b94C4a483A63f1EE26', hre.ethers.parseEther('100'))
  await fudToken.transfer('0x8d8A668F39Df525045cdeAE09F87C9430D1C20E8', hre.ethers.parseEther('100'))

  console.log({
    fud: fudToken.target,
    win: winToken.target,
    airVault: airVault.target
  })
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
