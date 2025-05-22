const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * Setup script to initialize the donation system after deployment
 * This script handles:
 * - Author verification
 * - Article registration
 * - Initial configuration
 */

async function main() {
  console.log("Setting up FuseToken donation system...");

  const [deployer] = await ethers.getSigners();
  console.log("Setup account:", deployer.address);

  // Load deployment info
  const network = await ethers.provider.getNetwork();
  const deploymentFile = path.join(__dirname, "../deployments", `${network.name}-latest.json`);
  
  if (!fs.existsSync(deploymentFile)) {
    console.error("Deployment file not found. Please deploy contracts first.");
    process.exit(1);
  }

  const deploymentInfo = JSON.parse(fs.readFileSync(deploymentFile, 'utf8'));
  const { FuseToken: fuseTokenInfo, DonationManager: donationManagerInfo } = deploymentInfo.contracts;

  // Connect to deployed contracts
  const FuseToken = await ethers.getContractFactory("FuseToken");
  const fuseToken = FuseToken.attach(fuseTokenInfo.address);

  const DonationManager = await ethers.getContractFactory("DonationManager");
  const donationManager = DonationManager.attach(donationManagerInfo.address);

  console.log("Connected to contracts:");
  console.log("FuseToken:", fuseTokenInfo.address);
  console.log("DonationManager:", donationManagerInfo.address);

  try {
    // Example setup operations
    console.log("\n1. Verifying contract setup...");
    
    // Check if DonationManager is the owner of FuseToken
    const fuseTokenOwner = await fuseToken.owner();
    console.log("FuseToken owner:", fuseTokenOwner);
    
    if (fuseTokenOwner.toLowerCase() !== donationManagerInfo.address.toLowerCase()) {
      console.log("⚠️  Warning: DonationManager is not the owner of FuseToken");
    } else {
      console.log("✅ DonationManager correctly owns FuseToken");
    }

    // Check donation manager configuration
    const platformFee = await donationManager.platformFeePercent();
    const feeCollector = await donationManager.feeCollector();
    const minDonation = await donationManager.minimumDonation();
    const maxDonation = await donationManager.maximumDonation();

    console.log("\nDonationManager Configuration:");
    console.log("Platform Fee:", platformFee.toString(), "basis points");
    console.log("Fee Collector:", feeCollector);
    console.log("Min Donation:", ethers.utils.formatEther(minDonation), "ETH");
    console.log("Max Donation:", ethers.utils.formatEther(maxDonation), "ETH");

    // Example: Verify some test authors (replace with actual author addresses)
    const testAuthors = [
      // Add test author addresses here
      // "0x742d35Cc6635C0532925a3b8D52C1Cf6E592e6F2",
      // "0x8ba1f109551bD432803012645Hac136c54EaA95",
    ];

    if (testAuthors.length > 0) {
      console.log("\n2. Verifying test authors...");
      for (const authorAddress of testAuthors) {
        try {
          const tx = await donationManager.verifyAuthor(
            authorAddress,
            JSON.stringify({ verified_by: "setup_script", timestamp: Date.now() })
          );
          await tx.wait();
          console.log(`✅ Verified author: ${authorAddress}`);
        } catch (error) {
          console.log(`❌ Failed to verify author ${authorAddress}:`, error.message);
        }
      }
    }

    // Example: Register test articles (replace with actual article IDs and authors)
    const testArticles = [
      // Add test articles here
      // { id: "550e8400-e29b-41d4-a716-446655440000", author: "0x742d35Cc6635C0532925a3b8D52C1Cf6E592e6F2" },
    ];

    if (testArticles.length > 0) {
      console.log("\n3. Registering test articles...");
      for (const article of testArticles) {
        try {
          const tx = await donationManager.registerArticle(article.id, article.author);
          await tx.wait();
          console.log(`✅ Registered article: ${article.id} -> ${article.author}`);
        } catch (error) {
          console.log(`❌ Failed to register article ${article.id}:`, error.message);
        }
      }
    }

    console.log("\n4. Creating sample donation (if test mode)...");
    if (process.env.NODE_ENV === 'test' && testArticles.length > 0) {
      try {
        const testAmount = ethers.utils.parseEther("0.001");
        const tx = await donationManager.processDonation(
          testArticles[0].id,
          "https://example.com/nft-metadata/test",
          { value: testAmount }
        );
        const receipt = await tx.wait();
        console.log("✅ Test donation successful, transaction:", receipt.transactionHash);
      } catch (error) {
        console.log("❌ Test donation failed:", error.message);
      }
    }

    // Generate frontend configuration
    const frontendConfig = {
      contracts: {
        fuseToken: fuseTokenInfo.address,
        donationManager: donationManagerInfo.address
      },
      network: {
        name: network.name,
        chainId: network.chainId
      },
      config: {
        platformFeePercent: platformFee.toString(),
        minDonation: ethers.utils.formatEther(minDonation),
        maxDonation: ethers.utils.formatEther(maxDonation)
      }
    };

    const configFile = path.join(__dirname, "../deployments", "frontend-config.json");
    fs.writeFileSync(configFile, JSON.stringify(frontendConfig, null, 2));
    console.log(`\nFrontend configuration saved to: ${configFile}`);

    console.log("\n🎉 Setup completed successfully!");
    console.log("\nSystem is ready for donations!");
    
  } catch (error) {
    console.error("Setup failed:", error);
    process.exit(1);
  }
}

// Helper function to verify an author
async function verifyAuthor(donationManager, authorAddress, metadata = {}) {
  try {
    const tx = await donationManager.verifyAuthor(
      authorAddress,
      JSON.stringify(metadata)
    );
    await tx.wait();
    console.log(`✅ Verified author: ${authorAddress}`);
    return true;
  } catch (error) {
    console.log(`❌ Failed to verify author ${authorAddress}:`, error.message);
    return false;
  }
}

// Helper function to register an article
async function registerArticle(donationManager, articleId, authorAddress) {
  try {
    const tx = await donationManager.registerArticle(articleId, authorAddress);
    await tx.wait();
    console.log(`✅ Registered article: ${articleId} -> ${authorAddress}`);
    return true;
  } catch (error) {
    console.log(`❌ Failed to register article ${articleId}:`, error.message);
    return false;
  }
}

// Execute setup
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}

module.exports = {
  main,
  verifyAuthor,
  registerArticle
};