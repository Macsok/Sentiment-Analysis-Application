import asyncio
import csv
from playwright.async_api import async_playwright, TimeoutError
import re

 # Get URL from user input
username = "dwadwadwaw11384"
password = "password12345"

async def login_to_x(page, username: str, password: str):
    """Log in to X.com using provided credentials."""
    print("Navigating to login page...")
    await page.goto("https://x.com/login")
    await page.fill("input[name='text']", username)
    await page.press("input[name='text']", "Enter")

    try:
        await page.wait_for_selector("input[name='text']", timeout=10000)
        await page.fill("input[name='text']", username)
        await page.press("input[name='text']", "Enter")
    except TimeoutError:
        print("No second username prompt.")

    await page.wait_for_selector("input[name='password']", timeout=1000)
    await page.fill("input[name='password']", password)
    await page.press("input[name='password']", "Enter")

    await page.wait_for_selector("a[data-testid='AppTabBar_Home_Link']", timeout=15000)
    print("Logged in successfully.")

async def extract_replies(replies_data, page, max_replies=200):
    reply_selector = "[data-testid='tweet'][tabindex='0']"
    text_selector = "div[data-testid='tweetText'] span"
    username_selector = "div[data-testid='User-Name'] span span"

    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_selector(reply_selector)

    loaded_replies_count = 0

    while loaded_replies_count < max_replies:
        reply_cards = page.locator(reply_selector)
        replies_count = await reply_cards.count()

        for index in range(replies_count):
            reply = reply_cards.nth(index)
            reply_texts = await reply.locator(text_selector).all_inner_texts()
            reply_text = " ".join(reply_texts) if reply_texts else None

            usernames = await reply.locator(username_selector).all_inner_texts()
            username = usernames[0] if usernames else None

            reply_text = clean_data(reply_text)
            username = clean_data(username)

            if reply_text:
                if reply_text and username and reply_text not in [reply["reply_text"] for reply in replies_data]:
                    data_to_save = {
                        "username": username,
                        "reply_text": reply_text,
                    }
                    replies_data.append(data_to_save)
                    loaded_replies_count += 1

                    if loaded_replies_count >= max_replies:
                        break

        await page.mouse.wheel(0, 1000)
        await page.wait_for_timeout(10000)

        new_replies_count = await page.locator(reply_selector).count()
        if new_replies_count <= replies_count:
            break


    #save_data_to_csv(replies_data, "X_Tweet_Replies.csv")
    return replies_data

async def run(playwright, url) -> list:
    replies_data = []
    while len(replies_data) == 0:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_default_timeout(120000)

        await login_to_x(page, username, password)
        await page.goto(url, wait_until="domcontentloaded")
        replies_data = await extract_replies(replies_data, page)

        await context.close()
        await browser.close()

    return replies_data

def clean_data(data):
    if not data:
        return None
    cleaned_data = " ".join(data.split()).strip()
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")

    if re.search(r'[a-zA-Z]', cleaned_data):
        return cleaned_data
    return None

def save_data_to_csv(replies_data: list, filename: str):
    header = ["username", "reply_text"]

    with open(filename, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(replies_data)

async def main(url) -> list:
    async with async_playwright() as playwright:
        return await run(playwright, url)

# Running the asyncio event loop and capturing returned replies_data
#url5 = input("Give X.com tweet URL: ")
#replies_data = asyncio.run(main(url5))
