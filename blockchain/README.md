# FuseToken (FTK) NFT Donation System

A blockchain-based donation system for content creators using NFT tokens as proof of support.

## Overview

The FuseToken system enables readers to donate to authors using cryptocurrency and receive unique NFT tokens (FTK) as proof of their contribution. The system consists of two main smart contracts:

- **FuseToken.sol**: ERC721 NFT contract that mints unique donation tokens
- **DonationManager.sol**: Manages the donation process, author verification, and fee collection

## Features

- ✅ NFT-based donation receipts
- ✅ Author verification system
- ✅ Configurable platform fees
- ✅ Multiple donation support (batch donations)
- ✅ Anonymous donation option
- ✅ Donation statistics and analytics
- ✅ Emergency withdrawal functions
- ✅ Pausable contract for security

## Smart Contracts

### FuseToken.sol
- ERC721 compliant NFT contract
- Stores donation metadata on-chain
- Tracks donor, recipient, and article information
- Supports custom token URIs for metadata

### DonationManager.sol
- Manages donation processing
- Handles author verification
- Collects platform fees
- Provides donation statistics
- Supports batch operations

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Compile contracts:**
   ```bash
   npm run compile
   ```

4. **Run tests:**
   ```bash
   npm run test
   ```

## Deployment

### Local Development

#### Option 1: Using Hardhat Network
1. **Start local blockchain:**
   ```bash
   npm run node
   ```

2. **Deploy contracts:**
   ```bash
   npm run deploy:local
   ```

3. **Setup system:**
   ```bash
   npm run setup:local
   ```

#### Option 2: Using Ganache (Recommended for Development)
1. **Install and start Ganache:**
   ```bash
   # Install Ganache CLI globally
   npm install -g ganache-cli
   
   # Start Ganache on port 7545 with deterministic accounts
   ganache-cli --port 7545 --deterministic --accounts 10 --defaultBalanceEther 10000
   ```

2. **Deploy contracts to Ganache:**
   ```bash
   npm run deploy:ganache
   ```

3. **Setup system with test data:**
   ```bash
   npm run setup:ganache
   ```

4. **Copy environment variables to backend:**
   ```bash
   cp ../backend/.env.ganache ../backend/.env
   ```

### Testnet Deployment

1. **Deploy to Sepolia:**
   ```bash
   npm run deploy:testnet
   ```

2. **Setup system:**
   ```bash
   npm run setup:testnet
   ```

### Mainnet Deployment

1. **Deploy to mainnet:**
   ```bash
   npm run deploy:mainnet
   ```

2. **Setup system:**
   ```bash
   npm run setup:mainnet
   ```

## Configuration

### Environment Variables

Required environment variables for deployment:

```env
PRIVATE_KEY=your_wallet_private_key
SEPOLIA_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
ETHERSCAN_API_KEY=your_etherscan_api_key
NFT_BASE_URI=https://api.yourapp.com/nft-metadata/
FEE_COLLECTOR_ADDRESS=0x742d35Cc6635C0532925a3b8D52C1Cf6E592e6F2
```

### Contract Configuration

- **Platform Fee**: 2.5% (250 basis points)
- **Minimum Donation**: 0.001 ETH
- **Maximum Donation**: 10 ETH
- **NFT Symbol**: FTK (FuseToken)

## Usage

### For Administrators

1. **Verify Authors:**
   ```javascript
   await donationManager.verifyAuthor(authorAddress, metadata);
   ```

2. **Register Articles:**
   ```javascript
   await donationManager.registerArticle(articleId, authorAddress);
   ```

### For Users

1. **Make Donation:**
   ```javascript
   await donationManager.processDonation(
     articleId,
     tokenURI,
     { value: ethers.utils.parseEther("0.1") }
   );
   ```

2. **Batch Donations:**
   ```javascript
   await donationManager.batchProcessDonations(
     articleIds,
     tokenURIs,
     amounts,
     { value: totalAmount }
   );
   ```

## Security Considerations

- All contracts are pausable for emergency situations
- Reentrancy protection on all payable functions
- Access control for administrative functions
- Input validation on all public functions
- Emergency withdrawal mechanisms

## Gas Optimization

The contracts are optimized for gas efficiency:
- Batch operations to reduce multiple transaction costs
- Efficient storage patterns
- Minimal external calls
- Optimized loop structures

## Integration

### Backend Integration

The smart contracts integrate with the backend API to:
- Track donation transactions
- Update payment status
- Generate NFT metadata
- Provide donation statistics

### Frontend Integration

The frontend uses these contracts to:
- Display donation interfaces
- Show NFT collections
- Provide donation statistics
- Handle wallet connections

## Testing

Run the complete test suite:

```bash
npm run test
npm run coverage
```

## License

MIT License - see LICENSE file for details.

## Support

For technical support or questions about the FuseToken donation system, please contact the development team.