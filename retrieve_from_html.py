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
TABLE_NAME = 'Source 6'

FILENAME = 'sources/Ben-June.html'

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


def step_1():
  # STEP 1: Add all new URLs to the table
  new_urls = find_all_link_in_html(FILENAME)
  print(f"The page contains {len(new_urls)} links.")
  for new_url in new_urls:
    target_table.create({'Raw URL': new_url})
    print(f"Added {new_url} to the table.")

def step_2():
  # STEP 2: Process all new URLs
  new_urls_rows = target_table.all()
  limit = 20
  processsing = 0
  n = 0
  for row in new_urls_rows:
    n += 1
    print(f"Processing {n} of {len(new_urls_rows)} URLs.")
    try:
      status = row['fields']['Status']
      if status and status == 'New':
        raw_url = row['fields']['Raw URL']
        if processsing >= limit:
          print(f"Reached limit of {limit} URLs processed.")
          break
        processsing += 1
        cleaned_url = clean_url(raw_url)
        target_table.update(row['id'], {'URL': cleaned_url, 'Status': 'Processed'})
      else:
        print(f"Skipping {row['fields']['Raw URL']} because it is not new.")
    except Exception as e:
      print(f"Error while processing {row['fields']['Raw URL']}: {e}")
      target_table.update(row['id'], {'Status': 'Error'})

# step_1()
step_2()