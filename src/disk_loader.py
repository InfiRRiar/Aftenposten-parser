import aiohttp
from settings import settings
from loguru import logger


class YandexDiskClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.headers = {
            "Authorization": f"OAuth {settings.yd_token}"
        }
        self.api_url = "https://cloud-api.yandex.net/v1/disk/resources"
        
    async def check_entity_existence(self, disk_path: str) -> str|None:
        params = {
            "path": disk_path
        }
        async with self.session.get(self.api_url, headers=self.headers, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("type")
            elif resp.status == 404:
                return "empty"
            else:
                error_text = await resp.text()
                logger.error(f"Something wrong with disk checking: {error_text}")
                return None
    
    async def create_folder(self, disk_path: str) -> bool:
        params = {
            "path": disk_path
        }
        async with self.session.put(url=self.api_url, headers=self.headers, params=params) as resp:
            if resp.status == 201:
                logger.info(f"{disk_path} created")
                return True
            else:
                error_text = await resp.text()
                logger.error(f"Something went wrong creating a dir: {error_text}")
                return False

    async def get_upload_url(self, disk_path: str) -> str:
        params = {
            "path": disk_path,
            "overwrite": "true"
        }

        async with self.session.get(f"{self.api_url}/upload", headers=self.headers, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["href"]

    async def upload_file(self, content, disk_path: str):
        upload_url = await self.get_upload_url(disk_path)
        async with self.session.put(upload_url, data=content) as resp:
            resp.raise_for_status()
        return disk_path