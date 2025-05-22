// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./FuseToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title DonationManager
 * @dev Manages donation operations and integrates with FuseToken NFTs
 * Handles donation processing, fee collection, and author verification
 */
contract DonationManager is Ownable, ReentrancyGuard, Pausable {
    
    FuseToken public fuseToken;
    
    // Platform fee percentage (in basis points, 100 = 1%)
    uint256 public platformFeePercent = 250; // 2.5%
    
    // Minimum donation amount
    uint256 public minimumDonation = 0.001 ether;
    
    // Maximum donation amount per transaction
    uint256 public maximumDonation = 10 ether;
    
    // Platform fee collector address
    address public feeCollector;
    
    // Mapping to track verified authors
    mapping(address => bool) public verifiedAuthors;
    
    // Mapping to track article to author relationship
    mapping(string => address) public articleToAuthor;
    
    // Mapping to track total donations received by author
    mapping(address => uint256) public authorTotalReceived;
    
    // Mapping to track total donations by donor
    mapping(address => uint256) public donorTotalGiven;
    
    // Mapping to track donations per article
    mapping(string => uint256) public articleTotalDonations;
    
    // Events
    event AuthorVerified(address indexed author, string metadata);
    event AuthorUnverified(address indexed author);
    event ArticleRegistered(string indexed articleId, address indexed author);
    event DonationProcessed(
        address indexed donor,
        address indexed recipient,
        string indexed articleId,
        uint256 amount,
        uint256 platformFee,
        uint256 tokenId
    );
    event PlatformFeeUpdated(uint256 oldFee, uint256 newFee);
    event FeeCollectorUpdated(address oldCollector, address newCollector);
    event DonationLimitsUpdated(uint256 minDonation, uint256 maxDonation);
    
    modifier onlyVerifiedAuthor() {
        require(verifiedAuthors[msg.sender], "DonationManager: Author not verified");
        _;
    }
    
    modifier validDonationAmount(uint256 amount) {
        require(amount >= minimumDonation, "DonationManager: Donation below minimum");
        require(amount <= maximumDonation, "DonationManager: Donation above maximum");
        _;
    }
    
    constructor(
        address _fuseTokenAddress,
        address _feeCollector
    ) {
        require(_fuseTokenAddress != address(0), "DonationManager: Invalid FuseToken address");
        require(_feeCollector != address(0), "DonationManager: Invalid fee collector address");
        
        fuseToken = FuseToken(_fuseTokenAddress);
        feeCollector = _feeCollector;
    }
    
    /**
     * @dev Verify an author address
     */
    function verifyAuthor(address author, string memory metadata) public onlyOwner {
        require(author != address(0), "DonationManager: Invalid author address");
        verifiedAuthors[author] = true;
        emit AuthorVerified(author, metadata);
    }
    
    /**
     * @dev Unverify an author address
     */
    function unverifyAuthor(address author) public onlyOwner {
        verifiedAuthors[author] = false;
        emit AuthorUnverified(author);
    }
    
    /**
     * @dev Register an article with its author
     */
    function registerArticle(string memory articleId, address author) public onlyOwner {
        require(bytes(articleId).length > 0, "DonationManager: Invalid article ID");
        require(verifiedAuthors[author], "DonationManager: Author not verified");
        
        articleToAuthor[articleId] = author;
        emit ArticleRegistered(articleId, author);
    }
    
    /**
     * @dev Process a donation and mint NFT
     */
    function processDonation(
        string memory articleId,
        string memory tokenURI
    ) 
        public 
        payable 
        nonReentrant 
        whenNotPaused
        validDonationAmount(msg.value)
        returns (uint256)
    {
        require(bytes(articleId).length > 0, "DonationManager: Invalid article ID");
        
        address author = articleToAuthor[articleId];
        require(author != address(0), "DonationManager: Article not registered");
        require(verifiedAuthors[author], "DonationManager: Author not verified");
        require(msg.sender != author, "DonationManager: Cannot donate to yourself");
        
        uint256 totalAmount = msg.value;
        uint256 platformFee = (totalAmount * platformFeePercent) / 10000;
        uint256 authorAmount = totalAmount - platformFee;
        
        // Update tracking mappings
        authorTotalReceived[author] += authorAmount;
        donorTotalGiven[msg.sender] += totalAmount;
        articleTotalDonations[articleId] += totalAmount;
        
        // Transfer platform fee
        if (platformFee > 0) {
            (bool feeSuccess, ) = payable(feeCollector).call{value: platformFee}("");
            require(feeSuccess, "DonationManager: Platform fee transfer failed");
        }
        
        // Mint NFT and transfer author amount (handled by FuseToken contract)
        uint256 tokenId = fuseToken.mintDonationNFT{value: authorAmount}(
            msg.sender,
            author,
            articleId,
            authorAmount,
            tokenURI
        );
        
        emit DonationProcessed(
            msg.sender,
            author,
            articleId,
            authorAmount,
            platformFee,
            tokenId
        );
        
        return tokenId;
    }
    
    /**
     * @dev Batch process multiple donations
     */
    function batchProcessDonations(
        string[] memory articleIds,
        string[] memory tokenURIs,
        uint256[] memory amounts
    ) 
        public 
        payable 
        nonReentrant 
        whenNotPaused
        returns (uint256[] memory)
    {
        require(
            articleIds.length == tokenURIs.length && 
            tokenURIs.length == amounts.length,
            "DonationManager: Array lengths mismatch"
        );
        require(articleIds.length > 0, "DonationManager: Empty arrays");
        
        uint256 totalRequired = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            require(amounts[i] >= minimumDonation, "DonationManager: Donation below minimum");
            require(amounts[i] <= maximumDonation, "DonationManager: Donation above maximum");
            totalRequired += amounts[i];
        }
        
        require(msg.value >= totalRequired, "DonationManager: Insufficient payment");
        
        uint256[] memory tokenIds = new uint256[](articleIds.length);
        
        for (uint256 i = 0; i < articleIds.length; i++) {
            // Note: This is a simplified implementation
            // In practice, you'd need to handle individual payments more carefully
            tokenIds[i] = _processSingleDonation(articleIds[i], tokenURIs[i], amounts[i]);
        }
        
        // Refund excess payment
        uint256 excess = msg.value - totalRequired;
        if (excess > 0) {
            (bool refundSuccess, ) = payable(msg.sender).call{value: excess}("");
            require(refundSuccess, "DonationManager: Refund failed");
        }
        
        return tokenIds;
    }
    
    /**
     * @dev Internal function to process a single donation (for batch operations)
     */
    function _processSingleDonation(
        string memory articleId,
        string memory tokenURI,
        uint256 amount
    ) internal returns (uint256) {
        address author = articleToAuthor[articleId];
        require(author != address(0), "DonationManager: Article not registered");
        require(verifiedAuthors[author], "DonationManager: Author not verified");
        
        uint256 platformFee = (amount * platformFeePercent) / 10000;
        uint256 authorAmount = amount - platformFee;
        
        // Update tracking mappings
        authorTotalReceived[author] += authorAmount;
        donorTotalGiven[msg.sender] += amount;
        articleTotalDonations[articleId] += amount;
        
        // Transfer platform fee
        if (platformFee > 0) {
            (bool feeSuccess, ) = payable(feeCollector).call{value: platformFee}("");
            require(feeSuccess, "DonationManager: Platform fee transfer failed");
        }
        
        // Mint NFT
        uint256 tokenId = fuseToken.mintDonationNFT{value: authorAmount}(
            msg.sender,
            author,
            articleId,
            authorAmount,
            tokenURI
        );
        
        emit DonationProcessed(
            msg.sender,
            author,
            articleId,
            authorAmount,
            platformFee,
            tokenId
        );
        
        return tokenId;
    }
    
    /**
     * @dev Get donation statistics for an author
     */
    function getAuthorStats(address author) 
        public 
        view 
        returns (
            bool isVerified,
            uint256 totalReceived,
            uint256[] memory receivedTokens
        ) 
    {
        return (
            verifiedAuthors[author],
            authorTotalReceived[author],
            fuseToken.getTokensByRecipient(author)
        );
    }
    
    /**
     * @dev Get donation statistics for a donor
     */
    function getDonorStats(address donor) 
        public 
        view 
        returns (
            uint256 totalGiven,
            uint256[] memory ownedTokens
        ) 
    {
        return (
            donorTotalGiven[donor],
            fuseToken.getTokensByOwner(donor)
        );
    }
    
    /**
     * @dev Get article donation statistics
     */
    function getArticleStats(string memory articleId) 
        public 
        view 
        returns (
            address author,
            uint256 totalDonations
        ) 
    {
        return (
            articleToAuthor[articleId],
            articleTotalDonations[articleId]
        );
    }
    
    /**
     * @dev Update platform fee percentage (only owner)
     */
    function updatePlatformFee(uint256 newFeePercent) public onlyOwner {
        require(newFeePercent <= 1000, "DonationManager: Fee cannot exceed 10%");
        uint256 oldFee = platformFeePercent;
        platformFeePercent = newFeePercent;
        emit PlatformFeeUpdated(oldFee, newFeePercent);
    }
    
    /**
     * @dev Update fee collector address (only owner)
     */
    function updateFeeCollector(address newFeeCollector) public onlyOwner {
        require(newFeeCollector != address(0), "DonationManager: Invalid fee collector");
        address oldCollector = feeCollector;
        feeCollector = newFeeCollector;
        emit FeeCollectorUpdated(oldCollector, newFeeCollector);
    }
    
    /**
     * @dev Update donation limits (only owner)
     */
    function updateDonationLimits(
        uint256 newMinimum,
        uint256 newMaximum
    ) public onlyOwner {
        require(newMinimum > 0, "DonationManager: Minimum must be positive");
        require(newMaximum > newMinimum, "DonationManager: Maximum must be greater than minimum");
        
        minimumDonation = newMinimum;
        maximumDonation = newMaximum;
        emit DonationLimitsUpdated(newMinimum, newMaximum);
    }
    
    /**
     * @dev Pause contract (only owner)
     */
    function pause() public onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause contract (only owner)
     */
    function unpause() public onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency withdrawal (only owner)
     */
    function emergencyWithdraw() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "DonationManager: No balance to withdraw");
        
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "DonationManager: Withdrawal failed");
    }
}