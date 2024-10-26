import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List
from redis import asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DataStoreService:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self.key_ttl = settings.REDIS_KEY_TTL

    async def store_company_data(self, chat_id: str, company_data: Dict[str, Any]) -> List[str]:
        """Store company data in Redis with processing status"""
        try:
            company_ids = []
            if "companies" in company_data:
                for company in company_data["companies"]:
                    company_id = self._generate_id()
                    company_ids.append(company_id)
                    
                    logger.debug(f"Processing company: {company['name']}")

                    # Store company data
                    company_key = f"company:{company_id}"
                    await self.redis.hset(company_key, mapping={
                        "name": company["name"],
                        "summary": company["summary"],
                        "funding": json.dumps(company.get("funding", {})),
                        "chat_id": chat_id,
                        "created_at": str(datetime.utcnow()),
                        "processing_status": ProcessingStatus.PENDING.value
                    })
                    await self.redis.expire(company_key, self.key_ttl)

                    # Debug log the incoming data structure
                    logger.debug(f"Links data: {company.get('links', {})}")
                    logger.debug(f"Socials data: {company.get('socials', {})}")

                    # Combine links and socials into a single dictionary
                    all_links = {}
                    if "links" in company:
                        for link_type, link_data in company["links"].items():
                            if isinstance(link_data, dict) and link_data.get("link"):
                                all_links[link_type] = {
                                    "link": link_data["link"],
                                    "password": link_data.get("password", "")
                                }
                                logger.debug(f"Added link: {link_type} -> {link_data['link']}")

                    if "socials" in company:
                        for social_type, url in company["socials"].items():
                            if url:
                                all_links[social_type] = {
                                    "link": url,
                                    "password": ""
                                }
                                logger.debug(f"Added social: {social_type} -> {url}")

                    logger.debug(f"Combined links: {all_links}")

                    # Store all links
                    for link_type, link_data in all_links.items():
                        link_id = self._generate_id()
                        link_key = f"link:{link_id}"

                        link_mapping = {
                            "id": str(link_id),
                            "type": link_type,
                            "url": link_data["link"],
                            "password": link_data.get("password", ""),
                            "company_id": company_id,
                            "processing_status": ProcessingStatus.PENDING.value,
                            "last_updated": str(datetime.utcnow())
                        }

                        logger.debug(f"Storing link {link_id}: {link_mapping}")

                        await self.redis.hset(link_key, mapping=link_mapping)
                        await self.redis.expire(link_key, self.key_ttl)
                        await self.redis.sadd(f"{company_key}:link_ids", link_id)
                        await self.redis.sadd("links:pending", link_id)

                    logger.info(f"Stored {len(all_links)} links for company {company_id}")

            return company_ids
        except Exception as e:
            logger.error(f"Error storing company data: {str(e)}", exc_info=True)
            return []

    def _generate_id(self) -> str:
        return str(uuid.uuid4())[:8]
