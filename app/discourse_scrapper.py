import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
from tqdm import tqdm 

# 1. CONFIGURATION
COOKIE = "_gcl_au=1.1.2028158730.1746812117; _ga=GA1.1.163919697.1746812117; _fbp=fb.2.1746812117453.327612350139265662; _ga_5HTJMW67XK=GS2.1.s1749121202$o39$g0$t1749121307$j60$l0$h0; _ga_08NPRH5L4M=GS2.1.s1749121201$o54$g1$t1749121371$j60$l0$h0; _t=zbaDR5IlaYJHr3KS3DbZiwAMS5ONzKfOED4VJAQ6lLZ2fpOEksZzsZVVPnoHloGvqdYeJYxdg4S37ew2TWVrNg3zGWTPpZREDhmbcES%2FkdaI10EHN1cwhHDKCZ%2Fp1imzlBIPrauVq%2Bb73oanwkTrWzdO4wfu4kc4wF8tG2U4dZquSPTgsIsX38rm11ZhJjCzqyWq9sJdfOjPVl6rDIfxM0rQpYHtq6GQ7xjlixdQbcz5Ddtq2yXx4fZWP8kybb%2BLCkVtgjFUu1%2Bmvb3bokju5K5vOdNsFaNcLklq6j7xnpQODH0CZw6%2F79KmJJciuM79fs94ng%3D%3D--P1jhV%2BIDqsnLPXng--AKzs93JNhpDqCl4rJ4NZPA%3D%3D; _bypass_cache=true; _forum_session=jJ6Ivc9JPE%2FCva0DXfO%2BZ%2FDR7zXod%2FVxdW4iwd2EG1cDZmpZLMCHmwWyWO95s4HVrZpoKaAtXr16%2Fr3w2YuZYag2DNBszreaWI3G7sLNK3q5zhb2gb9Rd5Ijz14aHOAFOsrtqwkA8zUIB%2F4WIHyjUt3GXRJcCR%2FlDTZLLX%2BheCqpUt6E7u6JNsBlZqh8mJJrNPZieC%2FolBgX9yWU6NHCB4cWd7UPMPj7TeIihoi7v8Kudo7flhIB8RKATN2h5Es40lUmOI5Gc8WGTY94DEcSSSlIq1kwvoybEVwQO8rGr6dNDL8f7ofzfB9VehIM6YCU8H%2BCsWum9FOqeOh3iL0LrVPXdoi3ftuE3TAkfxQCtP8Q4yxcwV7EhtgLEYGLmg%3D%3D--rI8pB4jwCcLOfTF0--2rKv1OkQT1jlChUIdDunrA%3D%3D"  # paste your _t + _forum_session string here

HEADERS = {
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0"
}
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"

CATEGORY_ID = 34  # TDS category
DATE_FROM = datetime(2025, 1, 1)
DATE_TO = datetime(2025, 4, 14)

output = []

# 2. FETCH TOPICS
def get_all_topics():
    page = 0
    topics = []

    print("📥 Fetching topics from Discourse...")
    while True:
        url = f"{BASE_URL}/c/courses/tds-kb/{CATEGORY_ID}.json?page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"⚠️  Error fetching page {page}: {resp.status_code}")
            break

        data = resp.json()
        new_topics = data.get("topic_list", {}).get("topics", [])
        if not new_topics:
            break

        print(f"✅ Page {page}: {len(new_topics)} topics")
        topics.extend(new_topics)
        page += 1
        time.sleep(1)  # avoid rate limiting

    print(f"🎯 Total topics fetched: {len(topics)}")
    return topics

# 3. FETCH POSTS FROM TOPIC
def fetch_topic_posts(topic):
    topic_id = topic["id"]
    slug = topic["slug"]
    url = f"{BASE_URL}/t/{slug}/{topic_id}.json"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"⚠️  Failed to fetch topic {topic_id}: {resp.status_code}")
        return []

    topic_data = resp.json()
    posts = topic_data["post_stream"]["posts"]

    filtered_posts = []
    for post in posts:
        created = datetime.strptime(post["created_at"][:10], "%Y-%m-%d")
        if DATE_FROM <= created <= DATE_TO:
            text = BeautifulSoup(post["cooked"], "html.parser").get_text()
            filtered_posts.append({
                "topic_id": topic_id,
                "slug": slug,
                "url": f"{BASE_URL}/t/{slug}/{topic_id}/{post['post_number']}",
                "username": post["username"],
                "created_at": post["created_at"],
                "text": text
            })

    return filtered_posts

# 4. RUN
if __name__ == "__main__":
    all_topics = get_all_topics()

    print("\n🔍 Fetching posts from each topic...")
    for topic in tqdm(all_topics, desc="Processing topics"):
        posts = fetch_topic_posts(topic)
        output.extend(posts)
        time.sleep(1)  # be nice to the server

    with open("/home/siddharth/TDS-Virtual-Teaching-Assistant/rawdata/discourse_contents/discourse-posts.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Saved {len(output)} filtered posts to discourse-posts.json ✅")
