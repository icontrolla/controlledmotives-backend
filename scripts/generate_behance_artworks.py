import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_behance_profile(username):
    print(f"🔍 Scraping {username}...")
    url = f"https://www.behance.net/{username}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    artworks = []

    for project in soup.select('a.ProjectCoverNeue-link'):
        title = project.get('aria-label', 'Untitled Project')
        href = project['href']
        full_url = f"https://www.behance.net{href}"
        img_tag = project.select_one('img')
        img_url = img_tag['src'] if img_tag else ''

        artworks.append({
            "title": title.strip(),
            "image": img_url,
            "artist": username,
            "url": full_url,
            "tags": [],
            "category": "Uncategorized"
        })

    print(f"✅ Found {len(artworks)} artworks from {username}")
    return artworks


if __name__ == "__main__":
    usernames = [
        "ashthorp",
        "gydiant",
        "alexeyegorov",
        "vasjenkatro",
        "muratpak",
        "travisleighmartin",
        "beeple",
        "gavinshapiro",
        "antonioescalona",
        "malikafavre",
        "leandroassis",
        "ignasi",
        "foreal",
        "markusmagnusson"
    ]

    all_artworks = []
    for username in usernames:
        artworks = scrape_behance_profile(username)
        all_artworks.extend(artworks)
        time.sleep(1.5)

    with open("behance_artworks.json", "w") as f:
        json.dump(all_artworks, f, indent=2)

    print(f"\n🎉 Exported {len(all_artworks)} total artworks to behance_artworks.json")
