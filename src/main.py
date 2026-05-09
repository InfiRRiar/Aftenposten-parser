from playwright.async_api import async_playwright
from datetime import timedelta
import json
import asyncio
from loguru import logger
import aiohttp
from yarl import URL
from src.disk_loader import YandexDiskClient
from settings import settings


current = settings.start_date
dates = []

while current <= settings.end_date:
    dates.append(current.strftime("%Y-%m-%d"))
    current += timedelta(days=1)

token_checker = "https://content.textalk.se/api/web-reader/v1/issues/{ns_id}/pdf-token"

# It's important to save the cookie files from the browser to "cookies.json". The cookies store the record that we have already logged into our account on this website.
# Without them, the code would have to log into the profile again - with CAPTCHA, email confirmations, and so on, which is unpleasant.
with open("cookies.json") as f:
    cookies = json.load(f)["cookies"]

s = 0

async def get_pdf_content(page, date: str, disk_client: YandexDiskClient, session: aiohttp.ClientSession):
    # you can slightly change the url here in order to process other types of publisher's newspapers
    await page.goto(f"https://e-avis.aftenposten.no/search?title=7545,7549,991,7547,9349,9351,9355,9357&from={date}&to={date}")
    locator = page.locator("div div div div div a")

    while True:
        try:
            h1 = False
            await locator.first.wait_for(state="visible", timeout=1000)
            break
        except Exception:
            h1 = await page.locator("h1", has_text="Fant ingen publikasjoner").count() > 0
            if h1:
                break
    if h1:
        return
    
    links = await locator.element_handles()
    links = [await link.get_attribute("href") for link in links]
    for href in links:
        newspaper_type = href.split('/')[2]
        ns_id = href.split("/")[-1] # unique article identificator used for getting a request token
        
        async with session.get(token_checker.format(ns_id=ns_id)) as r:
            response = await r.json()
            
        url = response["url"]
        
        dir_for_paper = f"newspapers/{newspaper_type}"
        dir_exist = await disk_client.check_entity_existence(dir_for_paper) == "dir"
        if not dir_exist:
            await disk_client.create_folder(dir_for_paper)
        async with session.get(url, params={"h": settings.auth_token}) as resp:
            await disk_client.upload_file(
                resp.content,
                disk_path=f"{dir_for_paper}/{date}.pdf"
            )
    logger.info(f"processed {date}")

async def load_pdf_worker(context, date_queue, load_queue, session):
    while True:
        date = await date_queue.get()
        try:
            page = await context.new_page()
            await get_pdf_content(page, date["date"], load_queue, session)
        except Exception as e:
            logger.info(f"WEB: {str(e)}")
        finally:
            await page.close()
            date_queue.task_done()
        

async def main():
    queue_for_load = asyncio.Queue()
    for date in dates:
        await queue_for_load.put({"date": date})
        
    jar = aiohttp.CookieJar()
    for c in cookies:
        jar.update_cookies(
            {c["name"]: c["value"]},
            response_url=URL(f"https://{c['domain'].lstrip('.')}")
        )
    
    async with aiohttp.ClientSession(headers={
        "authorization": settings.auth_bearer,
        "x-textalk-content-client-authorize": settings.textalk,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    }, cookie_jar=jar) as session_http:
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            client = YandexDiskClient(session=session_http)
            context = await browser.new_context(storage_state="cookies.json")
            pdf_workers = [asyncio.create_task(load_pdf_worker(context, queue_for_load, client, session=session_http)) for _ in range(3)]
            
            await queue_for_load.join()
            
            for w in pdf_workers:
                w.cancel()
                
        await context.close()
        browser.close()

if __name__ == "__main__":
    asyncio.run(main=main())