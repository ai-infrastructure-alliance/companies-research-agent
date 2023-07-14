import os
from pyairtable import Table
from utils import clean_url

from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
BASE_ID = 'appvOnl6DnnKj8fVM'
TABLE_NAME = 'Automagic'

SOURCE_TABLE_NAME = 'Source 6'
SOURCE_COLUMN_NAME = 'URL'

target_table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
source_table = Table(AIRTABLE_API_KEY, BASE_ID, SOURCE_TABLE_NAME)

new_rows = source_table.all()
new_urls = [row['fields'][SOURCE_COLUMN_NAME] for row in new_rows if SOURCE_COLUMN_NAME in row['fields']]
new_urls = list(set(new_urls))
print(f"Found {len(new_urls)} new urls.")

old_rows = target_table.all()
old_urls = set([row['fields']['URL'] for row in old_rows])
print(f"Found {len(old_urls)} old urls.")

added = 0
skipped = 0
for new_url in new_urls:
  if new_url not in old_urls:
    print(f"Adding {new_url}")
    target_table.create({'URL': new_url})
    added += 1
  else:
    print(f"Skipping {new_url}")
    skipped += 1
print(f"Added {added} URLs")
print(f"Skipped {skipped} URLs")
