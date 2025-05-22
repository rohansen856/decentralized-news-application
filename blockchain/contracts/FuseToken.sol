// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title FuseToken (FTK)
 * @dev NFT contract for author donations in the decentralized news platform
 * Each FTK represents a unique donation NFT that can be minted and transferred
 */
contract FuseToken is ERC721, ERC721URIStorage, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Base URI for token metadata
    string private _baseTokenURI;
    
    // Mapping from token ID to donation amount in wei
    mapping(uint256 => uint256) public tokenDonationAmount;
    
    // Mapping from token ID to recipient author address
    mapping(uint256 => address) public tokenRecipient;
    
    // Mapping from token ID to article ID
    mapping(uint256 => string) public tokenArticleId;
    
    // Mapping from token ID to donor address
    mapping(uint256 => address) public tokenDonor;
    
    // Events
    event DonationNFTMinted(
        uint256 indexed tokenId,
        address indexed donor,
        address indexed recipient,
        uint256 amount,
        string articleId
    );
    
    event BaseURIUpdated(string newBaseURI);
    
    constructor(
        string memory name,
        string memory symbol,
        string memory baseURI
    ) ERC721(name, symbol) {
        _baseTokenURI = baseURI;
    }
    
    /**
     * @dev Mint a new donation NFT
     * @param to Address to mint the NFT to (usually the donor)
     * @param recipient Address of the author receiving the donation
     * @param articleId ID of the article being donated for
     * @param donationAmount Amount of the donation in wei
     * @param tokenURI Metadata URI for the NFT
     */
    function mintDonationNFT(
        address to,
        address recipient,
        string memory articleId,
        uint256 donationAmount,
        string memory tokenURI
    ) public payable nonReentrant returns (uint256) {
        require(to != address(0), "FTK: Cannot mint to zero address");
        require(recipient != address(0), "FTK: Invalid recipient address");
        require(bytes(articleId).length > 0, "FTK: Article ID cannot be empty");
        require(donationAmount > 0, "FTK: Donation amount must be positive");
        require(msg.value >= donationAmount, "FTK: Insufficient payment");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        // Store donation metadata
        tokenDonationAmount[tokenId] = donationAmount;
        tokenRecipient[tokenId] = recipient;
        tokenArticleId[tokenId] = articleId;
        tokenDonor[tokenId] = to;
        
        // Mint the NFT
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        // Transfer the donation amount to the recipient
        (bool success, ) = payable(recipient).call{value: donationAmount}("");
        require(success, "FTK: Transfer to recipient failed");
        
        // Refund excess payment if any
        if (msg.value > donationAmount) {
            (bool refundSuccess, ) = payable(msg.sender).call{value: msg.value - donationAmount}("");
            require(refundSuccess, "FTK: Refund failed");
        }
        
        emit DonationNFTMinted(tokenId, to, recipient, donationAmount, articleId);
        
        return tokenId;
    }
    
    /**
     * @dev Get donation details for a token
     */
    function getDonationDetails(uint256 tokenId) 
        public 
        view 
        returns (
            address donor,
            address recipient,
            uint256 amount,
            string memory articleId
        ) 
    {
        require(_exists(tokenId), "FTK: Token does not exist");
        
        return (
            tokenDonor[tokenId],
            tokenRecipient[tokenId],
            tokenDonationAmount[tokenId],
            tokenArticleId[tokenId]
        );
    }
    
    /**
     * @dev Set base URI for token metadata
     */
    function setBaseURI(string memory baseURI) public onlyOwner {
        _baseTokenURI = baseURI;
        emit BaseURIUpdated(baseURI);
    }
    
    /**
     * @dev Get total number of tokens minted
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }
    
    /**
     * @dev Get tokens owned by an address
     */
    function getTokensByOwner(address owner) public view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(owner);
        uint256[] memory tokens = new uint256[](tokenCount);
        uint256 currentIndex = 0;
        
        for (uint256 i = 0; i < _tokenIdCounter.current(); i++) {
            if (ownerOf(i) == owner) {
                tokens[currentIndex] = i;
                currentIndex++;
            }
        }
        
        return tokens;
    }
    
    /**
     * @dev Get tokens donated to a specific recipient
     */
    function getTokensByRecipient(address recipient) public view returns (uint256[] memory) {
        uint256 totalTokens = _tokenIdCounter.current();
        uint256 recipientTokenCount = 0;
        
        // First pass: count tokens for this recipient
        for (uint256 i = 0; i < totalTokens; i++) {
            if (tokenRecipient[i] == recipient) {
                recipientTokenCount++;
            }
        }
        
        // Second pass: collect token IDs
        uint256[] memory tokens = new uint256[](recipientTokenCount);
        uint256 currentIndex = 0;
        
        for (uint256 i = 0; i < totalTokens; i++) {
            if (tokenRecipient[i] == recipient) {
                tokens[currentIndex] = i;
                currentIndex++;
            }
        }
        
        return tokens;
    }
    
    /**
     * @dev Emergency withdrawal function (only owner)
     */
    function emergencyWithdraw() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "FTK: No balance to withdraw");
        
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "FTK: Withdrawal failed");
    }
    
    // Override functions
    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }
    
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}