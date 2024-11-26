import requests

API_URL = "https://buckets.grayhatwarfare.com/api/v2/files"

def query_files(session_cookie, keywords, extensions, start=0, limit=1000):
    """
    Query the Greyhat API using a session cookie to fetch all files with pagination.
    """
    all_results = []  # Store all results across pages
    headers = {
        "Cookie": f"SFSESSID={session_cookie}"
    }
    while True:
        params = {
            "keywords": keywords,
            "extensions": ",".join(extensions),
            "start": start,
            "limit": limit
        }
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break
        
        data = response.json()
        if "files" not in data or not data["files"]:
            print("No more results.")
            break
        
        all_results.extend(data["files"])
        print(f"Fetched {len(data['files'])} files. Total so far: {len(all_results)}")
        
        # Check if there are fewer files than the limit, meaning it's the last page
        if len(data["files"]) < limit:
            break

        # Increment the start parameter to fetch the next page
        start += limit

    return all_results
