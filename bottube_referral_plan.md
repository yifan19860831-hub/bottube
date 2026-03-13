# 🎯 BoTTube Referral Program - Implementation Plan

## 📊 Overview

**Issue**: [#55](https://github.com/Scottcjn/bottube/issues/55)  
**Bounty Pool**: 500 RTC (~$50 USD)  
**My Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Target Earnings**: 120 RTC (max cap: 10 referrals × 12 RTC)

---

## 🎁 Dual-Sided Reward Structure

| Action | Referrer Earns | New User Earns |
|--------|----------------|----------------|
| New user signs up + creates bot | 5 RTC | 3 RTC |
| New user uploads 5 videos | +7 RTC | +5 RTC |
| **Total per successful referral** | **12 RTC** | **8 RTC** |

### Maximum Earnings Per Person
- **Referrer Cap**: 10 referrals × 12 RTC = **120 RTC**
- **New User Bonus**: 8 RTC per referral (no cap mentioned)

---

## 🛡️ Anti-Gaming Rules

1. ✅ New user must have unique IP/device fingerprint
2. ✅ New user must create real content (not spam/bot uploads)
3. ✅ Self-referrals strictly prohibited
4. ✅ Maximum 10 referrals per person (120 RTC cap)
5. ✅ Fraud detection: suspicious patterns flagged for review

---

## 🔗 How It Works

### For Referrers (Existing Users)
1. Get your unique referral link from BoTTube profile dashboard
2. Share link on social media, Discord, forums, YouTube, etc.
3. Track referrals in your dashboard
4. Earn RTC automatically when milestones are hit

### For New Users (Referees)
1. Sign up using referral link
2. Create your first AI bot (required for initial bonus)
3. Upload 5 videos to unlock remaining bonus
4. Both you and referrer get rewarded

---

## 📋 Implementation Checklist

### Phase 1: System Design ✅
- [x] Review issue #55 requirements
- [x] Design reward structure
- [x] Define anti-gaming rules
- [ ] Create technical specification

### Phase 2: Technical Implementation
- [ ] Database schema for referrals
- [ ] API endpoints for referral tracking
- [ ] Dashboard UI for users
- [ ] Automated reward distribution
- [ ] Fraud detection system

### Phase 3: Documentation
- [ ] User guide for referrers
- [ ] FAQ page
- [ ] Terms and conditions
- [ ] Marketing materials

### Phase 4: Launch & Promotion
- [ ] Announce on social media
- [ ] Discord/Telegram community posts
- [ ] Blog post explaining program
- [ ] Track initial results

---

## 📊 Referral Tracking System

### Database Schema Design

```sql
-- Referrals table
CREATE TABLE referrals (
  id UUID PRIMARY KEY,
  referrer_user_id UUID NOT NULL,
  referee_user_id UUID NOT NULL,
  referral_code VARCHAR(32) UNIQUE NOT NULL,
  signup_timestamp TIMESTAMP,
  bot_created BOOLEAN DEFAULT FALSE,
  bot_created_timestamp TIMESTAMP,
  videos_uploaded INTEGER DEFAULT 0,
  five_videos_milestone BOOLEAN DEFAULT FALSE,
  referrer_reward_claimed BOOLEAN DEFAULT FALSE,
  referee_reward_claimed BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) DEFAULT 'pending', -- pending, active, completed, flagged
  ip_address VARCHAR(45),
  device_fingerprint VARCHAR(64),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Referral rewards ledger
CREATE TABLE referral_rewards (
  id UUID PRIMARY KEY,
  referral_id UUID NOT NULL,
  recipient_user_id UUID NOT NULL,
  reward_type VARCHAR(32) NOT NULL, -- signup_bonus, video_milestone
  amount INTEGER NOT NULL,
  transaction_hash VARCHAR(128),
  claimed_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'pending' -- pending, processing, completed, failed
);
```

### API Endpoints

```
GET  /api/referral/my-link          - Get user's referral link
GET  /api/referral/stats            - Get referral statistics
GET  /api/referral/list             - List all referrals
POST /api/referral/claim            - Claim earned rewards
GET  /api/referral/validate/:code   - Validate referral code
```

---

## 📈 Marketing Strategy

### Target Channels
1. **Twitter/X** - Crypto and AI creator communities
2. **Discord** - AI art, video creation, crypto servers
3. **Reddit** - r/artificial, r/CryptoCurrency, r/sidehustle
4. **YouTube** - AI tutorial creators
5. **Telegram** - Crypto and AI groups

### Messaging
- "Earn 12 RTC for every creator you invite to BoTTube!"
- "New users get 8 RTC bonus when they start creating"
- "Maximum 10 referrals = 120 RTC (~$12 USD)"
- "Both sides win - dual-sided rewards"

---

## 🏆 My Referral Goal

| Metric | Target |
|--------|--------|
| Referrals | 10 (max allowed) |
| Earnings per referral | 12 RTC |
| **Total Target** | **120 RTC (~$12 USD)** |
| Timeline | 4 weeks |

### Action Plan
1. Share referral link in 5+ Discord servers
2. Create Twitter thread about BoTTube
3. Post in 3+ Reddit communities
4. Message 10+ creator friends directly
5. Track conversions weekly

---

## 📝 Files to Create

1. `referral_program_spec.md` - Technical specification
2. `referral_tracker.md` - Personal referral tracking
3. `referral_marketing_templates.md` - Copy-paste promotional content
4. GitHub PR with implementation plan
5. GitHub comment on issue #55 with wallet address

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Issue #55 | https://github.com/Scottcjn/bottube/issues/55 |
| BoTTube Platform | https://bottube.ai |
| API Docs | https://bottube.ai/join |

---

**Created**: 2026-03-13  
**Status**: Planning Phase  
**Next**: Create technical spec and tracking system
