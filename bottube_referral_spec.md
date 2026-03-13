# 🛠️ BoTTube Referral Program - Technical Specification

## 📋 Overview

This document defines the technical implementation for the BoTTube Referral Program (Issue #55).

**Bounty Pool**: 500 RTC  
**Program Type**: Dual-sided referral rewards  
**Target Launch**: 2 weeks from approval

---

## 🎯 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Users can generate unique referral codes | P0 |
| FR-2 | System tracks referral signups | P0 |
| FR-3 | System tracks bot creation milestone | P0 |
| FR-4 | System tracks 5-video upload milestone | P0 |
| FR-5 | Automatic reward distribution on milestones | P0 |
| FR-6 | Dashboard showing referral stats | P1 |
| FR-7 | Fraud detection (IP/device fingerprinting) | P1 |
| FR-8 | Admin panel for manual review | P2 |
| FR-9 | Email notifications for milestones | P2 |
| FR-10 | Export referral data (CSV) | P3 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | API response time | < 200ms |
| NFR-2 | Fraud detection accuracy | > 95% |
| NFR-3 | System uptime | 99.9% |
| NFR-4 | Data retention | 2 years minimum |

---

## 🗄️ Database Schema

### Table: `referral_codes`

```sql
CREATE TABLE referral_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  code VARCHAR(32) UNIQUE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE,
  
  INDEX idx_code (code),
  INDEX idx_user_id (user_id)
);
```

### Table: `referrals`

```sql
CREATE TABLE referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_user_id UUID NOT NULL REFERENCES users(id),
  referee_user_id UUID NOT NULL REFERENCES users(id),
  referral_code_id UUID NOT NULL REFERENCES referral_codes(id),
  
  -- Milestones
  signup_completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  bot_created_at TIMESTAMP WITH TIME ZONE,
  videos_uploaded_count INTEGER DEFAULT 0,
  five_videos_completed_at TIMESTAMP WITH TIME ZONE,
  
  -- Rewards
  referrer_signup_reward INTEGER DEFAULT 5, -- RTC
  referrer_video_reward INTEGER DEFAULT 7, -- RTC
  referee_signup_reward INTEGER DEFAULT 3, -- RTC
  referee_video_reward INTEGER DEFAULT 5, -- RTC
  
  referrer_signup_claimed BOOLEAN DEFAULT FALSE,
  referrer_video_claimed BOOLEAN DEFAULT FALSE,
  referee_signup_claimed BOOLEAN DEFAULT FALSE,
  referee_video_claimed BOOLEAN DEFAULT FALSE,
  
  -- Anti-fraud
  signup_ip_address INET,
  signup_device_fingerprint VARCHAR(64),
  referral_score INTEGER DEFAULT 100, -- Fraud score (100 = clean)
  
  -- Status
  status VARCHAR(20) DEFAULT 'active', -- active, completed, flagged, banned
  flagged_reason TEXT,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT unique_referee UNIQUE (referee_user_id),
  CONSTRAINT unique_referral_pair UNIQUE (referrer_user_id, referee_user_id),
  
  INDEX idx_referrer (referrer_user_id),
  INDEX idx_referee (referee_user_id),
  INDEX idx_status (status)
);
```

### Table: `referral_rewards_ledger`

```sql
CREATE TABLE referral_rewards_ledger (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referral_id UUID NOT NULL REFERENCES referrals(id),
  recipient_user_id UUID NOT NULL REFERENCES users(id),
  reward_type VARCHAR(32) NOT NULL, -- signup_bonus, video_milestone
  amount INTEGER NOT NULL,
  currency VARCHAR(10) DEFAULT 'RTC',
  
  transaction_id UUID,
  transaction_hash VARCHAR(128),
  blockchain_tx_hash VARCHAR(256),
  
  status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
  failure_reason TEXT,
  
  claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed_at TIMESTAMP WITH TIME ZONE,
  
  INDEX idx_referral (referral_id),
  INDEX idx_user (recipient_user_id),
  INDEX idx_status (status)
);
```

### Table: `referral_fraud_checks`

```sql
CREATE TABLE referral_fraud_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referral_id UUID NOT NULL REFERENCES referrals(id),
  check_type VARCHAR(32) NOT NULL, -- ip_match, device_match, self_referral, spam_pattern
  check_result BOOLEAN NOT NULL, -- TRUE = passed, FALSE = failed
  details JSONB,
  checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  INDEX idx_referral (referral_id),
  INDEX idx_check_type (check_type)
);
```

---

## 🔌 API Endpoints

### GET `/api/v1/referral/my-link`

Get user's personal referral link.

**Response**:
```json
{
  "success": true,
  "data": {
    "referralCode": "abc123xyz",
    "referralLink": "https://bottube.ai/join?ref=abc123xyz",
    "shortLink": "https://bottube.ai/r/abc123xyz",
    "isActive": true,
    "createdAt": "2026-03-13T10:00:00Z"
  }
}
```

### GET `/api/v1/referral/stats`

Get referral statistics for current user.

**Response**:
```json
{
  "success": true,
  "data": {
    "totalReferrals": 5,
    "activeReferrals": 3,
    "completedReferrals": 2,
    "flaggedReferrals": 0,
    "totalEarned": 36,
    "pendingEarnings": 24,
    "referralCap": 10,
    "remainingSlots": 5,
    "breakdown": {
      "signupBonuses": 3,
      "videoMilestones": 2
    }
  }
}
```

### GET `/api/v1/referral/list`

List all referrals with pagination.

**Query Parameters**:
- `page` (default: 1)
- `limit` (default: 20, max: 100)
- `status` (optional: active, completed, flagged)

**Response**:
```json
{
  "success": true,
  "data": {
    "referrals": [
      {
        "id": "uuid",
        "refereeUsername": "creator123",
        "signupDate": "2026-03-10T08:30:00Z",
        "botCreated": true,
        "botCreatedAt": "2026-03-11T14:20:00Z",
        "videosUploaded": 7,
        "status": "completed",
        "earnings": {
          "signup": {"amount": 5, "claimed": true},
          "videos": {"amount": 7, "claimed": true}
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "totalPages": 1
    }
  }
}
```

### POST `/api/v1/referral/validate`

Validate a referral code during signup.

**Request**:
```json
{
  "referralCode": "abc123xyz"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "isValid": true,
    "referrerUsername": "topcreator",
    "referrerBonus": 12,
    "refereeBonus": 8
  }
}
```

### POST `/api/v1/referral/claim`

Claim earned referral rewards.

**Request**:
```json
{
  "referralId": "uuid",
  "rewardType": "signup_bonus" // or "video_milestone"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "rewardId": "uuid",
    "amount": 5,
    "currency": "RTC",
    "transactionHash": "0x...",
    "status": "completed"
  }
}
```

### POST `/api/v1/referral/webhook` (Internal)

Webhook for milestone tracking (bot creation, video uploads).

**Request**:
```json
{
  "userId": "uuid",
  "milestoneType": "bot_created", // or "video_uploaded"
  "metadata": {}
}
```

---

## 🛡️ Fraud Detection System

### Detection Rules

| Rule | Description | Action |
|------|-------------|--------|
| IP Match | Same IP as referrer | Flag for review |
| Device Fingerprint | Same device hash | Auto-reject |
| Self-Referral | Same user ID | Auto-reject + ban |
| Rapid Signups | >5 signups/hour from same IP | Temporary hold |
| Bot Pattern | No activity after signup | Flag after 7 days |
| Spam Content | Uploaded videos are spam | Manual review |

### Fraud Score Calculation

```python
def calculate_fraud_score(referral):
    score = 100  # Base score (clean)
    
    # IP check
    if referral.ip matches referrer.ip:
        score -= 30
    
    # Device check
    if referral.device == referrer.device:
        score -= 50
    
    # Time pattern
    if signup time is suspicious (e.g., 3am local):
        score -= 10
    
    # Activity pattern
    if no activity after 7 days:
        score -= 20
    
    # Content quality
    if videos are low quality/spam:
        score -= 40
    
    return max(0, score)

# Thresholds
# score >= 70: Auto-approve
# score 40-69: Flag for review
# score < 40: Auto-reject
```

---

## 🎨 Frontend Components

### Dashboard UI

```
┌─────────────────────────────────────────────┐
│  🎯 My Referrals                            │
├─────────────────────────────────────────────┤
│                                             │
│  Total Earned: 36 RTC                       │
│  Pending: 24 RTC                            │
│  Progress: ████████░░ 5/10 referrals        │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Your Referral Link                  │   │
│  │ https://bottube.ai/r/abc123xyz      │   │
│  │ [Copy] [Share]                      │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Recent Referrals:                          │
│  ┌─────────────────────────────────────┐   │
│  │ @creator123  ✅✅  12 RTC earned    │   │
│  │ @newuser456  ✅⏳  5 RTC pending    │   │
│  │ @artist789   ⏳⏳  0 RTC pending     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [View All Referrals] [Download Report]     │
└─────────────────────────────────────────────┘
```

### Referral Card Component

```typescript
interface ReferralCardProps {
  referee: User;
  signupDate: Date;
  botCreated: boolean;
  videosUploaded: number;
  status: 'active' | 'completed' | 'flagged';
  earnings: {
    signup: { amount: number; claimed: boolean };
    videos: { amount: number; claimed: boolean };
  };
}
```

---

## 📊 Analytics & Reporting

### Metrics to Track

1. **Conversion Funnel**
   - Link clicks → Signups
   - Signups → Bot created
   - Bot created → 5 videos uploaded

2. **Referral Quality**
   - Average videos per referral
   - Retention rate (30-day active)
   - Fraud flag rate

3. **Earnings Distribution**
   - Total RTC distributed
   - Average per referrer
   - Top referrers leaderboard

### Admin Dashboard

```
┌─────────────────────────────────────────────┐
│  📊 Referral Program Analytics              │
├─────────────────────────────────────────────┤
│                                             │
│  Total Participants: 1,234                  │
│  Total RTC Distributed: 8,456               │
│  Fraud Rate: 2.3%                           │
│                                             │
│  Top Referrers:                             │
│  1. @topcreator - 47 referrals (564 RTC)    │
│  2. @influencer - 38 referrals (456 RTC)    │
│  3. @community - 29 referrals (348 RTC)     │
│                                             │
│  [Export Data] [Flagged Reviews] [Settings] │
└─────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

1. **Rate Limiting**
   - Max 100 API calls/hour per user
   - Max 10 referral code generations/day

2. **Data Protection**
   - Encrypt IP addresses at rest
   - Hash device fingerprints
   - GDPR-compliant data retention

3. **Access Control**
   - Users can only see their own referrals
   - Admin role required for fraud review
   - Audit log for all manual actions

---

## 🚀 Deployment Plan

### Phase 1: Backend (Week 1)
- [ ] Database migrations
- [ ] API endpoints implementation
- [ ] Fraud detection logic
- [ ] Reward distribution system

### Phase 2: Frontend (Week 1-2)
- [ ] Referral dashboard UI
- [ ] Referral card components
- [ ] Share functionality
- [ ] Stats visualization

### Phase 3: Testing (Week 2)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Fraud detection testing
- [ ] Load testing

### Phase 4: Launch (Week 2)
- [ ] Staging deployment
- [ ] QA verification
- [ ] Production deployment
- [ ] Monitoring setup

---

## 📝 Open Questions

1. Should there be a time limit for milestones? (e.g., 5 videos within 30 days)
2. What happens if a referral is flagged after rewards are distributed?
3. Should referrers be notified when referrals hit milestones?
4. Is there a minimum withdrawal amount for RTC?

---

## 🔗 Related Documents

- [Referral Plan](./bottube_referral_plan.md)
- [Referral Tracker](./bottube_referral_tracker.md)
- [Marketing Templates](./bottube_referral_marketing.md)
- [Issue #55](https://github.com/Scottcjn/bottube/issues/55)

---

**Author**: Subagent for Issue #55  
**Created**: 2026-03-13  
**Version**: 1.0  
**Status**: Draft - Ready for Review
