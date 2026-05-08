import aiohttp
from settings import settings


class YandexDiskClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_upload_url(self, disk_path: str) -> str:
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {
            "path": disk_path,
            "overwrite": "true"
        }
        headers = {
            "Authorization": f"OAuth {settings.yd_token}"
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["href"]

    async def upload_file(self, content, disk_path: str):
        upload_url = await self.get_upload_url(disk_path)
        async with self.session.put(upload_url, data=content) as resp:
            resp.raise_for_status()
        return disk_path