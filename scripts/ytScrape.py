import googleapiclient.discovery
import csv


API_KEY = 'AIzaSyA-MaUCPX-ugyc4hTP8OHW-_dpN9k42KFk'  # API key for Youtube Data API v3
VIDEO_ID = 'dQw4w9WgXcQ'  # yt video ID


def get_comments(video_id, api_key, max_pages=5):
    """Function to fetch comments from a YouTube video using the API."""

    # Build the YouTube API client
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    comments = []  # Initialize an empty list to store comments
    page_token = None  # Initialize page token for pagination

    for _ in range(max_pages):  # Iterate through the specified number of pages
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,  # Max amount of comments per page
            pageToken=page_token
        )
        response = request.execute()  # Execute the API request and get the response

        for item in response['items']:  # Iterate through the comments in the response
            comment = item['snippet']['topLevelComment']['snippet']
            cleaned_comment = clean_data(comment['textOriginal'])  # Clean the comment text
            if cleaned_comment:  # Only add non-empty comments
                comments.append({
                    'author': comment['authorDisplayName'],
                    'comment': cleaned_comment,
                    'like_count': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })

        # Proceed to the next page of comments, if available
        page_token = response.get('nextPageToken')
        if not page_token:
            break  # Exit the loop if there are no more pages

    save_comments_to_csv(comments)  # Save the comments to a CSV file


def clean_data(data):
    #Cleaning data by removing extra white spaces and Unicode characters.
    if not data:
        return ""
    cleaned_data = " ".join(data.split()).strip()
    cleaned_data = cleaned_data.encode("ascii", "ignore").decode("ascii")
    return cleaned_data

def save_comments_to_csv(comments, filename="youtube_comments.csv"):
    #Saving comments to csv file, by default youtube_comments.csv
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        #Initializing field names for csv file
        writer = csv.DictWriter(f, fieldnames=['author', 'comment', 'like_count', 'published_at'])
        writer.writeheader()
        writer.writerows(comments)

get_comments(VIDEO_ID, API_KEY)


