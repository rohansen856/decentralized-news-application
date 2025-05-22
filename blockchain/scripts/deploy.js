const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Starting deployment of FuseToken NFT donation system...");
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // Configuration
  const config = {
    fuse_token: {
      name: "FuseToken",
      symbol: "FTK",
      baseURI: process.env.NFT_BASE_URI || "https://api.yourapp.com/nft-metadata/"
    },
    donation_manager: {
      platformFeePercent: 250, // 2.5%
      feeCollector: process.env.FEE_COLLECTOR_ADDRESS || deployer.address
    }
  };

  try {
    // Deploy FuseToken contract
    console.log("\n1. Deploying FuseToken contract...");
    const FuseToken = await ethers.getContractFactory("FuseToken");
    const fuseToken = await FuseToken.deploy(
      config.fuse_token.name,
      config.fuse_token.symbol,
      config.fuse_token.baseURI
    );
    await fuseToken.waitForDeployment();
    console.log("FuseToken deployed to:", await fuseToken.getAddress());

    // Deploy DonationManager contract
    console.log("\n2. Deploying DonationManager contract...");
    const DonationManager = await ethers.getContractFactory("DonationManager");
    const donationManager = await DonationManager.deploy(
      await fuseToken.getAddress(),
      config.donation_manager.feeCollector
    );
    await donationManager.waitForDeployment();
    console.log("DonationManager deployed to:", await donationManager.getAddress());

    // Transfer ownership of FuseToken to DonationManager
    console.log("\n3. Transferring FuseToken ownership to DonationManager...");
    const transferTx = await fuseToken.transferOwnership(await donationManager.getAddress());
    await transferTx.wait();
    console.log("Ownership transferred successfully");

    // Verify contracts on blockchain explorer (if not local network)
    const network = await ethers.provider.getNetwork();
    if (network.chainId !== 31337) { // Not hardhat local network
      console.log("\n4. Waiting for block confirmations before verification...");
      await fuseToken.deployTransaction.wait(6);
      await donationManager.deployTransaction.wait(6);
      
      try {
        console.log("Verifying contracts on Etherscan...");
        await hre.run("verify:verify", {
          address: fuseToken.address,
          constructorArguments: [
            config.fuse_token.name,
            config.fuse_token.symbol,
            config.fuse_token.baseURI
          ],
        });
        
        await hre.run("verify:verify", {
          address: donationManager.address,
          constructorArguments: [
            fuseToken.address,
            config.donation_manager.feeCollector
          ],
        });
        console.log("Contracts verified successfully");
      } catch (error) {
        console.log("Verification failed:", error.message);
      }
    }

    // Save deployment information
    const deploymentInfo = {
      network: network.name,
      chainId: network.chainId,
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      contracts: {
        FuseToken: {
          address: fuseToken.address,
          transactionHash: fuseToken.deployTransaction.hash,
          blockNumber: fuseToken.deployTransaction.blockNumber,
          gasUsed: fuseToken.deployTransaction.gasLimit.toString(),
          constructorArgs: [
            config.fuse_token.name,
            config.fuse_token.symbol,
            config.fuse_token.baseURI
          ]
        },
        DonationManager: {
          address: donationManager.address,
          transactionHash: donationManager.deployTransaction.hash,
          blockNumber: donationManager.deployTransaction.blockNumber,
          gasUsed: donationManager.deployTransaction.gasLimit.toString(),
          constructorArgs: [
            fuseToken.address,
            config.donation_manager.feeCollector
          ]
        }
      },
      config: config
    };

    // Save to deployments directory
    const deploymentsDir = path.join(__dirname, "../deployments");
    if (!fs.existsSync(deploymentsDir)) {
      fs.mkdirSync(deploymentsDir, { recursive: true });
    }

    const deploymentFile = path.join(deploymentsDir, `${network.name}-${Date.now()}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
    console.log(`\nDeployment info saved to: ${deploymentFile}`);

    // Save latest deployment for easy access
    const latestFile = path.join(deploymentsDir, `${network.name}-latest.json`);
    fs.writeFileSync(latestFile, JSON.stringify(deploymentInfo, null, 2));
    console.log(`Latest deployment info saved to: ${latestFile}`);

    // Generate environment variables
    const envVars = `
# FuseToken NFT Donation System Contract Addresses
FUSE_TOKEN_CONTRACT=${fuseToken.address}
DONATION_MANAGER_CONTRACT=${donationManager.address}
FEE_COLLECTOR_ADDRESS=${config.donation_manager.feeCollector}
PLATFORM_FEE_PERCENT=${config.donation_manager.platformFeePercent}
NFT_BASE_URI=${config.fuse_token.baseURI}
BLOCKCHAIN_NETWORK=${network.name}
CHAIN_ID=${network.chainId}
`;

    const envFile = path.join(__dirname, "../.env.contracts");
    fs.writeFileSync(envFile, envVars.trim());
    console.log(`\nContract environment variables saved to: ${envFile}`);

    console.log("\n🎉 Deployment completed successfully!");
    console.log("\nContract Addresses:");
    console.log("==================");
    console.log(`FuseToken: ${fuseToken.address}`);
    console.log(`DonationManager: ${donationManager.address}`);
    console.log(`Fee Collector: ${config.donation_manager.feeCollector}`);
    
    console.log("\nNext Steps:");
    console.log("==========");
    console.log("1. Update your backend .env file with the contract addresses");
    console.log("2. Register authors and articles in the DonationManager contract");
    console.log("3. Test the donation functionality");
    console.log("4. Consider setting up a monitoring system for contract events");

    return {
      fuseToken: fuseToken.address,
      donationManager: donationManager.address,
      deploymentInfo
    };

  } catch (error) {
    console.error("Deployment failed:", error);
    process.exit(1);
  }
}

// Execute deployment
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}

module.exports = main;