import asyncio
import csv
from playwright.async_api import async_playwright, TimeoutError
import re
import os

username = ''
password = ''
email = ''

async def login_to_x(page, username: str, password: str):
    """
    Logs in to X.com using the provided credentials.

    Args:
        page: Playwright's page object for the browser.
        username (str): Username for login.
        password (str): Password for login.
    """

    username_section = "input[name='text']"
    password_section = "input[name='password']"

    print("Navigating to login page...")
    await page.goto("https://x.com/login")
    await page.fill(username_section, username)
    await page.press(username_section, "Enter")

    # Retry filling the username in case of an additional prompt
    try:
        await page.wait_for_selector("input[name='text']", timeout=2500)
        await page.fill(username_section, username)
        await page.press(username_section, "Enter")
    except TimeoutError:
        print("No second username prompt.")

    try:
        await page.wait_for_selector("input[name='text']", timeout=2500)
        await page.fill(username_section, email)
        await page.press(username_section, "Enter")
    except TimeoutError:
        print("No second username prompt.")
    # Enter the password and continue
    await page.wait_for_selector("input[name='password']", timeout=2500)
    await page.fill(password_section, password)
    await page.press(password_section, "Enter")

    # Wait for the homepage to load after logging in
    await page.wait_for_selector("a[data-testid='AppTabBar_Home_Link']", timeout=15000)
    print("Logged in successfully.")


async def extract_replies(replies_data, page, max_replies=150):
    """
    Extracts replies from a specific post on X.com. Returns list of retrieved replies in cvs format, each entry has username and a text of the reply.

    Args:
        replies_data (list): List of replies to populate.
        page: Playwright's page object for the browser.
        max_replies (int): Maximum number of replies to retrieve.

    Returns:
        list: Updated list of replies.
    """
    #replay_selector-used to find all replies, text_selector-used to exctract reply text, username_selector-used to exctract username form reply
    reply_selector = "[data-testid='tweet'][tabindex='0']" #Each reply card
    text_selector = "div[data-testid='tweetText'] span" #Reply body text
    username_selector = "div[data-testid='User-Name'] span span" #Username of the one replying

    #waits for the page to fully load, The "domcontentloaded" event in web terms means that the HTML document has been completely loaded and parsed
    await page.wait_for_load_state("domcontentloaded")
    #waits for the reply elements have been rendered on the page
    await page.wait_for_selector(reply_selector)

    loaded_replies_count = 0

    # Retrieve replies, scrolling down as needed to reach the desired count
    while loaded_replies_count < max_replies:
        # Locate all reply elements on the page based on the reply_selector CSS selector
        reply_cards = page.locator(reply_selector)
        replies_count = await reply_cards.count()  # Count the number of replies currently loaded

        # Process each reply card on the page
        for index in range(replies_count):
            # Select the specific reply at the current index
            reply = reply_cards.nth(index)

            # Extract all text spans within the reply (since each tweet or reply can have multiple spans of text)
            reply_texts = await reply.locator(text_selector).all_inner_texts()
            reply_text = " ".join(reply_texts) if reply_texts else None  # Join spans into a single string, if present

            # Extract the username of the user who posted this reply
            usernames = await reply.locator(username_selector).all_inner_texts()
            username = usernames[0] if usernames else None  # Use the first username if available

            # Clean up the reply text and username by removing unnecessary whitespace and non-ASCII characters
            reply_text = clean_data(reply_text)
            username = clean_data(username)

            # Add the reply to the list if both the reply text and username are valid, and if this reply text is unique
            if reply_text and username and reply_text not in [reply["comment"] for reply in replies_data]:
                data_to_save = {
                    "author": username,
                    "comment": reply_text,
                }
                replies_data.append(data_to_save)  # Add to the list of collected replies
                loaded_replies_count += 1  # Increment the count of loaded replies

                # If we have collected the maximum desired replies, stop processing
                if loaded_replies_count >= max_replies:
                    break

        # Scroll down to load more replies, assuming more are dynamically loaded as we scroll
        await page.mouse.wheel(0, 150000)  # Scroll down by simulating mouse wheel movement
        await page.wait_for_timeout(10000)  # Wait 5 seconds to give time for new replies to load

        # Check if new replies have loaded by recounting the reply elements
        new_replies_count = await page.locator(reply_selector).count()
        if new_replies_count <= replies_count:
            await page.mouse.wheel(0, 150000)  # Scroll down by simulating mouse wheel movement
            await page.wait_for_timeout(10000)
            new_replies_count = await page.locator(reply_selector).count()
            if new_replies_count <= replies_count:
                await page.mouse.wheel(0, 150000)  # Scroll down by simulating mouse wheel movement
                await page.wait_for_timeout(10000)
                new_replies_count = await page.locator(reply_selector).count()
                # If no new replies were loaded (count has not increased), break the loop to stop scrolling
                if new_replies_count <= replies_count:
                    break

    # Return the list of collected replies after reaching the desired count or running out of new replies
    return replies_data


async def run(playwright, url) -> list:
    """
    Launches the browser, logs in to X.com, and retrieves replies from a specific post.

    Args:
        playwright: Playwright object.
        url (str): URL of the post to analyze.

    Returns:
        list: List of replies from the post.
    """
    replies_data = []  # Initialize an empty list to store replies

    # Keep attempting to gather replies until at least one reply is successfully extracted
    while len(replies_data) == 0:
        # Launch a new Chromium browser instance (headless=False to show the browser window)
        browser = await playwright.chromium.launch(headless=True)

        # Create a new browser context
        context = await browser.new_context()

        # Open a new page/tab within the created context
        page = await context.new_page()

        # Set the size of the browser window to a standard desktop resolution
        await page.set_viewport_size({"width": 1920, "height": 1080})

        # Set a default timeout of 120 seconds for page actions
        page.set_default_timeout(120000)

        # Log in to X.com using the provided credentials
        await login_to_x(page, username, password)

        # Navigate to the specified URL (the post to analyze) and wait until the main content is loaded
        await page.goto(url, wait_until="domcontentloaded")

        # Extract replies and save them to CSV
        await extract_replies(replies_data, page)
        print(len(replies_data))
        csv_file_path = os.path.join(os.path.dirname(__file__), '../web/comm/X_replies.csv')
        # Ensure the CSV file is empty before writing new data to it
        with open(csv_file_path, 'w') as file: pass    
        save_data_to_csv(replies_data, csv_file_path)

        # Close both the browser context and browser session to clear session data and isolate state
        await context.close()
        await browser.close()




def clean_data(data):
    """
    Cleans text by removing excess whitespace and non-ASCII characters.

    Args:
        data (str): The text to be cleaned.

    Returns:
        str or None: The cleaned text, or None if the result is empty or invalid.
    """
    if not data:
        return None  # Return None if data is empty or None
    # Remove extra whitespace and strip leading/trailing whitespace
    cleaned_data = " ".join(data.split()).strip()

    # Remove non-ASCII characters by encoding to ASCII and ignoring any non-ASCII bytes
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")

    # Check if the cleaned data contains at least one alphabetic character; return cleaned data if valid
    if re.search(r'[a-zA-Z]', cleaned_data):
        return cleaned_data

    return None  # Return None if the cleaned data is empty or contains no letters


def save_data_to_csv(replies_data: list, filename: str):
    """
    Saves the extracted replies to a CSV file for easy viewing and analysis.

    Args:
        replies_data (list): A list of dictionaries, each containing 'username' and 'reply_text' keys.
        filename (str): The desired filename for the CSV output.
    """
    header = ["author", "comment"]  # Define the CSV headers

    # Open the specified file for writing, with UTF-8 encoding to handle special characters
    with open(filename, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)  # Initialize the CSV writer
        writer.writeheader()  # Write the header row
        writer.writerows(replies_data)  # Write each reply as a new row in the CSV


async def get_replies(url) -> list:
    """
    Main function to initialize Playwright, log in, and retrieve replies from a specified post URL.

    Args:
        url (str): The URL of the post on X.com from which to extract replies.

    Returns:
        None
    """
    async with async_playwright() as playwright:
        # Run the process using Playwright and retrieve replies data
        return await run(playwright, url)


def scrap_and_save(url: str):
    """
    Scrapes replies from the given URL on X.com and saves the results to a CSV file.

    Args:
        url (str): The URL of the post to scrape replies from.

    Returns:
        int: Returns 0 upon successful completion.
    """
    global username, password, email
    # Load credentials from file
    credentials_file = os.path.join(os.path.dirname(__file__), '../credentials/X')
    try:
        with open(credentials_file, 'r') as file:
            username = file.readline().strip()
            password = file.readline().strip()
            email = file.readline().strip()
            print(f'Signed in as {username}')
    except FileNotFoundError:
        print("Credentials file not found. Please ensure the file exists and contains valid credentials.")
        exit(1)
    print('Starting...')
    asyncio.run(get_replies(url))
    return 0