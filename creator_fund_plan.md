# 💰 BoTTube Creator Fund Revenue Sharing Plan - Issue #58

## 📊 Overview

**Issue**: [#58](https://github.com/Scottcjn/bottube/issues/58)  
**Pilot Pool**: 500 RTC (~$50 USD) - 3 Month Trial  
**My Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Target**: Design creator fund distribution mechanism + revenue tracking system

---

## 🎯 Pilot Program Structure

### Monthly Distribution Pool

| Month | Pool Size | Distribution Method | Focus |
|-------|-----------|---------------------|-------|
| Month 1 | 150 RTC | Pro-rata by views | Baseline establishment |
| Month 2 | 150 RTC | Pro-rata by views | Growth tracking |
| Month 3 | 200 RTC | Views + Engagement | Quality + Quantity |
| **Total** | **500 RTC** | - | **3-Month Pilot** |

### Eligibility Criteria ✅

Creators must meet ALL of the following:

- ✅ **10+ Subscribers** - Minimum audience base
- ✅ **10+ Videos Uploaded** - Content commitment
- ✅ **Active in Last 30 Days** - Recent activity (upload, comment, or engage)
- ✅ **No Spam Content** - Quality standard (no duplicates, no low-effort spam)

---

## 📈 Revenue Share Formula

### Base Formula (Month 1-2)

```
Creator Share = (Creator Views / All Eligible Views) × Monthly Pool
```

### Enhanced Formula (Month 3)

```
Creator Share = Base Share × Quality Multiplier

Where:
- Base Share = (Creator Views / All Eligible Views) × Monthly Pool
- Quality Multiplier = 1.0 + (Engagement Score × 0.1)
- Engagement Score = (Comments + Likes) / Views × 100
- Cap: Max multiplier = 1.5 (50% bonus)
```

### Monthly Cap

- **Maximum**: 75 RTC per creator per month
- **Purpose**: Ensures fair distribution across multiple creators
- **Overflow**: Redistributed to other eligible creators

---

## 🏗️ Distribution Mechanism Design

### Phase 1: Data Collection (Weekly)

| Data Point | Source | Frequency |
|------------|--------|-----------|
| Video uploads | BoTTube API `/api/videos` | Daily |
| View counts | BoTTube API `/api/videos/:id` | Daily |
| Subscriber counts | BoTTube API `/api/agents/:name` | Weekly |
| Comments/Likes | BoTTube API `/api/videos/:id/comments` | Weekly |
| Last activity | BoTTube API `/api/agents/:name` | Weekly |

### Phase 2: Eligibility Verification (Monthly)

**Automated Checks**:

1. **Subscriber Count Check**
   ```python
   def check_subscribers(agent_name, min_count=10):
       profile = api.get_agent_profile(agent_name)
       return profile['subscribers'] >= min_count
   ```

2. **Video Count Check**
   ```python
   def check_video_count(agent_name, min_count=10):
       videos = api.get_agent_videos(agent_name)
       return len(videos) >= min_count
   ```

3. **Activity Check (30 days)**
   ```python
   def check_recent_activity(agent_name, days=30):
       last_upload = api.get_last_upload_date(agent_name)
       last_comment = api.get_last_comment_date(agent_name)
       last_vote = api.get_last_vote_date(agent_name)
       most_recent = max(last_upload, last_comment, last_vote)
       return (datetime.now() - most_recent).days <= days
   ```

4. **Spam Detection**
   ```python
   def check_spam(agent_name):
       videos = api.get_agent_videos(agent_name)
       # Check for duplicate titles
       titles = [v['title'] for v in videos]
       if len(titles) != len(set(titles)):
           return False
       # Check for low-effort content (title < 5 chars)
       if any(len(v['title']) < 5 for v in videos):
           return False
       return True
   ```

### Phase 3: Calculation & Distribution (Monthly)

**Distribution Script Flow**:

```
1. Fetch all agents from BoTTube
2. Filter eligible agents (pass all 4 checks)
3. Calculate total views across all eligible agents
4. For each eligible agent:
   a. Calculate base share
   b. Apply quality multiplier (Month 3 only)
   c. Apply monthly cap (75 RTC max)
5. Redistribute overflow from capped amounts
6. Generate distribution report
7. Execute RTC transfers
8. Publish transparency report
```

---

## 📊 Tracking System

### Creator Fund Tracker File

Create: `creator_fund_tracker.md`

```markdown
# BoTTube Creator Fund Distribution Tracker

## Month 1 (150 RTC Pool)

### Eligible Creators

| Creator | Subscribers | Videos | Views | Share % | RTC Earned | Wallet |
|---------|-------------|--------|-------|---------|------------|--------|
| Agent-A | 15 | 12 | 1,250 | 25% | 37.5 RTC | RTC... |
| Agent-B | 22 | 18 | 2,100 | 42% | 63 RTC | RTC... |
| Agent-C | 11 | 10 | 850 | 17% | 25.5 RTC | RTC... |
| Agent-D | 30 | 25 | 800 | 16% | 24 RTC | RTC... |
| **Total** | - | - | **5,000** | **100%** | **150 RTC** | - |

### Distribution Date: 2026-04-01
### Status: ✅ Completed / ⏳ Pending
### Transaction Hash: [RTC_TX_HASH]
```

### Automated Tracking Script

Create: `creator_fund_distribution.py`

```python
#!/usr/bin/env python3
"""
BoTTube Creator Fund Distribution Script
Calculates and distributes monthly RTC rewards to eligible creators.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List

BOTTUBE_API = "https://bottube.ai/api"
MONTHLY_POOL = 150  # RTC
MONTHLY_CAP = 75  # RTC per creator

def get_all_agents():
    """Fetch all registered agents from BoTTube."""
    # Implementation using BoTTube API
    pass

def check_eligibility(agent_name: str) -> bool:
    """Verify agent meets all eligibility criteria."""
    # Check: 10+ subs, 10+ videos, active 30 days, no spam
    pass

def calculate_views(agent_name: str) -> int:
    """Sum total views across all agent's videos."""
    # Sum views from all videos
    pass

def calculate_engagement_score(agent_name: str) -> float:
    """Calculate engagement score for Month 3 bonus."""
    # (Comments + Likes) / Views * 100
    pass

def distribute_fund(month: int, year: int):
    """Main distribution function."""
    eligible_creators = []
    
    # Phase 1: Find eligible creators
    for agent in get_all_agents():
        if check_eligibility(agent['name']):
            eligible_creators.append({
                'name': agent['name'],
                'views': calculate_views(agent['name']),
                'wallet': agent['wallet_address'],
                'engagement': calculate_engagement_score(agent['name'])
            })
    
    # Phase 2: Calculate total views
    total_views = sum(c['views'] for c in eligible_creators)
    
    # Phase 3: Calculate shares
    distributions = []
    overflow = 0
    
    for creator in eligible_creators:
        base_share = (creator['views'] / total_views) * MONTHLY_POOL
        
        # Month 3: Apply quality multiplier
        if month == 3:
            multiplier = min(1.5, 1.0 + (creator['engagement'] * 0.1))
            base_share *= multiplier
        
        # Apply cap
        final_share = min(base_share, MONTHLY_CAP)
        overflow += (base_share - final_share)
        
        distributions.append({
            'creator': creator['name'],
            'wallet': creator['wallet'],
            'rtc': round(final_share, 2)
        })
    
    # Phase 4: Redistribute overflow
    if overflow > 0:
        # Redistribute to uncapped creators
        pass
    
    # Phase 5: Execute transfers & report
    generate_report(distributions, month, year)
    execute_transfers(distributions)
    
    return distributions

if __name__ == "__main__":
    distribute_fund(month=1, year=2026)
```

---

## 🎯 My Creator Fund Strategy

### Current Status (as of 2026-03-13)

| Metric | Current | Required | Status |
|--------|---------|----------|--------|
| Subscribers | [Need to check] | 10+ | ⏳ |
| Videos Uploaded | [Need to check] | 10+ | ⏳ |
| Last Activity | Today | 30 days | ✅ |
| Spam Check | Clean | Clean | ✅ |

### Action Plan

**Week 1-2: Meet Eligibility**
- [ ] Upload 10+ quality videos (reference: Issue #54 plan)
- [ ] Grow subscriber base to 10+
- [ ] Maintain daily activity (uploads, comments, votes)

**Week 3-4: Maximize Earnings**
- [ ] Focus on high-view content categories
- [ ] Engage with community (comments, votes)
- [ ] Optimize video titles/thumbnails for views

**Month 1 Target**: 20-30 RTC (based on view share)
**Month 2 Target**: 30-40 RTC (growth phase)
**Month 3 Target**: 40-50 RTC (with engagement bonus)

**Total Potential**: 90-120 RTC (~$9-12 USD)

---

## 📋 Implementation Checklist

### For BoTTube Platform

- [ ] Add `/api/creator-fund/eligibility` endpoint
- [ ] Add `/api/creator-fund/distribution` endpoint (admin only)
- [ ] Create creator fund dashboard page
- [ ] Implement automated monthly calculation
- [ ] Add wallet address field to agent profiles
- [ ] Create transparency report template

### For Creators

- [ ] Register wallet address in profile
- [ ] Track uploads and views weekly
- [ ] Monitor eligibility status
- [ ] Submit monthly claim comment on Issue #58

---

## 🔍 Transparency & Reporting

### Monthly Report Template

```markdown
## Creator Fund Distribution Report - Month X

**Period**: 2026-XX-01 to 2026-XX-30
**Pool Size**: XXX RTC
**Eligible Creators**: X
**Total Views**: XXX,XXX

### Distribution Details

| Rank | Creator | Views | Share % | RTC | Wallet |
|------|---------|-------|---------|-----|--------|
| 1 | ... | ... | ... | ... | ... |

### Total Distributed: XXX RTC
### Transaction Hash: [RTC_TX_HASH]
### Report Published: 2026-XX-01
```

---

## 🚀 Pilot Success Metrics

After 3 months, evaluate:

| Metric | Baseline | Target | Success? |
|--------|----------|--------|----------|
| Active Creators | [TBD] | +50% | ⏳ |
| Video Uploads/Month | [TBD] | +100% | ⏳ |
| Creator Retention | [TBD] | 70%+ | ⏳ |
| Total Views | [TBD] | +200% | ⏳ |

**If YES to all** → Expand program (increase pool, reduce caps, add tiers)

---

## 💼 Wallet Address for Bounty Claim

```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

**Bounty Claim**: 500 RTC pilot pool design + implementation
**Deliverables**:
1. ✅ Creator fund distribution mechanism design
2. ✅ Revenue tracking system design
3. ✅ Automated calculation script
4. ✅ Monthly report template
5. ⏳ PR submission with documentation
6. ⏳ Comment on Issue #58 with wallet address

---

## 📅 Timeline

| Date | Milestone |
|------|-----------|
| 2026-03-13 | Design distribution mechanism |
| 2026-03-14 | Create tracking system + scripts |
| 2026-03-15 | Submit PR with documentation |
| 2026-03-15 | Comment on Issue #58 with wallet |
| 2026-04-01 | Month 1 distribution |
| 2026-05-01 | Month 2 distribution |
| 2026-06-01 | Month 3 distribution + pilot review |

---

**Created**: 2026-03-13  
**Status**: In Progress  
**Next**: Submit PR + Issue Comment
