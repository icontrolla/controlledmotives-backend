from django.core.management.base import BaseCommand
import time
import os
import boto3
from botocore.client import Config
import json
import requests
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = "Scrape Behance artists and upload JSON to Backblaze B2"

    def scrape_behance_profile(self, username):
        # Your scraping code here, same as before
        url = f"https://www.behance.net/{username}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch {url}"))
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
        self.stdout.write(self.style.SUCCESS(f"Found {len(artworks)} artworks from {username}"))
        return artworks

    def upload_json_to_b2_s3(self, data, bucket_name, file_name):
        s3 = boto3.resource(
            's3',
            endpoint_url=os.getenv('AWS_S3_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4'),
            region_name=os.getenv('AWS_S3_REGION_NAME')
        )
        json_str = json.dumps(data, indent=2)
        s3.Object(bucket_name, file_name).put(Body=json_str, ContentType='application/json')
        self.stdout.write(self.style.SUCCESS(f"Uploaded {file_name} to bucket {bucket_name}"))

    def handle(self, *args, **options):
        usernames = [
            "ashthorp", "gydiant", "alexeyegorov", "vasjenkatro",
            "muratpak", "travisleighmartin", "beeple", "gavinshapiro",
            "antonioescalona", "malikafavre", "leandroassis",
            "ignasi", "foreal", "markusmagnusson"
        ]

        all_artworks = []
        for username in usernames:
            artworks = self.scrape_behance_profile(username)
            all_artworks.extend(artworks)
            time.sleep(1.5)

        self.upload_json_to_b2_s3(
            all_artworks,
            os.getenv('AWS_STORAGE_BUCKET_NAME'),
            'behance_artworks.json'
        )
