from urllib.parse import urlencode
import requests

# API URL
API_URL = "https://buckets.grayhatwarfare.com/api/v2/files"

# Parse cookies
cookies_str = """
Cookie: REMEMBERME=QXBwXEVudGl0eVxVc2VyOk1HUmhlV055WlhjPToxNzMyMzc5MDY5OjBjZmZlYzU2YTQwNTk1ZjcyNmJmYjBhMWZjNDIxYTMxY2Y5MWJlMGI4MWJjMGQwMWU4ZDlkYmM4NDNlYjJjYmY%3D; __stripe_mid=af2965ba-4f1d-4bf0-a073-1aa7b3987d61ccd651; _gid=GA1.2.1818481707.1732197371; SFSESSID=ef1cskgeu6ha0e6v88msbec3ii; _ga=GA1.2.1930062620.1731774259; _gat_gtag_UA_121795267_1=1; _ga_QGK3VF4QHK=GS1.1.1732203206.13.1.1732203228.0.0.0
"""
cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies_str.strip().split('; ')}


def query_greyhat_api(keyword, extensions, start=0, limit=100):
    params = {
        "keywords": keyword,
        "extensions": ",".join(extensions),
        "start": start,
        "limit": limit
    }
    # URL encode the parameters
    encoded_params = urlencode(params)
    response = requests.get(f"{API_URL}?{encoded_params}", cookies=cookies)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def query_domain_with_extensions(domain, extensions):
    results = []
    start = 0
    while True:
        response = query_greyhat_api(domain, extensions, start=start)
        if not response or "files" not in response:
            break
        results.extend(response["files"])
        if len(response["files"]) < 100:
            break
        start += 100
    return results
