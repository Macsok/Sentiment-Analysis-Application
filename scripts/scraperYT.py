import googleapiclient.discovery  # Import the Google API client library
import csv
import re  # Import the regular expressions module for data cleaning
from typing import List, Dict, Optional  # Import types for type annotations
import os  # Import the os module to handle file paths

# API_KEY = ''  # Initialize the API key as an empty string

def get_comments(video_id: str, api_key: str = '', max_pages: int = 2) -> List[Dict[str, str]]:
    """Fetch comments from a YouTube video using the YouTube Data API v3.

    Args:
        video_id (str): The ID of the YouTube video to fetch comments from.
        api_key (str): API key for authenticating with YouTube Data API.
        max_pages (int): The maximum number of pages of comments to retrieve.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing comment details.
    """
    # Initialize the YouTube API client using the provided API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # List to store comment data
    comments: List[Dict[str, str]] = []

    # Token for pagination; initially None for the first page
    page_token: Optional[str] = None

    # Loop to fetch multiple pages of comments, up to `max_pages`
    for _ in range(max_pages):
        # Create a request to the YouTube API to retrieve comment threads
        request = youtube.commentThreads().list(
            part="snippet",  # Retrieve only the "snippet" part of each comment
            videoId=video_id,  # Specify the video ID
            maxResults=100,  # Maximum number of comments per page (100)
            pageToken=page_token  # Token to fetch the next page
        )
        # Execute the request and get the response from YouTube API
        response = request.execute()

        # Process each item (comment) in the response
        for item in response['items']:
            # Extract the top-level comment's snippet containing details
            comment = item['snippet']['topLevelComment']['snippet']

            # Clean the comment text and check if it is non-empty
            cleaned_comment: Optional[str] = clean_data(comment['textOriginal'])
            if cleaned_comment:
                # Append a dictionary of the cleaned comment data to `comments` list
                comments.append({
                    'author': comment['authorDisplayName'],  # Comment author
                    'comment': cleaned_comment,  # Cleaned comment text
                })

        # Get the token for the next page of comments, if available
        page_token = response.get('nextPageToken')
        if not page_token:
            # Exit the loop if there are no more pages of comments
            break

    # Uncomment the line below to save the comments to a CSV file
    csv_file_path = os.path.join(os.path.dirname(__file__), '../web/comm/YT_replies.csv')
    # Ensure the CSV file is empty before writing new data to it
    with open(csv_file_path, 'w') as file: pass    
    save_comments_to_csv(comments, csv_file_path)
    return comments  # Return the list of comments


def clean_data(data: str) -> Optional[str]:
    """Clean the comment text by removing extra whitespace and non-ASCII characters.

    Args:
        data (str): The original comment text.

    Returns:
        Optional[str]: The cleaned comment text if it contains letters; otherwise, None.
    """
    # Return None if the data is empty or None
    if not data:
        return None

    # Remove extra spaces and trim the text
    cleaned_data: str = " ".join(data.split()).strip()

    # Remove non-ASCII characters by encoding to ASCII and decoding back to a string
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")

    # Check if the cleaned comment contains at least one alphabetical character
    if re.search(r'[a-zA-Z]', cleaned_data):
        return cleaned_data  # Return the cleaned text if it contains letters

    # Return None if the comment does not contain any letters
    return None


def save_comments_to_csv(comments: List[Dict[str, str]], filename: str) -> None:
    """Save comments to a CSV file.

    Args:
        comments (List[Dict[str, str]]): A list of dictionaries containing comment details.
        filename (str): The name of the CSV file to save comments to.
    """
    # Open the CSV file for writing with UTF-8 encoding
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Initialize a CSV writer with specified field names
        writer = csv.DictWriter(f, fieldnames=['author', 'comment'])

        # Write the header row to the CSV file
        writer.writeheader()

        # Write each comment in the `comments` list as a row in the CSV file
        writer.writerows(comments)


def scrap_and_save(video_id: str):
    """
    Scrapes comments from a YouTube video and saves them.

    Args:
        video_id (str): The ID of the YouTube video to scrape comments from.

    Returns:
        int: Returns 0 upon successful completion.
    """
    # global API_KEY
    # Read the API key from the file
    try:
        api_path = os.path.join(os.path.dirname(__file__), '../credentials/YT_API_KEY')
        with open(api_path) as file:
            API_KEY: str = file.read().strip()
    except FileNotFoundError:
        print("API key file not found! Please create a file named 'YT_API_KEY' in the 'credentials' directory.")
        API_KEY = input("Enter your YouTube Data API key: ").strip()

    # Extract the video ID from the URL
    start = video_id.find("watch?v=") + len("watch?v=")
    end = video_id.find("&ab_channel") if "&ab_channel" in video_id else len(video_id)
    id = video_id[start:end]
    print(f"Scraping comments for video ID: '{id}'")
    get_comments(id, API_KEY)
    return 0