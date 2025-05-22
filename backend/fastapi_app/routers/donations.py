"""
NFT donation endpoints for FastAPI
"""

import sys
import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.models import (
    DonationRequest,
    BatchDonationRequest,
    DonationResponse,
    BatchDonationResponse,
    AuthorPaymentResponse,
    AuthorStatsResponse,
    DonorStatsResponse,
    NFTDetailsResponse,
    VerifyAuthorRequest,
    RegisterArticleRequest,
    PaymentStatus,
    PaymentType,
    BlockchainNetwork,
    BaseResponse
)
from shared.database import get_postgres_cursor
from ..dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

FUSE_TOKEN_CONTRACT = os.getenv("FUSE_TOKEN_CONTRACT", "0x59d3631c86BbE35EF041872d502F218A39FBa150")
DONATION_MANAGER_CONTRACT = os.getenv("DONATION_MANAGER_CONTRACT", "0x0290FB167208Af455bB137780163b7B7a9a10C16")
PLATFORM_FEE_PERCENT = int(os.getenv("PLATFORM_FEE_PERCENT", 250)) # 2.5% fee, stored as basis points (10000 = 100%)


@router.post("/donate", response_model=DonationResponse)
async def create_donation(
    donation: DonationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    """
    Create a new NFT donation for an article
    """
    try:
        # Validate article exists and get author
        with get_postgres_cursor() as cursor:
            article_query = """
                SELECT id, author_id, title 
                FROM articles 
                WHERE id = %s AND status = 'published'
            """
            cursor.execute(article_query, (str(donation.article_id),))
            article_result = cursor.fetchone()
        
        if not article_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found or not published"
            )
        
        author_id = article_result[1]
        article_title = article_result[2]
        
        # Check if user is not donating to themselves
        if current_user['id'] == author_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot donate to your own article"
            )
        
        # Get author's wallet address
        with get_postgres_cursor() as cursor:
            author_query = """
                SELECT did_address 
                FROM users 
                WHERE id = %s AND did_address IS NOT NULL
            """
            cursor.execute(author_query, (str(author_id),))
            author_result = cursor.fetchone()
        
        if not author_result or not author_result[0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author does not have a verified wallet address"
            )
        
        # Calculate fees
        platform_fee = (donation.amount * PLATFORM_FEE_PERCENT) / 10000
        net_amount = donation.amount - platform_fee
        
        # Generate unique token ID and transaction hash (mock for now)
        token_id = str(uuid.uuid4())
        transaction_hash = f"0x{uuid.uuid4().hex}"
        
        # Create payment record
        payment_id = uuid.uuid4()
        with get_postgres_cursor() as cursor:
            insert_query = """
                INSERT INTO author_payments (
                    id, author_id, article_id, donor_id, nft_token_id,
                    contract_address, donation_manager_address, amount,
                    platform_fee, net_amount, currency, transaction_hash,
                    payment_status, payment_type, blockchain_network,
                    token_uri, metadata, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, author_id, article_id, donor_id, nft_token_id, contract_address,
                         donation_manager_address, amount, platform_fee, net_amount, currency,
                         transaction_hash, payment_status, payment_type, blockchain_network,
                         token_uri, metadata, created_at, confirmed_at, processed_at
            """
            
            metadata = {
                "article_title": article_title,
                "message": donation.message,
                "anonymous": donation.anonymous
            }
            
            cursor.execute(insert_query, (
                str(payment_id),
                str(author_id),
                str(donation.article_id),
                str(current_user['id']) if not donation.anonymous else None,
                token_id,
                FUSE_TOKEN_CONTRACT,
                DONATION_MANAGER_CONTRACT,
                donation.amount,
                platform_fee,
                net_amount,
                "ETH",
                transaction_hash,
                PaymentStatus.PENDING.value,
                PaymentType.NFT_DONATION.value,
                BlockchainNetwork.ETHEREUM.value,
                donation.token_uri,
                str(metadata),
                datetime.now()
            ))
            
            payment_record = cursor.fetchone()
        
        # Schedule background task to process blockchain transaction
        background_tasks.add_task(
            process_blockchain_donation,
            payment_id,
            donation.amount,
            author_result[0],
            current_user.get('did_address'),
            str(donation.article_id)
        )
        
        # Convert to response model
        payment_response = AuthorPaymentResponse(
            id=uuid.UUID(str(payment_record[0])),
            author_id=uuid.UUID(str(payment_record[1])),
            article_id=uuid.UUID(str(payment_record[2])),
            donor_id=uuid.UUID(str(payment_record[3])) if payment_record[3] else None,
            nft_token_id=payment_record[4],
            contract_address=payment_record[5],
            donation_manager_address=payment_record[6],
            amount=float(payment_record[7]),
            platform_fee=float(payment_record[8]),
            net_amount=float(payment_record[9]),
            currency=payment_record[10],
            transaction_hash=payment_record[11],
            payment_status=PaymentStatus(payment_record[12]),
            payment_type=PaymentType(payment_record[13]),
            blockchain_network=BlockchainNetwork(payment_record[14]),
            token_uri=payment_record[15],
            metadata=eval(payment_record[16]) if payment_record[16] else {},
            created_at=payment_record[17],
            confirmed_at=payment_record[18],
            processed_at=payment_record[19]
        )
        
        return DonationResponse(
            payment=payment_response,
            token_id=int(token_id.replace('-', '')[:8], 16),  # Convert UUID to int
            transaction_hash=transaction_hash
        )
        
    except Exception as e:
        logger.error(f"Error creating donation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process donation"
        )


@router.get("/stats/author/{author_id}", response_model=AuthorStatsResponse)
async def get_author_stats(author_id: str):
    """
    Get donation statistics for an author
    """
    try:
        # Get basic stats
        with get_postgres_cursor() as cursor:
            stats_query = """
                SELECT 
                    COUNT(*) as total_donations,
                    COALESCE(SUM(net_amount), 0) as total_received,
                    COALESCE(AVG(net_amount), 0) as average_donation
                FROM author_payments 
                WHERE author_id = %s AND payment_status = 'confirmed'
            """
            cursor.execute(stats_query, (author_id,))
            stats_result = cursor.fetchone()
        
        # Get top articles by donation amount
        with get_postgres_cursor() as cursor:
            top_articles_query = """
                SELECT 
                    a.id,
                    a.title,
                    COUNT(ap.id) as donation_count,
                    COALESCE(SUM(ap.net_amount), 0) as total_received
                FROM articles a
                LEFT JOIN author_payments ap ON a.id = ap.article_id AND ap.payment_status = 'confirmed'
                WHERE a.author_id = %s
                GROUP BY a.id, a.title
                ORDER BY total_received DESC
                LIMIT 5
            """
            cursor.execute(top_articles_query, (author_id,))
            top_articles = cursor.fetchall()
        
        # Get recent donations
        with get_postgres_cursor() as cursor:
            recent_donations_query = """
                SELECT * FROM author_payments
                WHERE author_id = %s AND payment_status = 'confirmed'
                ORDER BY created_at DESC
                LIMIT 10
            """
            cursor.execute(recent_donations_query, (author_id,))
            recent_donations = cursor.fetchall()
        
        return AuthorStatsResponse(
            author_id=uuid.UUID(author_id),
            total_received=float(stats_result[1]),
            total_donations=stats_result[0],
            total_nfts=stats_result[0],  # Assuming 1 NFT per donation
            average_donation=float(stats_result[2]),
            top_articles=[{
                "id": str(article[0]),
                "title": article[1],
                "donation_count": article[2],
                "total_received": float(article[3])
            } for article in top_articles],
            recent_donations=[]  # Simplified for now
        )
        
    except Exception as e:
        logger.error(f"Error getting author stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author statistics"
        )


@router.get("/stats/donor/{donor_id}", response_model=DonorStatsResponse)
async def get_donor_stats(donor_id: str):
    """
    Get donation statistics for a donor
    """
    try:
        # Get basic stats
        with get_postgres_cursor() as cursor:
            stats_query = """
                SELECT 
                    COUNT(*) as total_donations,
                    COALESCE(SUM(amount), 0) as total_given
                FROM author_payments 
                WHERE donor_id = %s AND payment_status = 'confirmed'
            """
            cursor.execute(stats_query, (donor_id,))
            stats_result = cursor.fetchone()
        
        # Get favorite authors (most donated to)
        with get_postgres_cursor() as cursor:
            favorite_authors_query = """
                SELECT 
                    u.id,
                    u.username,
                    COUNT(ap.id) as donation_count,
                    COALESCE(SUM(ap.amount), 0) as total_donated
                FROM users u
                JOIN author_payments ap ON u.id = ap.author_id
                WHERE ap.donor_id = %s AND ap.payment_status = 'confirmed'
                GROUP BY u.id, u.username
                ORDER BY total_donated DESC
                LIMIT 5
            """
            cursor.execute(favorite_authors_query, (donor_id,))
            favorite_authors = cursor.fetchall()
        
        return DonorStatsResponse(
            donor_id=uuid.UUID(donor_id),
            total_given=float(stats_result[1]),
            total_donations=stats_result[0],
            total_nfts_owned=stats_result[0],
            favorite_authors=[{
                "id": str(author[0]),
                "username": author[1],
                "donation_count": author[2],
                "total_donated": float(author[3])
            } for author in favorite_authors],
            recent_donations=[]  # Simplified for now
        )
        
    except Exception as e:
        logger.error(f"Error getting donor stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get donor statistics"
        )


@router.get("/nft/{token_id}", response_model=NFTDetailsResponse)
async def get_nft_details(token_id: str):
    """
    Get details of a specific NFT donation token
    """
    try:
        with get_postgres_cursor() as cursor:
            query = """
                SELECT 
                    ap.*,
                    u_donor.did_address as donor_address,
                    u_author.did_address as author_address
                FROM author_payments ap
                LEFT JOIN users u_donor ON ap.donor_id = u_donor.id
                LEFT JOIN users u_author ON ap.author_id = u_author.id
                WHERE ap.nft_token_id = %s
            """
            cursor.execute(query, (token_id,))
            result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NFT not found"
            )
        
        return NFTDetailsResponse(
            token_id=int(token_id.replace('-', '')[:8], 16),
            contract_address=result[5],  # contract_address column
            owner=result[-2] or "Anonymous",  # donor_address
            donation_amount=float(result[7]),  # amount column
            recipient=result[-1],  # author_address
            article_id=str(result[2]),  # article_id column
            token_uri=result[15],  # token_uri column
            metadata=eval(result[16]) if result[16] else {}  # metadata column
        )
        
    except Exception as e:
        logger.error(f"Error getting NFT details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get NFT details"
        )


@router.get("/payments", response_model=List[AuthorPaymentResponse])
async def get_user_payments(
    current_user=Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[str] = None
):
    """
    Get payments for the current user (either as author or donor)
    """
    try:
        where_conditions = ["(author_id = %s OR donor_id = %s)"]
        params = [current_user['id'], current_user['id']]
        
        if status_filter:
            where_conditions.append("payment_status = %s")
            params.append(status_filter)
        
        params.extend([limit, offset])
        
        with get_postgres_cursor() as cursor:
            query = f"""
                SELECT * FROM author_payments
                WHERE {' AND '.join(where_conditions)}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params)
            results = cursor.fetchall()
        
        # Convert results to response models (simplified)
        return []  # Return empty list for now, would need full conversion
        
    except Exception as e:
        logger.error(f"Error getting user payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user payments"
        )


@router.post("/admin/verify-author", response_model=BaseResponse)
async def verify_author(
    request: VerifyAuthorRequest,
    current_user=Depends(get_current_user)
):
    """
    Verify an author for NFT donations (admin only)
    """
    if current_user['role'] != 'administrator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can verify authors"
        )
    
    try:
        # Update user's DID address
        with get_postgres_cursor() as cursor:
            query = """
                UPDATE users 
                SET did_address = %s, verification_status = true
                WHERE id = (SELECT id FROM users WHERE did_address = %s OR email = %s)
                RETURNING id
            """
            cursor.execute(query, (request.author_address, request.author_address, request.author_address))
            result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        
        return BaseResponse(message="Author verified successfully")
        
    except Exception as e:
        logger.error(f"Error verifying author: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify author"
        )


async def process_blockchain_donation(
    payment_id: uuid.UUID,
    amount: float,
    author_address: str,
    donor_address: str,
    article_id: str
):
    """
    Background task to process the actual blockchain transaction
    This would integrate with Web3.py or similar to interact with smart contracts
    """
    try:
        # Mock blockchain processing
        # In reality, this would:
        # 1. Connect to blockchain
        # 2. Call DonationManager.processDonation()
        # 3. Wait for transaction confirmation
        # 4. Update payment status
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(5)
        
        # Update payment status to confirmed
        with get_postgres_cursor() as cursor:
            cursor.execute(
                """
                UPDATE author_payments 
                SET payment_status = 'confirmed', confirmed_at = %s, processed_at = %s
                WHERE id = %s
                """,
                (datetime.now(), datetime.now(), str(payment_id))
            )
            
        logger.info(f"Donation {payment_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process donation {payment_id}: {str(e)}")
        
        # Update payment status to failed
        with get_postgres_cursor() as cursor:
            cursor.execute(
                """
                UPDATE author_payments 
                SET payment_status = 'failed'
                WHERE id = %s
                """,
                (str(payment_id),)
            )