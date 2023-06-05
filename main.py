import os
from langchain import OpenAI
from pyairtable import Table
from pyairtable.formulas import match
from urllib.parse import urlparse, urlunparse

from reading_agent import ReadingAgent
from logger import setup_log

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
BASE_ID = 'appvOnl6DnnKj8fVM'
TABLE_NAME = 'Automagic'

OPEN_AI_KEY = os.environ.get('OPEN_AI_KEY')
llm = OpenAI(temperature=0, openai_api_key=OPEN_AI_KEY)

logger = setup_log('companies')

reader = ReadingAgent(llm, logger)

table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

# Fields schema:
# URL - string
# Name - string
# Description - string
# Infrastructure? - boolean
# Agent? - boolean
# Page title - string
# Page summary - string
# Status - string


class Company:

  def __init__(self, id, url, status, page_title, page_summary, name,
               description, is_infrastructure, is_agent):
    self.id = id
    self.url = url
    self.status = status
    self.page_title = page_title
    self.page_summary = page_summary
    self.name = name
    self.description = description
    self.is_infrastructure = is_infrastructure
    self.is_agent = is_agent

  @staticmethod
  def from_airtable_fields(id, fields):

    return Company(
      id=id,
      url=fields['URL'],
      status=fields['Status'] if 'Status' in fields else 'New',
      page_title=fields['Page title'] if 'Page title' in fields else None,
      page_summary=fields['Page summary']
      if 'Page summary' in fields else None,
      name=fields['Name'] if 'Name' in fields else None,
      description=fields['Description'] if 'Description' in fields else None,
      is_infrastructure=fields['Infrastructure?']
      if 'Infrastructure?' in fields else None,
      is_agent=fields['Agent?'] if 'Agent?' in fields else None)

  def to_airtable_fields(self):
    return {
      'URL': self.url,
      'Status': self.status,
      'Page title': self.page_title,
      'Page summary': self.page_summary,
      'Name': self.name,
      'Description': self.description,
      'Infrastructure?': self.is_infrastructure,
      'Agent?': self.is_agent
    }


def connection_test():
  rows = table.all()
  print(len(rows))
  for row in rows:
    print(row)
    id = row['id']
    status = row['fields']['Status']
    table.update(id, {'Status': f'{status}'})


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


def clean_up_urls():
  rows = table.all()
  print(len(rows))
  for row in rows:
    id = row['id']
    url = row['fields']['URL']
    cleaned_url = clean_url(url)
    logger.info(f"[Clean up] Cleaning up {url} to {cleaned_url}")
    table.update(id, {'URL': f'{cleaned_url}'})


def process_company(company):
  company.page_title = reader.define_title_by_link(company.url)
  company.page_summary = reader.define_summary_by_link(company.url)
  company.status = 'Read'
  table.update(company.id, company.to_airtable_fields())
  logger.info(
    f"[Reader] Processed company {company.name} with URL {company.url}.")


def read_companies():
  logger.info("[Reader] Reading companies from AirTable...")
  formula = match({'Status': 'New'})
  rows = table.all(formula=formula)
  for row in rows:
    company = Company.from_airtable_fields(row['id'], row['fields'])
    process_company(company)
  logger.info(f"[Reader] Done. Processed {len(rows)} companies.")


# STEP 1: Clean up urls
# clean_up_urls()
# STEP 2: Read companies names and generate summaries
read_companies()
