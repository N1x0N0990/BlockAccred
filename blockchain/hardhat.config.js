require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
const networks = {
  localhost: { url: "http://127.0.0.1:8545", chainId: 31337 },
};

if (process.env.BLOCKCHAIN_RPC_URL && process.env.BLOCKCHAIN_PRIVATE_KEY) {
  networks.sepolia = {
    url: process.env.BLOCKCHAIN_RPC_URL,
    chainId: 11155111,
    accounts: [process.env.BLOCKCHAIN_PRIVATE_KEY],
  };
}

module.exports = {
  solidity: "0.8.20",
  networks,
};
