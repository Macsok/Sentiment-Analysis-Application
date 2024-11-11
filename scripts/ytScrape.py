import googleapiclient.discovery  # Import the Google API client library
import csv  
import re  # Import the regular expressions module for data cleaning

API_KEY = 'API_KEY'  # Your API key for YouTube Data API v3
VIDEO_ID = 'dQw4w9WgXcQ'  # The YouTube video ID you want to retrieve comments from


def get_comments(video_id, api_key=API_KEY, max_pages=5):
    """Fetch comments from a YouTube video using the YouTube Data API v3.

    Args:
        video_id (str): The ID of the YouTube video to fetch comments from.
        api_key (str): API key for authenticating with YouTube Data API.
        max_pages (int): The maximum number of pages of comments to retrieve.

    Returns:
        list: A list of dictionaries containing comment details.
    """
    # Initialize the YouTube API client using the provided API key
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # List to store comment data
    comments = []

    # Token for pagination; initially None for the first page
    page_token = None

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
            cleaned_comment = clean_data(comment['textOriginal'])
            if cleaned_comment:
                # Append a dictionary of the cleaned comment data to `comments` list
                comments.append({
                    'author': comment['authorDisplayName'],  # Comment author
                    'comment': cleaned_comment,  # Cleaned comment text
                    'like_count': comment['likeCount'],  # Number of likes on the comment
                    'published_at': comment['publishedAt']  # Comment's publication date
                })

        # Get the token for the next page of comments, if available
        page_token = response.get('nextPageToken')
        if not page_token:
            # Exit the loop if there are no more pages of comments
            break

    # Uncomment the line below to save the comments to a CSV file
    # save_comments_to_csv(comments)
    return comments  # Return the list of comments


def clean_data(data):
    """Clean the comment text by removing extra whitespace and non-ASCII characters.

    Args:
        data (str): The original comment text.

    Returns:
        str or None: The cleaned comment text if it contains letters; otherwise, None.
    """
    # Return None if the data is empty or None
    if not data:
        return None

    # Remove extra spaces and trim the text
    cleaned_data = " ".join(data.split()).strip()

    # Remove non-ASCII characters by encoding to ASCII and decoding back to a string
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")

    # Check if the cleaned comment contains at least one alphabetical character
    if re.search(r'[a-zA-Z]', cleaned_data):
        return cleaned_data  # Return the cleaned text if it contains letters

    # Return None if the comment does not contain any letters
    return None


def save_comments_to_csv(comments, filename="youtube_comments.csv"):
    """Save comments to a CSV file.

    Args:
        comments (list): A list of dictionaries containing comment details.
        filename (str): The name of the CSV file to save comments to.
    """
    # Open the CSV file for writing with UTF-8 encoding
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Initialize a CSV writer with specified field names
        writer = csv.DictWriter(f, fieldnames=['author', 'comment', 'like_count', 'published_at'])

        # Write the header row to the CSV file
        writer.writeheader()

        # Write each comment in the `comments` list as a row in the CSV file
        writer.writerows(comments)


# Example usage
# get_comments(VIDEO_ID, API_KEY)
