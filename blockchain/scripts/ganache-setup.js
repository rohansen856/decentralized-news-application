const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * Ganache-specific setup script with test data
 * This script sets up the donation system with realistic test data for development
 */

async function main() {
  console.log("Setting up FuseToken donation system for Ganache development...");

  const accounts = await ethers.getSigners();
  const deployer = accounts[0];
  const author1 = accounts[1];
  const author2 = accounts[2];
  const donor1 = accounts[3];
  const donor2 = accounts[4];

  console.log("Using accounts:");
  console.log("Deployer:", deployer.address);
  console.log("Author 1:", author1.address);
  console.log("Author 2:", author2.address);
  console.log("Donor 1:", donor1.address);
  console.log("Donor 2:", donor2.address);

  // Load deployment info
  const network = await ethers.provider.getNetwork();
  const deploymentFile = path.join(__dirname, "../deployments", `${network.name}-latest.json`);
  
  if (!fs.existsSync(deploymentFile)) {
    console.error("Deployment file not found. Please deploy contracts first using 'npm run deploy:ganache'");
    process.exit(1);
  }

  const deploymentInfo = JSON.parse(fs.readFileSync(deploymentFile, 'utf8'));
  const { FuseToken: fuseTokenInfo, DonationManager: donationManagerInfo } = deploymentInfo.contracts;

  // Connect to deployed contracts
  const FuseToken = await ethers.getContractFactory("FuseToken");
  const fuseToken = FuseToken.attach(fuseTokenInfo.address);

  const DonationManager = await ethers.getContractFactory("DonationManager");
  const donationManager = DonationManager.attach(donationManagerInfo.address);

  console.log("\nConnected to contracts:");
  console.log("FuseToken:", fuseTokenInfo.address);
  console.log("DonationManager:", donationManagerInfo.address);

  try {
    console.log("\n1. Verifying test authors...");
    
    // Verify authors
    const authors = [
      { address: author1.address, name: "Alice Smith", bio: "Tech journalist" },
      { address: author2.address, name: "Bob Johnson", bio: "Science writer" }
    ];

    for (const author of authors) {
      try {
        const metadata = JSON.stringify({
          name: author.name,
          bio: author.bio,
          verified_by: "ganache_setup",
          verified_at: new Date().toISOString()
        });
        
        const tx = await donationManager.verifyAuthor(author.address, metadata);
        await tx.wait();
        console.log(`✅ Verified author: ${author.name} (${author.address})`);
      } catch (error) {
        if (error.message.includes("already verified")) {
          console.log(`⚠️  Author already verified: ${author.name}`);
        } else {
          console.log(`❌ Failed to verify author ${author.name}:`, error.message);
        }
      }
    }

    console.log("\n2. Registering test articles...");
    
    // Test articles
    const testArticles = [
      {
        id: "550e8400-e29b-41d4-a716-446655440001",
        author: author1.address,
        title: "The Future of Blockchain Technology",
        author_name: "Alice Smith"
      },
      {
        id: "550e8400-e29b-41d4-a716-446655440002",
        author: author1.address,
        title: "Decentralized Finance: A Beginner's Guide",
        author_name: "Alice Smith"
      },
      {
        id: "550e8400-e29b-41d4-a716-446655440003",
        author: author2.address,
        title: "Climate Change and Technology Solutions",
        author_name: "Bob Johnson"
      }
    ];

    for (const article of testArticles) {
      try {
        const tx = await donationManager.registerArticle(article.id, article.author);
        await tx.wait();
        console.log(`✅ Registered article: "${article.title}" by ${article.author_name}`);
      } catch (error) {
        if (error.message.includes("already registered")) {
          console.log(`⚠️  Article already registered: "${article.title}"`);
        } else {
          console.log(`❌ Failed to register article "${article.title}":`, error.message);
        }
      }
    }

    console.log("\n3. Creating test donations...");
    
    // Test donations
    const testDonations = [
      {
        donor: donor1,
        articleId: testArticles[0].id,
        amount: "0.05",
        message: "Great article! Keep up the good work!"
      },
      {
        donor: donor2,
        articleId: testArticles[0].id,
        amount: "0.1",
        message: "Very informative piece."
      },
      {
        donor: donor1,
        articleId: testArticles[2].id,
        amount: "0.025",
        message: "Important topic, thanks for covering it."
      }
    ];

    for (const donation of testDonations) {
      try {
        const amount = ethers.parseEther(donation.amount);
        const tokenURI = `http://localhost:8000/api/v1/nft-metadata/${donation.articleId}`;
        
        const tx = await donationManager.connect(donation.donor).processDonation(
          donation.articleId,
          tokenURI,
          { value: amount }
        );
        
        const receipt = await tx.wait();
        console.log(`✅ Donation of ${donation.amount} ETH processed successfully`);
        console.log(`   Transaction: ${receipt.hash}`);
      } catch (error) {
        console.log(`❌ Failed to process donation of ${donation.amount} ETH:`, error.message);
      }
    }

    console.log("\n4. Generating development configuration...");
    
    // Get current stats for verification
    const totalSupply = await fuseToken.totalSupply();
    const platformFee = await donationManager.platformFeePercent();
    const minDonation = await donationManager.minimumDonation();
    const maxDonation = await donationManager.maximumDonation();

    // Generate development configuration
    const devConfig = {
      network: {
        name: network.name,
        chainId: network.chainId.toString(),
        url: "http://127.0.0.1:7545"
      },
      contracts: {
        fuseToken: fuseTokenInfo.address,
        donationManager: donationManagerInfo.address
      },
      accounts: {
        deployer: deployer.address,
        feeCollector: await donationManager.feeCollector(),
        authors: authors.map(a => ({ address: a.address, name: a.name })),
        donors: [
          { address: donor1.address, name: "Donor 1" },
          { address: donor2.address, name: "Donor 2" }
        ]
      },
      testData: {
        articles: testArticles,
        donations: testDonations.map(d => ({
          donor: d.donor.address,
          articleId: d.articleId,
          amount: d.amount,
          message: d.message
        }))
      },
      stats: {
        totalNFTs: totalSupply.toString(),
        platformFeePercent: platformFee.toString(),
        minDonation: ethers.formatEther(minDonation),
        maxDonation: ethers.formatEther(maxDonation)
      }
    };

    // Save development configuration
    const deploymentsDir = path.join(__dirname, "../deployments");
    if (!fs.existsSync(deploymentsDir)) {
      fs.mkdirSync(deploymentsDir, { recursive: true });
    }

    const devConfigFile = path.join(deploymentsDir, "ganache-dev-config.json");
    fs.writeFileSync(devConfigFile, JSON.stringify(devConfig, null, 2));
    console.log(`Development configuration saved to: ${devConfigFile}`);

    // Generate .env for backend
    const backendEnv = `
# Ganache Development Configuration
FUSE_TOKEN_CONTRACT=${fuseTokenInfo.address}
DONATION_MANAGER_CONTRACT=${donationManagerInfo.address}
FEE_COLLECTOR_ADDRESS=${await donationManager.feeCollector()}
PLATFORM_FEE_PERCENT=${platformFee.toString()}
NFT_BASE_URI=http://localhost:8000/api/v1/nft-metadata/
BLOCKCHAIN_NETWORK=ganache
CHAIN_ID=${network.chainId.toString()}
GANACHE_URL=http://127.0.0.1:7545

# Test Accounts
DEPLOYER_ADDRESS=${deployer.address}
AUTHOR1_ADDRESS=${author1.address}
AUTHOR2_ADDRESS=${author2.address}
DONOR1_ADDRESS=${donor1.address}
DONOR2_ADDRESS=${donor2.address}
`;

    const backendEnvFile = path.join(__dirname, "../../backend/.env.ganache");
    fs.writeFileSync(backendEnvFile, backendEnv.trim());
    console.log(`Backend environment file saved to: ${backendEnvFile}`);

    console.log("\n🎉 Ganache setup completed successfully!");
    console.log("\nDevelopment Environment Ready:");
    console.log("==============================");
    console.log(`Network: ${network.name} (Chain ID: ${network.chainId.toString()})`);
    console.log(`FuseToken: ${fuseTokenInfo.address}`);
    console.log(`DonationManager: ${donationManagerInfo.address}`);
    console.log(`Total NFTs minted: ${totalSupply.toString()}`);
    
    console.log("\nTest Accounts:");
    console.log("==============");
    authors.forEach(author => {
      console.log(`📝 ${author.name}: ${author.address}`);
    });
    console.log(`💰 Donor 1: ${donor1.address}`);
    console.log(`💰 Donor 2: ${donor2.address}`);
    
    console.log("\nNext Steps:");
    console.log("===========");
    console.log("1. Copy backend/.env.ganache to backend/.env");
    console.log("2. Start your backend server");
    console.log("3. Test the donation functionality");
    console.log("4. Use the test accounts for frontend development");

  } catch (error) {
    console.error("Setup failed:", error);
    process.exit(1);
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

module.exports = main;