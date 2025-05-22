'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Heart, Gift, Coins, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface DonationDialogProps {
  articleId: string
  articleTitle: string
  authorName: string
  authorAddress?: string
  onDonationComplete?: (tokenId: string, transactionHash: string) => void
}

interface DonationFormData {
  amount: string
  message: string
  anonymous: boolean
}

export function DonationDialog({
  articleId,
  articleTitle,
  authorName,
  authorAddress,
  onDonationComplete
}: DonationDialogProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [formData, setFormData] = useState<DonationFormData>({
    amount: '',
    message: '',
    anonymous: false
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const { toast } = useToast()

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = 'Please enter a valid donation amount'
    } else if (parseFloat(formData.amount) < 0.001) {
      newErrors.amount = 'Minimum donation is 0.001 ETH'
    } else if (parseFloat(formData.amount) > 10) {
      newErrors.amount = 'Maximum donation is 10 ETH'
    }

    if (formData.message && formData.message.length > 500) {
      newErrors.message = 'Message cannot exceed 500 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return

    setIsProcessing(true)
    
    try {
      const response = await fetch('/api/v1/donations/donate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          article_id: articleId,
          amount: parseFloat(formData.amount),
          message: formData.message || null,
          anonymous: formData.anonymous,
          token_uri: `${window.location.origin}/nft-metadata/${articleId}`
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to process donation')
      }

      const result = await response.json()
      
      toast({
        title: 'Donation Successful! 🎉',
        description: `Your donation of ${formData.amount} ETH is being processed. You'll receive your FTK NFT shortly.`,
      })

      if (onDonationComplete) {
        onDonationComplete(result.token_id, result.transaction_hash)
      }

      setIsOpen(false)
      setFormData({ amount: '', message: '', anonymous: false })
      
    } catch (error) {
      console.error('Donation error:', error)
      toast({
        title: 'Donation Failed',
        description: error instanceof Error ? error.message : 'An unexpected error occurred',
        variant: 'destructive'
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const calculateFees = (amount: number) => {
    const platformFee = amount * 0.025 // 2.5%
    const netAmount = amount - platformFee
    return { platformFee, netAmount }
  }

  const donationAmount = parseFloat(formData.amount) || 0
  const { platformFee, netAmount } = calculateFees(donationAmount)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Heart className="w-4 h-4" />
          Donate FTK
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Gift className="w-5 h-5" />
            Support with FuseToken NFT
          </DialogTitle>
          <DialogDescription>
            Send a donation to <strong>{authorName}</strong> for "{articleTitle}" and receive a unique FTK NFT as proof of your support.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Author Info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Donation Recipient</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{authorName}</p>
                  {authorAddress && (
                    <p className="text-xs text-muted-foreground font-mono">
                      {authorAddress.slice(0, 6)}...{authorAddress.slice(-4)}
                    </p>
                  )}
                </div>
                {authorAddress ? (
                  <Badge variant="secondary" className="gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Verified
                  </Badge>
                ) : (
                  <Badge variant="outline" className="gap-1">
                    <AlertCircle className="w-3 h-3" />
                    Unverified
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Donation Amount */}
          <div className="grid gap-2">
            <Label htmlFor="amount">Donation Amount (ETH)</Label>
            <div className="relative">
              <Coins className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                id="amount"
                type="number"
                step="0.001"
                min="0.001"
                max="10"
                placeholder="0.001"
                value={formData.amount}
                onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
                className="pl-10"
              />
            </div>
            {errors.amount && (
              <p className="text-sm text-destructive">{errors.amount}</p>
            )}
          </div>

          {/* Fee Breakdown */}
          {donationAmount > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Transaction Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Donation Amount:</span>
                  <span>{donationAmount.toFixed(4)} ETH</span>
                </div>
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>Platform Fee (2.5%):</span>
                  <span>-{platformFee.toFixed(4)} ETH</span>
                </div>
                <div className="flex justify-between font-medium border-t pt-2">
                  <span>Author Receives:</span>
                  <span>{netAmount.toFixed(4)} ETH</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Message */}
          <div className="grid gap-2">
            <Label htmlFor="message">Message (Optional)</Label>
            <Textarea
              id="message"
              placeholder="Leave a message for the author..."
              value={formData.message}
              onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
              className="resize-none"
              rows={3}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{formData.message.length}/500 characters</span>
              {errors.message && (
                <span className="text-destructive">{errors.message}</span>
              )}
            </div>
          </div>

          {/* Anonymous Option */}
          <div className="flex items-center space-x-2">
            <Switch
              id="anonymous"
              checked={formData.anonymous}
              onCheckedChange={(checked) => setFormData(prev => ({ ...prev, anonymous: checked }))}
            />
            <Label htmlFor="anonymous" className="text-sm">
              Donate anonymously
            </Label>
          </div>

          {/* NFT Info */}
          <Alert>
            <Gift className="w-4 h-4" />
            <AlertDescription>
              You'll receive a unique FuseToken (FTK) NFT as proof of your donation. 
              This NFT contains metadata about your contribution and can be viewed in your wallet.
            </AlertDescription>
          </Alert>

          {/* Author Verification Warning */}
          {!authorAddress && (
            <Alert variant="destructive">
              <AlertCircle className="w-4 h-4" />
              <AlertDescription>
                This author hasn't set up their wallet address for receiving donations yet. 
                Donations are currently unavailable.
              </AlertDescription>
            </Alert>
          )}

          {/* Processing Status */}
          {isProcessing && (
            <Alert>
              <Clock className="w-4 h-4" />
              <AlertDescription>
                Processing your donation on the blockchain. This may take a few moments...
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button 
            type="button" 
            variant="outline" 
            onClick={() => setIsOpen(false)}
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button 
            type="button" 
            onClick={handleSubmit}
            disabled={isProcessing || !formData.amount || parseFloat(formData.amount) <= 0 || !authorAddress}
            className="gap-2"
          >
            {isProcessing ? (
              <>
                <Clock className="w-4 h-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Heart className="w-4 h-4" />
                Donate {formData.amount || '0'} ETH
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}