import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

class DataStoreService:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self.key_ttl = 60 * 60 * 24  # 24 hours

    async def store_company_data(self, chat_id: str, company_data: Dict[str, Any]) -> List[str]:
        """
        Store company data in Redis, creating unique IDs for each company
        Returns list of company IDs created
        """
        try:
            company_ids = []
            if "companies" in company_data:
                for company in company_data["companies"]:
                    # Generate unique ID for company
                    company_id = str(uuid.uuid4())
                    company_ids.append(company_id)
                    
                    # Store company data
                    company_key = f"company:{company_id}"
                    await self.redis.hset(company_key, mapping={
                        "name": company["name"],
                        "summary": company["summary"],
                        "funding": json.dumps(company.get("funding", {})),
                        "chat_id": chat_id,
                        "created_at": str(datetime.utcnow())
                    })
                    await self.redis.expire(company_key, self.key_ttl)

                    # Store links separately
                    if "links" in company:
                        links_key = f"{company_key}:links"
                        for link_type, link_data in company["links"].items():
                            if link_data and "link" in link_data:
                                link_id = await self.redis.incr("link_id_counter")
                                link_info = {
                                    "id": link_id,
                                    "type": link_type,
                                    "url": link_data["link"],
                                    "password": link_data.get("password", ""),
                                    "company_id": company_id
                                }
                                await self.redis.sadd(links_key, json.dumps(link_info))
                                await self.redis.expire(links_key, self.key_ttl)

                    # Store chat_id to company_id mapping for later reference
                    chat_companies_key = f"chat:{chat_id}:companies"
                    await self.redis.sadd(chat_companies_key, company_id)
                    await self.redis.expire(chat_companies_key, self.key_ttl)

            logger.info(f"Stored {len(company_ids)} companies for chat {chat_id}")
            return company_ids

        except Exception as e:
            logger.error(f"Error storing company data: {str(e)}")
            return []

    async def get_company_data(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve company data from Redis"""
        try:
            company_key = f"company:{company_id}"
            company_data = await self.redis.hgetall(company_key)
            
            if not company_data:
                return None

            # Convert stored JSON strings back to objects
            if "funding" in company_data:
                company_data["funding"] = json.loads(company_data["funding"])

            # Get links
            links_key = f"{company_key}:links"
            links_data = await self.redis.smembers(links_key)
            if links_data:
                company_data["links"] = [json.loads(link) for link in links_data]

            return company_data

        except Exception as e:
            logger.error(f"Error retrieving company data: {str(e)}")
            return None

    async def get_companies_by_chat(self, chat_id: str) -> List[str]:
        """Get all company IDs associated with a chat"""
        try:
            chat_companies_key = f"chat:{chat_id}:companies"
            return [cid.decode() for cid in await self.redis.smembers(chat_companies_key)]
        except Exception as e:
            logger.error(f"Error getting companies for chat {chat_id}: {str(e)}")
            return []

    async def store_scrape_data(self, link_id: int, scrape_data: Dict[str, Any]) -> bool:
        """Store scraping results"""
        try:
            key = f"link:{link_id}:scrape"
            await self.redis.hset(key, mapping={
                "content": json.dumps(scrape_data),
                "timestamp": str(datetime.utcnow())
            })
            await self.redis.expire(key, self.key_ttl)
            return True
        except Exception as e:
            logger.error(f"Error storing scrape data: {str(e)}")
            return False
