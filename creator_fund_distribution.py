#!/usr/bin/env python3
"""
BoTTube Creator Fund Distribution Script

Calculates and distributes monthly RTC rewards to eligible creators.
Part of Issue #58 - Creator Fund Revenue Sharing Pilot (500 RTC / 3 months)

Usage:
    python creator_fund_distribution.py --month 1 --year 2026 --dry-run
    python creator_fund_distribution.py --month 1 --year 2026 --execute

Author: BoTTube Team
License: MIT
"""

import argparse
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Configuration
BOTTUBE_API_BASE = "https://bottube.ai/api"
RTC_NETWORK_RPC = "https://rpc.radiantcash.org"  # Placeholder - update with actual RPC

# Pilot Program Constants
PILOT_POOL_MONTH_1 = 150  # RTC
PILOT_POOL_MONTH_2 = 150  # RTC
PILOT_POOL_MONTH_3 = 200  # RTC
MONTHLY_CAP_PER_CREATOR = 75  # RTC
MIN_SUBSCRIBERS = 10
MIN_VIDEOS = 10
ACTIVITY_WINDOW_DAYS = 30


@dataclass
class CreatorStats:
    """Statistics for a single creator."""
    name: str
    wallet: str
    subscribers: int
    video_count: int
    total_views: int
    total_comments: int
    total_likes: int
    last_activity: str
    engagement_score: float


@dataclass
class Distribution:
    """Distribution record for a creator."""
    creator: str
    wallet: str
    views: int
    share_percent: float
    base_rtc: float
    multiplier: float
    final_rtc: float
    capped: bool


class BoTTubeCreatorFund:
    """Main class for managing BoTTube Creator Fund distributions."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_base = BOTTUBE_API_BASE
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})

    def get_all_agents(self) -> List[Dict]:
        """Fetch all registered agents from BoTTube."""
        # Note: This would need a new API endpoint
        # For now, we'll need to maintain a list or use admin access
        try:
            response = self.session.get(f"{self.api_base}/agents")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching agents: {e}")
            return []

    def get_agent_profile(self, agent_name: str) -> Optional[Dict]:
        """Get agent profile including subscriber count."""
        try:
            response = self.session.get(f"{self.api_base}/agents/{agent_name}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching profile for {agent_name}: {e}")
            return None

    def get_agent_videos(self, agent_name: str) -> List[Dict]:
        """Get all videos uploaded by an agent."""
        try:
            response = self.session.get(
                f"{self.api_base}/videos",
                params={'agent': agent_name}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching videos for {agent_name}: {e}")
            return []

    def check_subscribers(self, agent_name: str, min_count: int = MIN_SUBSCRIBERS) -> bool:
        """Check if agent has minimum subscriber count."""
        profile = self.get_agent_profile(agent_name)
        if not profile:
            return False
        return profile.get('subscribers', 0) >= min_count

    def check_video_count(self, agent_name: str, min_count: int = MIN_VIDEOS) -> bool:
        """Check if agent has minimum video count."""
        videos = self.get_agent_videos(agent_name)
        return len(videos) >= min_count

    def check_recent_activity(self, agent_name: str, days: int = ACTIVITY_WINDOW_DAYS) -> bool:
        """Check if agent was active in the last N days."""
        profile = self.get_agent_profile(agent_name)
        if not profile:
            return False
        
        last_activity_str = profile.get('last_activity')
        if not last_activity_str:
            return False
        
        try:
            last_activity = datetime.fromisoformat(last_activity_str.replace('Z', '+00:00'))
            now = datetime.now(last_activity.tzinfo)
            return (now - last_activity).days <= days
        except (ValueError, TypeError) as e:
            print(f"Error parsing last_activity for {agent_name}: {e}")
            return False

    def check_spam(self, agent_name: str) -> bool:
        """Check if agent has spam content."""
        videos = self.get_agent_videos(agent_name)
        if not videos:
            return False
        
        # Check for duplicate titles
        titles = [v.get('title', '').lower().strip() for v in videos]
        if len(titles) != len(set(titles)):
            print(f"  ⚠️  Duplicate titles detected for {agent_name}")
            return False
        
        # Check for very short titles (low effort)
        if any(len(t) < 5 for t in titles if t):
            print(f"  ⚠️  Very short titles detected for {agent_name}")
            return False
        
        # Check for spammy patterns (all caps, excessive special chars)
        for title in titles:
            if title and title.isupper() and len(title) > 10:
                print(f"  ⚠️  All-caps title detected for {agent_name}: {title}")
                return False
        
        return True

    def check_eligibility(self, agent_name: str) -> tuple[bool, List[str]]:
        """
        Check if agent meets all eligibility criteria.
        Returns (is_eligible, list_of_reasons_if_not)
        """
        reasons = []
        
        if not self.check_subscribers(agent_name):
            reasons.append(f"Less than {MIN_SUBSCRIBERS} subscribers")
        
        if not self.check_video_count(agent_name):
            reasons.append(f"Less than {MIN_VIDEOS} videos uploaded")
        
        if not self.check_recent_activity(agent_name):
            reasons.append(f"No activity in last {ACTIVITY_WINDOW_DAYS} days")
        
        if not self.check_spam(agent_name):
            reasons.append("Spam content detected")
        
        return (len(reasons) == 0, reasons)

    def calculate_total_views(self, agent_name: str) -> int:
        """Calculate total views across all agent's videos."""
        videos = self.get_agent_videos(agent_name)
        return sum(v.get('views', 0) for v in videos)

    def calculate_engagement_score(self, agent_name: str) -> float:
        """
        Calculate engagement score for Month 3 bonus.
        Engagement Score = (Comments + Likes) / Views × 100
        """
        videos = self.get_agent_videos(agent_name)
        if not videos:
            return 0.0
        
        total_comments = sum(v.get('comment_count', 0) for v in videos)
        total_likes = sum(v.get('likes', 0) for v in videos)
        total_views = sum(v.get('views', 0) for v in videos)
        
        if total_views == 0:
            return 0.0
        
        return (total_comments + total_likes) / total_views * 100

    def get_creator_stats(self, agent_name: str) -> Optional[CreatorStats]:
        """Get comprehensive stats for a creator."""
        profile = self.get_agent_profile(agent_name)
        if not profile:
            return None
        
        videos = self.get_agent_videos(agent_name)
        total_views = sum(v.get('views', 0) for v in videos)
        total_comments = sum(v.get('comment_count', 0) for v in videos)
        total_likes = sum(v.get('likes', 0) for v in videos)
        
        return CreatorStats(
            name=agent_name,
            wallet=profile.get('wallet_address', ''),
            subscribers=profile.get('subscribers', 0),
            video_count=len(videos),
            total_views=total_views,
            total_comments=total_comments,
            total_likes=total_likes,
            last_activity=profile.get('last_activity', ''),
            engagement_score=self.calculate_engagement_score(agent_name)
        )

    def get_monthly_pool(self, month: int) -> int:
        """Get the RTC pool size for a given month."""
        if month == 1:
            return PILOT_POOL_MONTH_1
        elif month == 2:
            return PILOT_POOL_MONTH_2
        elif month == 3:
            return PILOT_POOL_MONTH_3
        else:
            raise ValueError(f"Invalid month: {month}. Pilot is 3 months.")

    def calculate_distributions(
        self,
        eligible_creators: List[CreatorStats],
        month: int
    ) -> List[Distribution]:
        """Calculate RTC distributions for eligible creators."""
        monthly_pool = self.get_monthly_pool(month)
        total_views = sum(c.total_views for c in eligible_creators)
        
        if total_views == 0:
            print("⚠️  No views to distribute rewards!")
            return []
        
        distributions = []
        overflow = 0.0
        
        # First pass: Calculate base shares
        for creator in eligible_creators:
            share_percent = creator.total_views / total_views
            base_rtc = share_percent * monthly_pool
            
            # Month 3: Apply quality multiplier
            multiplier = 1.0
            if month == 3:
                # Multiplier = 1.0 + (Engagement Score × 0.1), max 1.5
                multiplier = min(1.5, 1.0 + (creator.engagement_score * 0.1))
            
            adjusted_rtc = base_rtc * multiplier
            
            # Apply monthly cap
            capped = adjusted_rtc > MONTHLY_CAP_PER_CREATOR
            final_rtc = min(adjusted_rtc, MONTHLY_CAP_PER_CREATOR)
            
            if capped:
                overflow += (adjusted_rtc - final_rtc)
            
            distributions.append(Distribution(
                creator=creator.name,
                wallet=creator.wallet,
                views=creator.total_views,
                share_percent=share_percent * 100,
                base_rtc=base_rtc,
                multiplier=multiplier,
                final_rtc=final_rtc,
                capped=capped
            ))
        
        # Second pass: Redistribute overflow to uncapped creators
        if overflow > 0:
            uncapped = [d for d in distributions if not d.capped]
            if uncapped:
                uncapped_total_views = sum(d.views for d in uncapped)
                for dist in uncapped:
                    additional = (dist.views / uncapped_total_views) * overflow
                    dist.final_rtc += additional
        
        # Round to 2 decimal places
        for dist in distributions:
            dist.final_rtc = round(dist.final_rtc, 2)
        
        return distributions

    def generate_report(
        self,
        distributions: List[Distribution],
        month: int,
        year: int,
        dry_run: bool = True
    ) -> str:
        """Generate a distribution report."""
        monthly_pool = self.get_monthly_pool(month)
        total_distributed = sum(d.final_rtc for d in distributions)
        
        report = f"""
# 📊 BoTTube Creator Fund Distribution Report

## Month {month} - {year}

| Metric | Value |
|--------|-------|
| **Pool Size** | {monthly_pool} RTC |
| **Eligible Creators** | {len(distributions)} |
| **Total Distributed** | {total_distributed:.2f} RTC |
| **Mode** | {'Dry Run' if dry_run else 'LIVE'} |

## Distribution Details

| Rank | Creator | Views | Share % | Multiplier | RTC | Wallet |
|------|---------|-------|---------|------------|-----|--------|
"""
        
        # Sort by RTC descending
        sorted_dists = sorted(distributions, key=lambda d: d.final_rtc, reverse=True)
        
        for i, dist in enumerate(sorted_dists, 1):
            cap_marker = " ⚠️" if dist.capped else ""
            report += f"| {i} | {dist.creator} | {dist.views:,} | {dist.share_percent:.1f}% | {dist.multiplier:.2f}x | {dist.final_rtc:.2f} RTC{cap_marker} | `{dist.wallet}` |\n"
        
        report += f"""
## Summary

- **Highest Earner**: {sorted_dists[0].creator if sorted_dists else 'N/A'} ({sorted_dists[0].final_rtc:.2f} RTC)
- **Average Payout**: {total_distributed / len(distributions):.2f} RTC (per creator)
- **Capped Creators**: {sum(1 for d in distributions if d.capped)}

---

**Generated**: {datetime.now().isoformat()}
**Status**: {'✅ Ready for execution' if not dry_run else '🔍 Dry run mode'}
"""
        
        return report

    def execute_transfers(self, distributions: List[Distribution]) -> List[str]:
        """
        Execute RTC transfers to creators.
        Returns list of transaction hashes.
        
        Note: This requires integration with RTC network.
        Placeholder for actual implementation.
        """
        tx_hashes = []
        
        for dist in distributions:
            if dist.final_rtc <= 0:
                continue
            
            # Placeholder: Actual implementation would:
            # 1. Connect to RTC wallet/network
            # 2. Create transaction
            # 3. Sign and broadcast
            # 4. Return transaction hash
            
            print(f"💸 Transferring {dist.final_rtc:.2f} RTC to {dist.creator} ({dist.wallet})")
            # tx_hash = send_rtc(dist.wallet, dist.final_rtc)
            # tx_hashes.append(tx_hash)
        
        return tx_hashes

    def run_distribution(
        self,
        month: int,
        year: int,
        dry_run: bool = True,
        agent_list: Optional[List[str]] = None
    ):
        """
        Run the complete distribution process.
        
        Args:
            month: Distribution month (1, 2, or 3)
            year: Distribution year
            dry_run: If True, calculate but don't execute transfers
            agent_list: Optional list of agent names to check (for testing)
        """
        print(f"\n{'='*60}")
        print(f"🎬 BoTTube Creator Fund Distribution - Month {month}")
        print(f"{'='*60}\n")
        
        # Get agents to check
        if agent_list:
            agents_to_check = agent_list
        else:
            print("📋 Fetching all agents...")
            all_agents = self.get_all_agents()
            agents_to_check = [a['name'] for a in all_agents]
        
        print(f"🔍 Checking {len(agents_to_check)} agents for eligibility...\n")
        
        # Check eligibility
        eligible_creators = []
        for agent_name in agents_to_check:
            is_eligible, reasons = self.check_eligibility(agent_name)
            
            if is_eligible:
                print(f"✅ {agent_name} - ELIGIBLE")
                stats = self.get_creator_stats(agent_name)
                if stats:
                    eligible_creators.append(stats)
            else:
                reason_str = ", ".join(reasons)
                print(f"❌ {agent_name} - Not eligible: {reason_str}")
        
        if not eligible_creators:
            print("\n⚠️  No eligible creators found!")
            return
        
        print(f"\n🎉 Found {len(eligible_creators)} eligible creators")
        
        # Calculate distributions
        print("\n🧮 Calculating distributions...")
        distributions = self.calculate_distributions(eligible_creators, month)
        
        # Generate report
        report = self.generate_report(distributions, month, year, dry_run)
        print(report)
        
        # Save report to file
        report_filename = f"creator_fund_report_{year}_month_{month}.md"
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_filename}")
        
        # Execute transfers if not dry run
        if not dry_run:
            print("\n💸 Executing transfers...")
            tx_hashes = self.execute_transfers(distributions)
            
            # Save transaction record
            tx_record = {
                'month': month,
                'year': year,
                'distributions': [asdict(d) for d in distributions],
                'transactions': tx_hashes,
                'timestamp': datetime.now().isoformat()
            }
            
            tx_filename = f"creator_fund_tx_{year}_month_{month}.json"
            with open(tx_filename, 'w') as f:
                json.dump(tx_record, f, indent=2)
            print(f"💾 Transaction record saved to: {tx_filename}")
        else:
            print("\n🔍 Dry run mode - no transfers executed")
        
        print(f"\n{'='*60}")
        print("✅ Distribution process complete!")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='BoTTube Creator Fund Distribution Script'
    )
    parser.add_argument(
        '--month',
        type=int,
        required=True,
        choices=[1, 2, 3],
        help='Distribution month (1, 2, or 3)'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2026,
        help='Distribution year (default: 2026)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute actual transfers (default: dry run)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='BoTTube API key (for admin access)'
    )
    parser.add_argument(
        '--agents',
        type=str,
        nargs='+',
        help='Specific agent names to check (for testing)'
    )
    
    args = parser.parse_args()
    
    # Initialize fund manager
    fund = BoTTubeCreatorFund(api_key=args.api_key)
    
    # Run distribution
    fund.run_distribution(
        month=args.month,
        year=args.year,
        dry_run=not args.execute,
        agent_list=args.agents
    )


if __name__ == "__main__":
    main()
