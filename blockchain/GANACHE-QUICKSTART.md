# 🚀 Ganache Quick Start Guide

This guide will help you set up the FuseToken donation system with Ganache for local development.

## Prerequisites

- Node.js (v16+)
- NPM or Yarn
- Ganache CLI

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd blockchain
npm install
```

### 2. Install and Start Ganache

```bash
# Install Ganache CLI globally
npm install -g ganache-cli

# Start Ganache with deterministic accounts
ganache-cli --port 7545 --deterministic --accounts 10 --defaultBalanceEther 10000 --gasLimit 8000000
```

**Ganache will provide you with:**
- 10 test accounts with 10,000 ETH each
- Deterministic addresses (same every time)
- Local blockchain on http://127.0.0.1:7545

### 3. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# The default values are already configured for Ganache
# No changes needed for basic Ganache development
```

### 4. Deploy Contracts

```bash
# Compile and deploy contracts to Ganache
npm run compile
npm run deploy:ganache
```

This will deploy:
- ✅ FuseToken (FTK) NFT contract
- ✅ DonationManager contract
- ✅ Configure ownership and permissions

### 5. Setup Test Data

```bash
# Setup with realistic test data
npm run setup:ganache
```

This will:
- ✅ Verify 2 test authors
- ✅ Register 3 test articles
- ✅ Create 3 test donations
- ✅ Generate development configuration

### 6. Configure Backend

```bash
# Copy Ganache environment to backend
cp ../backend/.env.ganache ../backend/.env
```

## Test Accounts

After setup, you'll have these test accounts:

| Role | Address | Description |
|------|---------|-------------|
| Deployer | `0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1` | Contract deployer & admin |
| Author 1 | `0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0` | Alice Smith (Tech journalist) |
| Author 2 | `0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b` | Bob Johnson (Science writer) |
| Donor 1 | `0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d` | Test donor account |
| Donor 2 | `0xd03ea8624C8C5987235048901fB614fDcA89b117` | Test donor account |

## Test Articles

Pre-registered articles for testing:

1. **"The Future of Blockchain Technology"** by Alice Smith
2. **"Decentralized Finance: A Beginner's Guide"** by Alice Smith  
3. **"Climate Change and Technology Solutions"** by Bob Johnson

## Verification

After setup, verify everything works:

```bash
# Check contract status
npx hardhat console --network ganache

# In console:
const DonationManager = await ethers.getContractFactory("DonationManager");
const dm = await DonationManager.attach("DONATION_MANAGER_ADDRESS");
await dm.platformFeePercent(); // Should return 250 (2.5%)
```

## Frontend Development

Your frontend can now connect to:
- **Network**: Ganache (Chain ID: 1337)
- **RPC URL**: http://127.0.0.1:7545
- **Contracts**: Check `deployments/ganache-dev-config.json`

## Testing Donations

You can test donations using MetaMask:

1. **Add Ganache Network to MetaMask:**
   - Network Name: Ganache
   - RPC URL: http://127.0.0.1:7545
   - Chain ID: 1337
   - Currency Symbol: ETH

2. **Import Test Accounts:**
   Use the private keys from Ganache CLI output

3. **Test Donation Flow:**
   - Connect as a donor account
   - Donate to any registered article
   - Receive FTK NFT as proof

## Troubleshooting

### Ganache Connection Issues
```bash
# Make sure Ganache is running on port 7545
netstat -an | grep 7545

# Restart Ganache if needed
pkill -f ganache
ganache-cli --port 7545 --deterministic --accounts 10 --defaultBalanceEther 10000
```

### Contract Deployment Issues
```bash
# Clean and recompile
rm -rf cache artifacts
npm run compile
npm run deploy:ganache
```

### Reset Everything
```bash
# Stop Ganache and restart with clean state
pkill -f ganache
rm -rf deployments/ganache-*
ganache-cli --port 7545 --deterministic --accounts 10 --defaultBalanceEther 10000
npm run deploy:ganache
npm run setup:ganache
```

## Next Steps

1. **Start Backend**: Copy the generated `.env.ganache` to your backend
2. **Test API**: Use the donation endpoints with test accounts
3. **Frontend Integration**: Connect your React app to Ganache
4. **Development**: Build and test your features

## File Locations

- **Contract Addresses**: `deployments/ganache-latest.json`
- **Development Config**: `deployments/ganache-dev-config.json`
- **Backend Environment**: `../backend/.env.ganache`
- **Test Data**: `scripts/ganache-setup.js`

---

🎉 **You're all set!** Your local FuseToken donation system is ready for development.