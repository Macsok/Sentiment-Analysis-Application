import asyncio
import csv
from playwright.async_api import async_playwright

url = input("Give amazon url:") # Get URL from user input
max_pagination = int(input("Give number of pages:")) # Get number of pages to paginate from user input


async def extract_data(amazon_reviews_ratings, page) -> list:

    # Initializing selectors and xpaths
    seemore_selector = "//div[@id='reviews-medley-footer']//a"
    div_selector = "[class='a-section celwidget']"
    next_page_selector = "[class='a-last']"
    name_xpath = "//a[@class='a-profile']//span[@class='a-profile-name']"
    rate_xpath = "//a//i[contains(@class,'review-rating')]/span"
    review_title_xpath = "//a[contains(@class, 'review-title')]/span[2]"
    review_date_xpath = "//span[contains(@class,'review-date')]"
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
            rate = await inner_element.locator(rate_xpath).inner_text() if await inner_element.locator(
                rate_xpath).count() else None
            review_title = await inner_element.locator(review_title_xpath).inner_text() if await inner_element.locator(
                review_title_xpath).count() else None
            review_date = await inner_element.locator(review_date_xpath).inner_text() if await inner_element.locator(
                review_date_xpath).count() else None
            review_text = await inner_element.locator(review_text_xpath).inner_text() if await inner_element.locator(
                review_text_xpath).count() else None

            # Removing extra spaces and unicode characters
            name = clean_data(name)
            rate = clean_data(rate)
            review_title = clean_data(review_title)
            review_date = clean_data(review_date)
            review_text = clean_data(review_text)

            data_to_save = {
                "reviewer_name": name,
                "rate": rate,
                "review_title": review_title,
                "review_date": review_date,
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

    save_data_to_csv(amazon_reviews_ratings, "Data.csv")


async def run(playwright) -> None:
    amazon_reviews_ratings = []
    while len(amazon_reviews_ratings) == 0:# Initializing the browser and creating a new page
        browser = await playwright.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_default_timeout(120000)

    # Navigating to the homepage
        await page.goto(url, wait_until="domcontentloaded")
        await extract_data(amazon_reviews_ratings, page)

        await context.close()
        await browser.close()


def clean_data(data: str) -> str:
    if not data:
        return ""
    cleaned_data = " ".join(data.split()).strip()
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")
    return cleaned_data


def save_data_to_csv(reviews_data: list, filename: str):
    # Defining the CSV header
    header = ["reviewer_name", "rate", "review_title", "review_date", "review_text"]

    # Writing to the CSV file
    with open(filename, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(reviews_data)


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright) # Start Playwright and run the main extraction logic

# Running the asyncio event loop to run the Playwright coroutine
asyncio.run(main())
