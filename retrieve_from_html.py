import os
from pyairtable import Table
from bs4 import BeautifulSoup
from utils import clean_url

from dotenv import load_dotenv
load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('BASE_ID')

TARGET_TABLE_NAME = 'Source'
FILENAME = 'sources/links.html'

# Limit the amount of URLs processed on one run, because each processing 
# takes a long time and requires a lot of resources.
LIMIT=20

target_table = Table(AIRTABLE_API_KEY, BASE_ID, TARGET_TABLE_NAME)

def find_all_link_in_html(filename):
  with open(filename, "r") as f:
    page_content = f.read()
    soup = BeautifulSoup(page_content, "html.parser")
    raw_links = [a["href"] for a in soup.find_all("a", href=True)]
    return raw_links

# STEP 1: Add all new URLs to the table
def step_1():
  new_urls = find_all_link_in_html(FILENAME)
  print(f"The page contains {len(new_urls)} links.")
  for new_url in new_urls:
    target_table.create({'Raw URL': new_url})
    print(f"Added {new_url} to the table.")

# STEP 2: Process all new URLs (render JS, remove query params, etc.)
def step_2():
  new_urls_rows = target_table.all()
  processsing = 0
  n = 0
  for row in new_urls_rows:
    n += 1
    print(f"Processing {n} of {len(new_urls_rows)} URLs.")
    try:
      status = row['fields']['Status']
      if status and status == 'New':
        raw_url = row['fields']['Raw URL']
        if processsing >= LIMIT:
          print(f"Reached limit of {LIMIT} URLs processed.")
          break
        processsing += 1
        cleaned_url = clean_url(raw_url)
        target_table.update(row['id'], {'URL': cleaned_url, 'Status': 'Processed'})
      else:
        print(f"Skipping {row['fields']['Raw URL']} because it is not new.")
    except Exception as e:
      print(f"Error while processing {row['fields']['Raw URL']}: {e}")
      target_table.update(row['id'], {'Status': 'Error'})

step_1()
step_2()