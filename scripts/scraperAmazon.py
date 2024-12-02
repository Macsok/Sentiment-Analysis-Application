import asyncio
import csv
from playwright.async_api import async_playwright
import re
import os

username_burner = ''
password_burner = ''
# Prompt the user to input the Amazon product URL for review extraction
# url = input("Enter the Amazon product URL: ")
max_pagination = 8  # Set the maximum number of review pages to paginate through

# Function to log in to Amazon using Playwright
async def login_to_amazon(page, username: str, password: str) -> None:
    """
    Logs in to Amazon using provided credentials.

    Args:
        page (Page): The Playwright page instance.
        username (str): The username/email for Amazon login.
        password (str): The password for Amazon login.

    Returns:
        None
    """
    # Navigate to the Amazon login page
    print("Navigating to Amazon login page...")
    await page.goto("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2FRedragon-S101-Keyboard-Ergonomic-Programmable%2Fdp%2FB00NLZUM36%2Fref%3Dnav_signin%3F_encoding%3DUTF8%26content-id%3Damzn1.sym.12129333-2117-4490-9c17-6d31baf0582a%26dib%3DeyJ2IjoiMSJ9.5IlsBDmYkV0cxr2kcvPErft4Zv50KQZF5msSYapyt3-c0aoK8Q2jW8E_B7jXwd9x0R-F0asV2u_xofM5o-OfsbhoVydlcgErNYZxAEXAM2uFJnF5ytQ1Q2LmwHg1NtZQh9tTmflAoXOvgcbe7sbMGOC1kIokWeNfIqacEuq_Q0FRaz_WHyPVXzZsFL2VzLNARFxBf-LbJPBbQYzUv0kUUm6gQH7rwSkPrBdYbaP1DdY.2KsNSHAbwPIFRafc3J20nBUW_t2aXVcu7BCdnx3npzU%26dib_tag%3Dse%26keywords%3Dgaming%252Bkeyboard%26pd_rd_r%3D5b2dc48b-f75d-4903-867b-3831b638758f%26pd_rd_w%3DAXY9J%26pd_rd_wg%3D84UWx%26pf_rd_p%3D12129333-2117-4490-9c17-6d31baf0582a%26pf_rd_r%3DH94N0B3T6TRQQ53WHVS8%26qid%3D1731965745%26sr%3D8-1%26th%3D1&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")

    # Enter the username and submit
    await page.fill("input[name='email']", username)
    await page.click("input[type='submit']")

    # Wait for the password input field, enter the password, and submit
    await page.wait_for_selector("input[name='password']", timeout=10000)
    await page.fill("input[name='password']", password)
    await page.click("input[type='submit']")

    # Confirm successful login by waiting for an account-related element to appear
    await page.wait_for_selector("a#nav-link-accountList", timeout=15000)
    print("Logged in to Amazon successfully.")

# Function to extract review data from the product's review section
async def extract_data(amazon_reviews_ratings, page) -> list:
    """
    Extracts reviews and associated data from an Amazon product page.

    Args:
        amazon_reviews_ratings (list): A list to store review data.
        page (Page): The Playwright page instance.

    Returns:
        list: A list of dictionaries containing review information.
    """
    # Define the selectors and xpaths for elements needed to extract review data
    seemore_selector = "//div[@id='reviews-medley-footer']//a"  # "See all reviews" button
    div_selector = "[class='a-section celwidget']"  # Each review card
    next_page_selector = "[class='a-last']"  # Button to go to the next review page
    name_xpath = "//a[@class='a-profile']//span[@class='a-profile-name']"  # Reviewer's name
    review_title_xpath = "//a[contains(@class, 'review-title')]/span[2]"  # Review title
    review_text_xpath = "[data-hook='review-body']"  # Review body text

    # Click the "See all reviews" button to navigate to the full reviews page
    await page.locator(seemore_selector).click()

    # Loop through pages of reviews, limited by max_pagination
    for i in range(max_pagination):
        print(f'Doing page {i}')
        await page.wait_for_load_state("load")  # Wait until page is fully loaded

        # Locate review cards and get the total number of reviews on the current page
        review_cards = page.locator(div_selector)
        cards_count = await review_cards.count()
        print(f'cards count: {cards_count}')

        # Loop through each review card to extract data
        for index in range(cards_count):
            review = review_cards.nth(index)
            await review.hover()  # Hover over review to load content if needed

            # Attempt to extract reviewer's name, title, and review text, if available
            name = await review.locator(name_xpath).inner_text() if await review.locator(name_xpath).count() else None
            review_title = await review.locator(review_title_xpath).inner_text() if await review.locator(review_title_xpath).count() else None
            review_text = await review.locator(review_text_xpath).inner_text() if await review.locator(review_text_xpath).count() else None

            # Clean the extracted data to remove unwanted characters and whitespace
            name = clean_data(name)
            review_title = clean_data(review_title)
            review_text = clean_data(review_text)

            # Store the cleaned data in a dictionary format
            data_to_save = {
                "author": name,
                "title": review_title,
                "comment": review_text
            }
            amazon_reviews_ratings.append(data_to_save)  # Add review data to the main list

        # Check if there's a "Next" button to go to the next page of reviews
        next_page = page.locator(next_page_selector)
        if await next_page.count() > 0:
            await next_page.click()
        else:
            break  # Stop if there are no more pages
        print('Done with page') 
    
    print('Done extracting reviews!')
    return amazon_reviews_ratings

# Function to initialize browser, log in to Amazon, and extract review data
async def run(playwright, url) -> None:
    """
    Initializes the browser, logs in to Amazon, extracts reviews, and saves them.

    Args:
        playwright (Playwright): The Playwright instance.
        url (str): The URL of the Amazon product page.

    Returns:
        None
    """
    amazon_reviews_ratings = []  # Initialize a list to hold all review data

    # Retry loop to handle cases where no reviews are extracted initially
    while len(amazon_reviews_ratings) == 0:
        # Launch a headless Firefox browser and create a new browser context
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Set viewport size to standard desktop resolution
        await page.set_viewport_size({"width": 1920, "height": 1080})

        # Log in to Amazon and navigate to the product page URL
        await login_to_amazon(page, username_burner, password_burner)
        print(f"Extracting reviews...")
        await page.goto(url)

        # Extract reviews and save them to CSV
        await extract_data(amazon_reviews_ratings, page)

        csv_file_path = os.path.join(os.path.dirname(__file__), '../web/comm/Amazon_replies.csv')
        # Ensure the CSV file is empty before writing new data to it
        with open(csv_file_path, 'w') as file: pass    
        save_data_to_csv(amazon_reviews_ratings, csv_file_path)

        # Close the browser context and browser after completion
        await context.close()
        await browser.close()


# Function to clean extracted text by removing whitespace and non-ASCII characters
def clean_data(data) -> str|None:
    """
    Cleans text by removing excess whitespace and non-ASCII characters.

    Args:
        data (str): The text to be cleaned.

    Returns:
        str or None: The cleaned text, or None if the result is empty or invalid.
    """
    if not data:
        return None  # Return None if input is empty or None
    # Remove excess whitespace and non-ASCII characters
    cleaned_data = " ".join(data.split()).strip()
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")
    return cleaned_data if re.search(r'[a-zA-Z]', cleaned_data) else None  # Return cleaned text or None if invalid

# Function to save extracted review data to a CSV file
def save_data_to_csv(reviews_data: list, filename: str) -> None:
    """
    Saves extracted review data to a CSV file.

    Args:
        reviews_data (list): A list of dictionaries containing review information.
        filename (str): The name of the file to save the data.

    Returns:
        None
    """
    header = ["author", "title", "comment"]  # Define CSV headers for data fields
    with open(filename, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(reviews_data)  # Write each review's data to the CSV

# Main entry function to run Playwright and start the review extraction
async def get_reviews(url) -> None:
    """
    Main entry point to start Playwright and extract Amazon reviews.

    Args:
        url (str): The URL of the Amazon product page.

    Returns:
        None
    """
    global username_burner, password_burner
    # Load credentials from file
    credentials_file = os.path.join(os.path.dirname(__file__), '../credentials/AMAZON')
    with open(credentials_file, 'r') as file:
        username_burner = file.readline().strip()
        password_burner = file.readline().strip()
        print(f'Signed in as {username_burner}')

    async with async_playwright() as playwright:
        await run(playwright, url)  # Call the main function to run extraction

# Run the asynchronous review extraction process
# asyncio.run(get_reviews(str(url)))