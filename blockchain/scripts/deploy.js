// Deploys the contract to the running local Hardhat node and writes
// blockchain/deployment.json (address + ABI) which the FastAPI backend reads.
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const Factory = await hre.ethers.getContractFactory("AccreditationEvidence");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();
  const address = await contract.getAddress();

  const artifact = await hre.artifacts.readArtifact("AccreditationEvidence");
  const out = { address, network: hre.network.name, abi: artifact.abi };
  fs.writeFileSync(path.join(__dirname, "..", "deployment.json"), JSON.stringify(out, null, 2));

  console.log("AccreditationEvidence deployed to:", address);
  console.log("Wrote blockchain/deployment.json");
}

main().catch((e) => { console.error(e); process.exit(1); });
