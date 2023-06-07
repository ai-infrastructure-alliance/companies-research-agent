import os
from pyairtable import Table
from urllib.parse import urlparse, urlunparse

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
BASE_ID = 'appvOnl6DnnKj8fVM'
TABLE_NAME = 'Automagic'

SOURCE_TABLE_NAME = 'Source 1'
SOURCE_COLUMN_NAME = 'URL'

target_table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
source_table = Table(AIRTABLE_API_KEY, BASE_ID, SOURCE_TABLE_NAME)


def clean_url(url):
  parsed_url = urlparse(url)
  cleaned_url = parsed_url._replace(query="")
  if not cleaned_url.scheme:
    cleaned_url = cleaned_url._replace(scheme='https')
  new_url = urlunparse(cleaned_url)
  new_url = new_url.replace('///', '//')
  if new_url.endswith('/'):
    new_url = new_url[:-1]
  return new_url


new_rows = source_table.all()
new_urls = [clean_url(row['fields'][SOURCE_COLUMN_NAME]) for row in new_rows]
old_rows = target_table.all()
old_urls = set([row['fields']['URL'] for row in old_rows])

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
