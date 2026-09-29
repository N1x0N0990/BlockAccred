const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AccreditationEvidence", function () {
  let contract, other;
  const HASH1 = "91d8f8c3c7aa".padEnd(64, "0");
  const HASH2 = "ffee00112233".padEnd(64, "0");

  beforeEach(async () => {
    [, other] = await ethers.getSigners();
    const F = await ethers.getContractFactory("AccreditationEvidence");
    contract = await F.deploy();
    await contract.waitForDeployment();
  });

  it("registers and reads back an evidence hash", async () => {
    await contract.registerEvidence("EV001", 1, HASH1, "XIE-DEMO-001");
    const e = await contract.getEvidence("EV001", 1);
    expect(e.documentHash).to.equal(HASH1);
    expect(e.status).to.equal("Recorded");
    expect(await contract.totalRecords()).to.equal(1n);
  });

  it("never overwrites an existing version", async () => {
    await contract.registerEvidence("EV001", 1, HASH1, "XIE-DEMO-001");
    await expect(contract.registerEvidence("EV001", 1, HASH2, "XIE-DEMO-001")).to.be.revertedWith("Version already recorded");
  });

  it("keeps separate versions", async () => {
    await contract.registerEvidence("EV001", 1, HASH1, "XIE-DEMO-001");
    await contract.registerEvidence("EV001", 2, HASH2, "XIE-DEMO-001");
    expect((await contract.getEvidence("EV001", 2)).documentHash).to.equal(HASH2);
    expect((await contract.getEvidence("EV001", 1)).documentHash).to.equal(HASH1);
  });

  it("updates status without changing the hash", async () => {
    await contract.registerEvidence("EV001", 1, HASH1, "XIE-DEMO-001");
    await contract.verifyEvidence("EV001", 1, "Verified");
    const e = await contract.getEvidence("EV001", 1);
    expect(e.status).to.equal("Verified");
    expect(e.documentHash).to.equal(HASH1);
  });

  it("rejects unknown evidence and non-owners", async () => {
    await expect(contract.getEvidence("NOPE", 1)).to.be.revertedWith("Evidence not found");
    await expect(contract.connect(other).registerEvidence("EV009", 1, HASH1, "X")).to.be.revertedWith("Only owner");
  });
});
