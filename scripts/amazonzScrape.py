import asyncio
import csv
from playwright.async_api import async_playwright
import re

url = "https://www.amazon.com/Redragon-S101-Keyboard-Ergonomic-Programmable/dp/B00NLZUM36/ref=sr_1_4?_encoding=UTF8&content-id=amzn1.sym.12129333-2117-4490-9c17-6d31baf0582a&dib=eyJ2IjoiMSJ9.7_LpxWwuBa0EKw4v976athwpXnhNZrtv8JW5ZP3BaCgoxxcpIFE9hbLGeOYfaaswhFOXn7jWAZu9EGtj4uGuNLhiJRy1N9U7ZvPxWN08MmmZQkmA4bANVBXaLn61_z5oA-mpmVLN2jz3sMj-dCcQjKj0jyLePfi6k1kAN_O5EfJAt0jqqBqPWLHf2mNuYmKRExj9pufKshiK5bx8r7nIKYrtYl6XjI8HYT39QbOh3X4.oGxh6px4apXBTTa0JLIjGe0_x5wUl3mn9V0jFMyBeuQ&dib_tag=se&keywords=gaming+keyboard&pd_rd_r=5b2dc48b-f75d-4903-867b-3831b638758f&pd_rd_w=AXY9J&pd_rd_wg=84UWx&pf_rd_p=12129333-2117-4490-9c17-6d31baf0582a&pf_rd_r=H94N0B3T6TRQQ53WHVS8&qid=1730845360&sr=8-4" # Get URL from user input
max_pagination = 2 # Get number of pages to paginate from user input

username_burner="login"
password_burner="password"
async def login_to_amazon(page, username: str, password: str):
    """Log in to Amazon using provided credentials."""
    print("Navigating to Amazon login page...")
    await page.goto("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fref%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")

    # Enter username
    await page.fill("input[name='email']", username)
    await page.click("input[type='submit']")  # Click on the continue button

    # Wait for password input to appear and enter password
    await page.wait_for_selector("input[name='password']", timeout=10000)
    await page.fill("input[name='password']", password)
    await page.click("input[type='submit']")  # Click on the sign-in button

    # Wait until redirected to the homepage to confirm login
    await page.wait_for_selector("a#nav-link-accountList", timeout=15000)
    print("Logged in to Amazon successfully.")


async def extract_data(amazon_reviews_ratings, page) -> list:

    # Initializing selectors and xpaths
    seemore_selector = "//div[@id='reviews-medley-footer']//a"
    div_selector = "[class='a-section celwidget']"
    next_page_selector = "[class='a-last']"
    name_xpath = "//a[@class='a-profile']//span[@class='a-profile-name']"
    #rate_xpath = "//a//i[contains(@class,'review-rating')]/span"
    review_title_xpath = "//a[contains(@class, 'review-title')]/span[2]"
    #review_date_xpath = "//span[contains(@class,'review-date')]"
    review_text_xpath = "[data-hook='review-body']"

    # Navigating to the review page
    review_page_locator = page.locator(seemore_selector)
    await review_page_locator.hover()
    await review_page_locator.click()

    # Paginating through each page
    for _ in range(max_pagination):
        # Waiting for the page to finish loading
        await page.wait_for_load_state("load")

        # Extracting the elements
        review_cards = page.locator(div_selector)
        cards_count = await review_cards.count()
        for index in range(cards_count):
            # Hovering the element to load the data
            inner_element = review_cards.nth(index=index)
            await inner_element.hover()

            # Extracting necessary data
            name = await inner_element.locator(name_xpath).inner_text() if await inner_element.locator(
                name_xpath).count() else None
            #rate = await inner_element.locator(rate_xpath).inner_text() if await inner_element.locator(
               # rate_xpath).count() else None
            review_title = await inner_element.locator(review_title_xpath).inner_text() if await inner_element.locator(
                review_title_xpath).count() else None
            #review_date = await inner_element.locator(review_date_xpath).inner_text() if await inner_element.locator(
                #review_date_xpath).count() else None
            review_text = await inner_element.locator(review_text_xpath).inner_text() if await inner_element.locator(
                review_text_xpath).count() else None

            # Removing extra spaces and unicode characters
            name = clean_data(name)
            #rate = clean_data(rate)
            review_title = clean_data(review_title)
            #review_date = clean_data(review_date)
            review_text = clean_data(review_text)

            data_to_save = {
                "reviewer_name": name,
                #"rate": rate,
                "review_title": review_title,
                #"review_date": review_date,
                "review_text": review_text
            }

            amazon_reviews_ratings.append(data_to_save)

        next_page_locator = page.locator(next_page_selector)

        # Check if the "Next Page" button exists
        if await next_page_locator.count() > 0:
            await next_page_locator.hover()
            await next_page_locator.click()
        else:
            break
    return amazon_reviews_ratings
    #save_data_to_csv(amazon_reviews_ratings, "Data.csv")


async def run(playwright, url) -> None:
    amazon_reviews_ratings = []
    while len(amazon_reviews_ratings) == 0:  # Initializing the browser and creating a new page
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_default_timeout(120000)

        # Get Amazon login credentials from the user
        # Log in to Amazon
        await login_to_amazon(page, username_burner, password_burner)

        # Navigate to the homepage
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_selector("//div[@id='reviews-medley-footer']//a", timeout=15000)
        # Extract data after logging in
        await extract_data(amazon_reviews_ratings, page)

        await context.close()
        await browser.close()


def clean_data(data):
    # Cleaning data by removing extra white spaces and Unicode characters.
    if not data:
        return None  # Return None if the data is empty or None
    cleaned_data = " ".join(data.split()).strip()
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")

    # Regular expression to check for at least one alphabetical character
    if re.search(r'[a-zA-Z]', cleaned_data):
        return cleaned_data  # Return the cleaned data if it contains letters
    return None  # Return None if it does not contain any letters


def save_data_to_csv(reviews_data: list, filename: str):
    # Defining the CSV header
    header = ["reviewer_name", "rate", "review_title", "review_date", "review_text"]

    # Writing to the CSV file
    with open(filename, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(reviews_data)


async def get_Reviews(url) -> None:
    async with async_playwright() as playwright:
        await run(playwright, url) # Start Playwright and run the main extraction logic

# Running the asyncio event loop to run the Playwright coroutine
asyncio.run(get_Reviews(url))
