const hre = require("hardhat");
const dotenv = require("dotenv")

dotenv.config()

async function main() {
  const fudToken = await hre.ethers.deployContract("Fud");
  await fudToken.waitForDeployment();

  const winToken = await hre.ethers.deployContract("Win");
  await winToken.waitForDeployment();

  const airVault = await hre.ethers.deployContract("AirVault", [fudToken.target]);
  await airVault.waitForDeployment();

  await winToken.setMinter(process.env.MINTER_ADDRESS, true)

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
