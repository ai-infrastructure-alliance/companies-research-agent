import os
from pyairtable import Table
import requests
from bs4 import BeautifulSoup

from utils import clean_url
from urllib.parse import urljoin

from dotenv import load_dotenv

load_dotenv()
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
BASE_ID = 'appvOnl6DnnKj8fVM'
TABLE_NAME = 'Automagic 2'

FILENAME = 'sources/Jon-June.html'

target_table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)


def find_all_links_at_url(url):
  headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
  }
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    page_content = response.text
    soup = BeautifulSoup(page_content, "html.parser")
    raw_links = [a["href"] for a in soup.find_all("a", href=True)]
    absolute_links = [urljoin(url, x) for x in raw_links]
    return absolute_links
  else:
    print(f"Failed to load {url}, status code: {response.status_code}")
    return []


def find_all_link_in_html(filename):
  with open(filename, "r") as f:
    page_content = f.read()
    soup = BeautifulSoup(page_content, "html.parser")
    raw_links = [a["href"] for a in soup.find_all("a", href=True)]
    return raw_links


new_urls = find_all_link_in_html(FILENAME)
print(f"The page contains {len(new_urls)} links.")
amount = len(new_urls)

added = 0
skipped = 0

for new_url in new_urls:
  print(f"Processing {added + skipped + 1} of {amount} found URLs.")

  try:
    url = clean_url(new_url)
    old_rows = target_table.all()
    old_urls = set([row['fields']['URL'] for row in old_rows])

    if url not in old_urls:
      print(f"Adding {url}")
      target_table.create({'URL': url})
      added += 1
    else:
      print(f"Skipping {url}")
      skipped += 1
  except Exception as e:
    print(f"Error while processing {new_url}: {e}")
    skipped += 1

print(f"Added {added} URLs")
print(f"Skipped {skipped} URLs")
