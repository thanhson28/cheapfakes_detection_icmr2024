from google.oauth2 import service_account
from googleapiclient.discovery import build
from selenium_image_searcher import *

# Service account credentials
credentials = service_account.Credentials.from_service_account_file(
    "/home/peter/Documents/repositories/cheapfakes_detection_icmr2024/visualsearch-419810-180105447981.json",
    scopes=["https://www.googleapis.com/auth/drive.readonly"],
)

# Build the Drive service
service = build("drive", "v3", credentials=credentials)


# get name of all files of folder A on google drive
def get_folder_contents(folder_id):
    results = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents",
            fields="nextPageToken, files(id, name)",
            pageSize=1000,
        )
        .execute()
    )
    items = results.get("files", [])
    return items


# print(get_folder_contents('1iE6gdC33ivzw7DjdbwUJVmvqwnh9Gxod'))
def get_name_of_image(file_id):
    # Retrieve the file metadata
    file_metadata = service.files().get(fileId=file_id).execute()
    # Get the filename
    filename = file_metadata['name']
    return filename

# get raw url of image from google drive
def get_link_of_image(file_id):
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"

image_paths = get_folder_contents("1iE6gdC33ivzw7DjdbwUJVmvqwnh9Gxod")
image_urls = {}
for image in image_paths:
    image_path = get_link_of_image(image["id"])
    image_name = get_name_of_image(image["id"])
    # print(image_path)
    print(f"Visual Searching for {image_name}")
    pyperclip.copy(image_path)
    results = get_image_urls(image_path)

    if results:
        print(f"Found {len(results)} image URLs:")
        image_urls[image_name] = results
    else:
        print("No image URLs found.")
        image_urls[image_name] = []

    with open('image_urls.json', 'w') as f:
        json.dump(image_urls, f)