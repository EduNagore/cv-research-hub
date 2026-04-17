"""Gemini-powered discovery of fresh research items."""
import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.category import Category
from app.models.research_item import (
    ArchitectureFamily,
    ContributionType,
    ModalityType,
    ResearchItem,
    SourceType,
    StatusLabel,
    research_item_categories,
    research_item_tags,
)
from app.models.tag import Tag
from app.services.classification import ClassificationService
from app.services.scoring import ScoringService

settings = get_settings()


class GeminiDiscoveryService:
    """Discover fresh research items with a Gemini-generated category snapshot."""

    API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, db: AsyncSession, *, batch_id: Optional[str] = None):
        self.db = db
        self.batch_id = batch_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.classification_service = ClassificationService()
        self.scoring_service = ScoringService()

    async def run_daily_discovery(self) -> Dict[str, Any]:
        """Query Gemini once for all active categories and persist discovered items."""
        if not settings.GEMINI_API_KEY:
            return {
                "source": "gemini_discovery",
                "ingested": 0,
                "updated": 0,
                "skipped": 0,
                "error": "Gemini API key not configured",
            }

        result = await self.db.execute(
            select(Category).where(Category.is_active.is_(True)).order_by(Category.display_order, Category.id)
        )
        categories = result.scalars().all()
        return await self._run_snapshot_discovery(categories)

    async def run_category_discovery(self, category_slug: str) -> Dict[str, Any]:
        """Query Gemini for a single active category and persist discovered items."""
        if not settings.GEMINI_ENABLE_CATEGORY_REFRESH:
            raise ValueError("Category refresh is disabled. Use the daily full Gemini refresh instead.")
        if not settings.GEMINI_API_KEY:
            return {
                "source": "gemini_discovery",
                "ingested": 0,
                "updated": 0,
                "skipped": 0,
                "error": "Gemini API key not configured",
            }

        result = await self.db.execute(
            select(Category)
            .where(Category.is_active.is_(True), Category.slug == category_slug)
            .order_by(Category.display_order, Category.id)
        )
        categories = result.scalars().all()
        if not categories:
            raise ValueError(f"Unknown or inactive category: {category_slug}")

        return await self._run_snapshot_discovery(categories)

    async def _run_snapshot_discovery(self, categories: List[Category]) -> Dict[str, Any]:
        """Execute Gemini discovery for the provided categories using one grouped snapshot call."""
        ingested = 0
        updated = 0
        skipped = 0
        category_results: List[Dict[str, Any]] = []
        categories_by_slug = {category.slug: category for category in categories}

        async with httpx.AsyncClient(timeout=90.0) as client:
            grouped_items = await self._discover_snapshot(client, categories)

        for category in categories:
            items = grouped_items.get(category.slug, [])
            cat_ingested = 0
            cat_updated = 0
            cat_skipped = 0
            cat_error: Optional[str] = None
            try:
                for payload in items:
                    outcome = await self._save_discovered_item(payload, category)
                    if outcome == "ingested":
                        ingested += 1
                        cat_ingested += 1
                    elif outcome == "updated":
                        updated += 1
                        cat_updated += 1
                    else:
                        skipped += 1
                        cat_skipped += 1
            except Exception as exc:
                cat_error = str(exc)

            entry = {
                "category": category.slug,
                "received": len(items),
                "ingested": cat_ingested,
                "updated": cat_updated,
                "skipped": cat_skipped,
            }
            if cat_error:
                entry["error"] = cat_error
            category_results.append(entry)

        extra_category_slugs = [slug for slug in grouped_items.keys() if slug not in categories_by_slug]
        for slug in extra_category_slugs:
            category_results.append(
                {
                    "category": slug,
                    "received": len(grouped_items[slug]),
                    "ingested": 0,
                    "updated": 0,
                    "skipped": len(grouped_items[slug]),
                    "error": "Gemini returned an unknown category slug",
                }
            )

        return {
            "source": "gemini_discovery",
            "ingested": ingested,
            "updated": updated,
            "skipped": skipped,
            "batch_id": self.batch_id,
            "categories": category_results,
        }

    async def _discover_snapshot(self, client: httpx.AsyncClient, categories: List[Category]) -> Dict[str, List[Dict[str, Any]]]:
        """Ask Gemini for one grouped JSON payload covering all requested categories."""
        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": (
                            "You are curating a computer vision research tracker. "
                            "Use Google Search grounding to find recent, real, verifiable items and return only JSON."
                        )
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": self._build_snapshot_prompt(categories)}],
                }
            ],
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "temperature": 0.2,
            },
        }

        response = await self._post_with_retry(client, payload, settings.GEMINI_MODEL)
        data = response.json()

        text = self._extract_text_response(data)
        parsed = self._parse_json_response(text)
        category_groups = parsed.get("categories", [])
        if not isinstance(category_groups, list):
            return {}

        grouped_items: Dict[str, List[Dict[str, Any]]] = {}
        for group in category_groups:
            if not isinstance(group, dict):
                continue
            category_slug = group.get("category_slug")
            items = group.get("items", [])
            if not isinstance(category_slug, str) or not isinstance(items, list):
                continue

            normalized_items = []
            for item in items[: settings.GEMINI_RESULTS_PER_CATEGORY]:
                if isinstance(item, dict) and item.get("title") and item.get("primary_url") and item.get("summary"):
                    normalized_items.append(item)
            grouped_items[category_slug] = normalized_items

        return grouped_items

    def _build_snapshot_prompt(self, categories: List[Category]) -> str:
        category_lines = "\n".join(
            f'- slug: "{category.slug}", name: "{category.name}", description: "{category.description or "N/A"}"'
            for category in categories
        )
        return (
            f"Find up to {settings.GEMINI_RESULTS_PER_CATEGORY} genuinely recent items from the last "
            f"{settings.GEMINI_LOOKBACK_DAYS} days for each of these computer vision categories.\n"
            f"{category_lines}\n"
            "Use Google Search grounding. Search for a balanced mix of papers, technical articles, repositories, model releases, "
            "and architecture writeups that are relevant to researchers and builders. Exclude low-quality SEO pages, duplicates, "
            "and unverifiable claims. Return only one valid JSON object with this exact top-level shape: "
            "{\"categories\":[{\"category_slug\":\"classification\",\"items\":[{\"title\":\"...\",\"item_type\":\"article|paper|repository|model_release|architecture\","
            "\"primary_url\":\"https://...\",\"paper_url\":\"https://...\",\"code_url\":\"https://...\",\"project_page_url\":\"https://...\","
            "\"authors\":[\"...\"],\"published_at\":\"2026-04-16\",\"summary\":\"...\",\"why_it_matters\":\"...\",\"problem_solved\":\"...\","
            "\"contribution_description\":\"...\",\"use_cases\":[\"...\"],\"category_slugs\":[\"classification\"],\"tags\":[\"...\"],"
            "\"contribution_type\":\"paper|model|repository|dataset|benchmark\",\"modality\":\"image|video|multimodal|3d|medical|histopathology|dermatology\","
            "\"architecture_family\":\"cnn|transformer|diffusion|gan|autoencoder|rnn|mlp|hybrid|other\",\"model_name\":\"...\",\"source_name\":\"...\"}]}]}"
        )

    def _extract_text_response(self, response_data: Dict[str, Any]) -> str:
        candidates = response_data.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini returned no candidates")

        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        text_chunks = []
        for part in parts:
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                text_chunks.append(text.strip())

        if not text_chunks:
            finish_reason = candidate.get("finishReason")
            raise ValueError(
                "Gemini returned no text content. "
                f"finishReason={finish_reason!r}, candidate_keys={list(candidate.keys())}"
            )

        return "\n".join(text_chunks).strip()

    async def _post_with_retry(
        self,
        client: httpx.AsyncClient,
        payload: Dict[str, Any],
        model_name: str,
    ) -> httpx.Response:
        """Post to Gemini with retry and backoff for quota/rate-limit errors."""
        last_error: Optional[Exception] = None
        for attempt in range(settings.GEMINI_MAX_RETRIES + 1):
            try:
                response = await client.post(
                    self.API_URL_TEMPLATE.format(model=model_name),
                    headers={"x-goog-api-key": settings.GEMINI_API_KEY},
                    json=payload,
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status_code = exc.response.status_code
                detail = exc.response.text.strip()
                if status_code not in {429, 500, 503}:
                    raise ValueError(f"Gemini API request failed with {status_code}: {detail}") from exc
                if attempt >= settings.GEMINI_MAX_RETRIES:
                    break

                retry_after = exc.response.headers.get("retry-after")
                delay = self._compute_retry_delay(attempt, retry_after)
                await asyncio.sleep(delay)
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= settings.GEMINI_MAX_RETRIES:
                    raise ValueError(f"Gemini API transport error: {exc}") from exc
                await asyncio.sleep(self._compute_retry_delay(attempt, None))

        if (
            model_name == settings.GEMINI_MODEL
            and settings.GEMINI_FALLBACK_MODEL
            and settings.GEMINI_FALLBACK_MODEL != settings.GEMINI_MODEL
        ):
            return await self._post_with_retry(client, payload, settings.GEMINI_FALLBACK_MODEL)

        raise ValueError(f"Gemini API request failed after retries using model {model_name}: {last_error}")

    def _compute_retry_delay(self, attempt: int, retry_after: Optional[str]) -> float:
        """Compute delay before retrying Gemini requests."""
        if retry_after:
            try:
                return max(float(retry_after), settings.GEMINI_REQUEST_DELAY_SECONDS)
            except ValueError:
                pass
        return max(settings.GEMINI_REQUEST_DELAY_SECONDS, min(2 ** attempt, 20))

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON response, tolerating fenced code blocks."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            fenced_match = re.search(r"```json\s*(\{.*\})\s*```", text, flags=re.DOTALL)
            if fenced_match:
                return json.loads(fenced_match.group(1))

            object_match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
            if object_match:
                return json.loads(object_match.group(1))

            raise ValueError("Gemini returned non-JSON text")

    async def _save_discovered_item(self, payload: Dict[str, Any], category: Category) -> str:
        primary_url = payload.get("primary_url", "").strip()
        title = payload.get("title", "").strip()
        if not primary_url or not title:
            return "skipped"

        source_id = self._build_source_id(primary_url, title)
        existing = await self.db.execute(
            select(ResearchItem).where(
                or_(
                    ResearchItem.source_id == source_id,
                    ResearchItem.source_url == primary_url,
                )
            )
        )
        item = existing.scalar_one_or_none()

        combined_text = "\n\n".join(
            filter(
                None,
                [
                    payload.get("summary", ""),
                    payload.get("why_it_matters", ""),
                    payload.get("problem_solved", ""),
                    payload.get("contribution_description", ""),
                ],
            )
        )
        classification = await self.classification_service.classify(title=title, abstract=combined_text)

        category_slugs = payload.get("category_slugs") or []
        category_slugs = [slug for slug in category_slugs if isinstance(slug, str)]
        if category.slug not in category_slugs:
            category_slugs.append(category.slug)

        tag_names = payload.get("tags") or []
        tag_names = [tag for tag in tag_names if isinstance(tag, str)]

        published_date = self._parse_datetime(payload.get("published_at"))
        contribution_type = self._parse_enum(
            ContributionType,
            payload.get("contribution_type"),
            classification.get("contribution_type", ContributionType.PAPER),
        )
        modality = self._parse_enum(ModalityType, payload.get("modality"), classification.get("modality"))
        architecture = self._parse_enum(
            ArchitectureFamily,
            payload.get("architecture_family"),
            classification.get("architecture_family", ArchitectureFamily.OTHER),
        )

        data = {
            "title": title,
            "source": SourceType.OTHER,
            "source_id": source_id,
            "source_url": primary_url,
            "published_date": published_date,
            "authors": payload.get("authors") or None,
            "abstract": payload.get("summary"),
            "short_summary": self._truncate(payload.get("summary"), 320) or classification.get("short_summary"),
            "full_summary": payload.get("summary") or classification.get("full_summary"),
            "why_it_matters": payload.get("why_it_matters") or classification.get("why_it_matters"),
            "problem_solved": payload.get("problem_solved"),
            "contribution_description": payload.get("contribution_description"),
            "use_cases": payload.get("use_cases") or None,
            "paper_url": payload.get("paper_url"),
            "code_url": payload.get("code_url"),
            "github_url": payload.get("code_url") if "github.com" in (payload.get("code_url") or "") else None,
            "project_page_url": payload.get("project_page_url"),
            "contribution_type": contribution_type,
            "modality": modality,
            "architecture_family": architecture,
            "model_name": payload.get("model_name") or classification.get("model_name"),
            "status_label": StatusLabel.NEW,
            "is_official_code": bool(payload.get("code_url")),
            "ingestion_batch_id": self.batch_id,
            "last_ingested_at": datetime.utcnow(),
            "raw_metadata": {
                "discovered_via": "gemini",
                "item_type": payload.get("item_type"),
                "category_slug": category.slug,
                "source_name": payload.get("source_name"),
                "primary_url": primary_url,
            },
        }

        if item is None:
            item = ResearchItem(
                slug=self._generate_slug(title, source_id),
                **data,
            )
            self.db.add(item)
            await self.db.flush()
            await self._assign_categories_and_tags(item, category_slugs, tag_names + classification.get("tags", []))
            await self.scoring_service.calculate_score(item)
            return "ingested"

        for field, value in data.items():
            setattr(item, field, value)

        await self._assign_categories_and_tags(item, category_slugs, tag_names + classification.get("tags", []))
        await self.scoring_service.calculate_score(item)
        return "updated"

    def _build_source_id(self, primary_url: str, title: str) -> str:
        base = primary_url or title
        digest = hashlib.md5(base.encode("utf-8")).hexdigest()[:12]
        return f"gemini_{digest}"

    def _generate_slug(self, title: str, unique_id: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        slug = slug[:100]
        hash_suffix = hashlib.md5(unique_id.encode("utf-8")).hexdigest()[:8]
        return f"{slug}-{hash_suffix}"

    def _truncate(self, value: Optional[str], max_length: int) -> Optional[str]:
        if not value:
            return value
        return value if len(value) <= max_length else value[: max_length - 3].rstrip() + "..."

    def _parse_datetime(self, value: Optional[str]) -> datetime:
        if not value:
            return datetime.utcnow()

        cleaned = value.strip()
        try:
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return parsed
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            return datetime.utcnow()

    def _parse_enum(self, enum_cls, value: Optional[str], fallback):
        if isinstance(value, str):
            normalized = value.strip().lower().replace(" ", "_")
            for member in enum_cls:
                if member.value == normalized:
                    return member
        return fallback

    async def _assign_categories_and_tags(
        self,
        item: ResearchItem,
        category_names: List[str],
        tag_names: List[str],
    ) -> None:
        if item.id is None:
            await self.db.flush()

        existing_category_ids = set(
            (
                await self.db.execute(
                    select(research_item_categories.c.category_id).where(
                        research_item_categories.c.research_item_id == item.id
                    )
                )
            ).scalars().all()
        )
        for category_name in dict.fromkeys(category_names):
            result = await self.db.execute(
                select(Category).where(
                    or_(
                        Category.name.ilike(category_name),
                        Category.slug.ilike(category_name),
                    )
                )
            )
            matched_category = result.scalar_one_or_none()
            if matched_category and matched_category.id not in existing_category_ids:
                await self.db.execute(
                    insert(research_item_categories).values(
                        research_item_id=item.id,
                        category_id=matched_category.id,
                    )
                )
                matched_category.item_count += 1
                existing_category_ids.add(matched_category.id)

        existing_tag_ids = set(
            (
                await self.db.execute(
                    select(research_item_tags.c.tag_id).where(
                        research_item_tags.c.research_item_id == item.id
                    )
                )
            ).scalars().all()
        )
        for tag_name in dict.fromkeys(tag_names):
            normalized = tag_name.strip()
            if not normalized:
                continue

            result = await self.db.execute(select(Tag).where(Tag.name.ilike(normalized)))
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(
                    name=normalized,
                    slug=self._generate_slug(normalized, normalized),
                )
                self.db.add(tag)
                await self.db.flush()

            if tag.id not in existing_tag_ids:
                await self.db.execute(
                    insert(research_item_tags).values(
                        research_item_id=item.id,
                        tag_id=tag.id,
                    )
                )
                tag.item_count += 1
                existing_tag_ids.add(tag.id)
