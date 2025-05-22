const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Starting deployment of FuseToken NFT donation system...");
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  // Configuration
  const config = {
    fuse_token: {
      name: "FuseToken",
      symbol: "FTK",
      baseURI: process.env.NFT_BASE_URI || "http://localhost:8000/api/v1/nft-metadata/"
    },
    donation_manager: {
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
    const fuseTokenAddress = await fuseToken.getAddress();
    console.log("FuseToken deployed to:", fuseTokenAddress);

    // Deploy DonationManager contract
    console.log("\n2. Deploying DonationManager contract...");
    const DonationManager = await ethers.getContractFactory("DonationManager");
    const donationManager = await DonationManager.deploy(
      fuseTokenAddress,
      config.donation_manager.feeCollector
    );
    await donationManager.waitForDeployment();
    const donationManagerAddress = await donationManager.getAddress();
    console.log("DonationManager deployed to:", donationManagerAddress);

    // Transfer ownership of FuseToken to DonationManager
    console.log("\n3. Transferring FuseToken ownership to DonationManager...");
    const transferTx = await fuseToken.transferOwnership(donationManagerAddress);
    await transferTx.wait();
    console.log("Ownership transferred successfully");

    // Get network info
    const network = await ethers.provider.getNetwork();
    console.log("Network:", network.name, "Chain ID:", network.chainId.toString());

    // Save deployment information
    const deploymentInfo = {
      network: network.name,
      chainId: network.chainId.toString(),
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      contracts: {
        FuseToken: {
          address: fuseTokenAddress,
          constructorArgs: [
            config.fuse_token.name,
            config.fuse_token.symbol,
            config.fuse_token.baseURI
          ]
        },
        DonationManager: {
          address: donationManagerAddress,
          constructorArgs: [
            fuseTokenAddress,
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
FUSE_TOKEN_CONTRACT=${fuseTokenAddress}
DONATION_MANAGER_CONTRACT=${donationManagerAddress}
FEE_COLLECTOR_ADDRESS=${config.donation_manager.feeCollector}
PLATFORM_FEE_PERCENT=250
NFT_BASE_URI=${config.fuse_token.baseURI}
BLOCKCHAIN_NETWORK=${network.name}
CHAIN_ID=${network.chainId.toString()}
`;

    const envFile = path.join(__dirname, "../.env.contracts");
    fs.writeFileSync(envFile, envVars.trim());
    console.log(`\nContract environment variables saved to: ${envFile}`);

    console.log("\n🎉 Deployment completed successfully!");
    console.log("\nContract Addresses:");
    console.log("==================");
    console.log(`FuseToken: ${fuseTokenAddress}`);
    console.log(`DonationManager: ${donationManagerAddress}`);
    console.log(`Fee Collector: ${config.donation_manager.feeCollector}`);
    
    console.log("\nNext Steps:");
    console.log("==========");
    console.log("1. Run setup script: npm run setup:ganache");
    console.log("2. Update your backend .env file with the contract addresses");
    console.log("3. Test the donation functionality");

    return {
      fuseToken: fuseTokenAddress,
      donationManager: donationManagerAddress,
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