"""Trend service for generating and tracking trends."""
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.research_item import ResearchItem
from app.models.tag import Tag
from app.models.trend import Trend, TrendPeriod, TrendType


class TrendService:
    """Service for generating trends."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_trends(self) -> Dict:
        """Generate trends from recent items."""
        now = datetime.utcnow()
        
        results = {
            "weekly": await self._generate_period_trends(TrendPeriod.WEEKLY, now - timedelta(days=7), now),
            "monthly": await self._generate_period_trends(TrendPeriod.MONTHLY, now - timedelta(days=30), now),
        }
        
        return results
    
    async def _generate_period_trends(
        self,
        period: TrendPeriod,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict:
        """Generate trends for a specific period."""
        # Get items from period
        result = await self.db.execute(
            select(ResearchItem)
            .where(
                ResearchItem.published_date >= start_date,
                ResearchItem.published_date <= end_date,
            )
        )
        items = result.scalars().all()
        
        # Extract architectures
        architectures = []
        for item in items:
            if item.architecture_family:
                architectures.append(item.architecture_family.value)
        
        arch_trends = await self._create_trends_from_counter(
            Counter(architectures),
            TrendType.ARCHITECTURE,
            period,
            start_date,
            end_date,
            items,
        )
        
        # Extract tags as topics
        tag_counter = Counter()
        for item in items:
            for tag in item.tags:
                tag_counter[tag.name] += 1
        
        topic_trends = await self._create_trends_from_counter(
            tag_counter,
            TrendType.TOPIC,
            period,
            start_date,
            end_date,
            items,
        )
        
        # Extract modalities
        modalities = []
        for item in items:
            if item.modality:
                modalities.append(item.modality.value)
        
        method_trends = await self._create_trends_from_counter(
            Counter(modalities),
            TrendType.METHOD,
            period,
            start_date,
            end_date,
            items,
        )
        
        return {
            "architectures": len(arch_trends),
            "topics": len(topic_trends),
            "methods": len(method_trends),
            "total_items_analyzed": len(items),
        }
    
    async def _create_trends_from_counter(
        self,
        counter: Counter,
        trend_type: TrendType,
        period: TrendPeriod,
        start_date: datetime,
        end_date: datetime,
        items: List[ResearchItem],
    ) -> List[Trend]:
        """Create trend records from a counter."""
        trends = []
        
        for name, frequency in counter.most_common(20):
            if frequency < 2:  # Skip rare items
                continue
            
            # Check if trend already exists
            result = await self.db.execute(
                select(Trend).where(
                    Trend.name == name,
                    Trend.trend_type == trend_type,
                    Trend.period == period,
                    Trend.period_start == start_date,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.frequency = frequency
                trend = existing
            else:
                # Create slug
                import re
                slug = re.sub(r'[^\w\s-]', '', name.lower())
                slug = re.sub(r'[-\s]+', '-', slug)
                
                trend = Trend(
                    name=name,
                    slug=slug,
                    trend_type=trend_type,
                    period=period,
                    period_start=start_date,
                    period_end=end_date,
                    frequency=frequency,
                    popularity_score=min(100.0, frequency * 5),
                )
                self.db.add(trend)
            
            trends.append(trend)
        
        await self.db.commit()
        return trends
