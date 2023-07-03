import os
from langchain import OpenAI
from pyairtable import Table
from pyairtable.formulas import match
from utils import clean_url
import guidance
import time

from reading_agent import ReadingAgent
from describing_agent import DescribingAgent
from q_n_a_agent import QnAAgent
from logger import setup_log, reset_log

from agent_summarizer import summarize, retrieve, get_best_llm_openai

import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

LIMIT = 100

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
BASE_ID = 'appvOnl6DnnKj8fVM'
TABLE_NAME = 'Automagic'

OPEN_AI_KEY = os.environ.get('OPEN_AI_KEY')
# llm = OpenAI(temperature=0, openai_api_key=OPEN_AI_KEY)
llm = get_best_llm_openai(OPEN_AI_KEY)

gpt = guidance.llms.OpenAI(model="gpt-3.5-turbo", token=OPEN_AI_KEY)
guidance.llm = gpt

logger = setup_log('companies')
reset_log('companies')

reader = ReadingAgent(llm, logger)
describer = DescribingAgent(gpt, logger)
answerer = QnAAgent(gpt, logger)

table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

# Fields schema:
# URL - string
# Name - string
# Description - string
# Infrastructure? - boolean
# Comment - string
# Page title - string
# Page summary - string
# Status - string


class Company:

  def __init__(self, id, url, status, page_title, page_summary, name,
               description, is_infrastructure, comment):
    self.id = id
    self.url = url
    self.status = status
    self.page_title = page_title
    self.page_summary = page_summary
    self.name = name
    self.description = description
    self.is_infrastructure = is_infrastructure
    self.comment = comment

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
      comment=fields['Comment'] if 'Comment' in fields else None)

  def to_airtable_fields(self):
    return {
      'URL': self.url,
      'Status': self.status,
      'Page title': self.page_title,
      'Page summary': self.page_summary,
      'Name': self.name,
      'Description': self.description,
      'Infrastructure?': self.is_infrastructure,
      'Comment': self.comment
    }


def connection_test():
  rows = table.all()
  print(len(rows))
  for row in rows:
    print(row)
    id = row['id']
    status = row['fields']['Status']
    table.update(id, {'Status': f'{status}'})


def clean_up_urls():
  rows = table.all()
  print(len(rows))
  for row in rows:
    id = row['id']
    url = row['fields']['URL']
    cleaned_url = clean_url(url)
    logger.info(f"[Clean up] Cleaning up {url} to {cleaned_url}")
    table.update(id, {'URL': f'{cleaned_url}'})


def read_company(company):
  try:
    result = summarize(company.url, llm)
    company.page_title = result['title']
    company.page_summary = result['summary']
    # company.page_title = reader.define_title_by_link(company.url)
    # company.page_summary = reader.define_summary_by_link(company.url)
    company.page_summary = company.page_summary.strip()
    print(f"=== Summary ===\n{company.page_summary}")
    company.status = 'Read'
    table.update(company.id, company.to_airtable_fields())
    logger.info(f"[Main] Processed company with URL {company.url}.")
  except Exception as e:
    table.update(company.id, {'Status': 'Error'})
    logger.error(
      f"[Main] Error while processing company with URL {company.url}.")
    logger.error(e)


def read_companies():
  logger.info("[Main] Reading companies from AirTable...")
  formula = match({'Status': 'New'})
  rows = table.all(formula=formula)
  n = 0
  all = len(rows)
  for row in rows[:LIMIT]:
    n += 1
    logger.info(f"[Main] Processing the record [{n}/{all}]")
    company = Company.from_airtable_fields(row['id'], row['fields'])
    read_company(company)
    time.sleep(1)
  logger.info(f"[Main] Done. Processed {n} companies.")


def describe_company(company):
  try:
    logger.info(f"[Main] Analyzing a company with URL {company.url}.")
    name, description, thoughts = describer.describe_company(
      company.page_title, company.page_summary)
    print(f"=== Thoughts ===\n{thoughts}\n")
    print(f"=== Name === \n{name}\n")
    print(f"=== Description ===\n{description}\n")
    if name.startswith("The name of the company is "):
      name = name[len("The name of the company is "):]
    if name.endswith("."):
      name = name[:-1]
    if name.startswith("\""):
      name = name[1:-1]
    if name.endswith("."):
      name = name[:-1]
    company.name = name
    company.description = description
    company.status = 'Described'
    table.update(company.id, company.to_airtable_fields())
    logger.info(f"[Analyze] Done. Processed company {company.name}")
  except Exception as e:
    table.update(company.id, {'Status': 'Error'})
    logger.error(f"[Main] Error while processing company {company.name}.")
    logger.error(e)


def describe_companies():
  logger.info("[Main] Describing companies from AirTable...")
  formula = match({'Status': 'Read'})
  rows = table.all(formula=formula)
  n = 0
  all = len(rows)
  for row in rows[:LIMIT]:
    n += 1
    logger.info(f"[Main] Processing the record [{n}/{all}]")
    company = Company.from_airtable_fields(row['id'], row['fields'])
    describe_company(company)
    time.sleep(1)
  logger.info(f"[Main] Done. Processed {n} companies.")


def answer_q1_for_company(company):
  try:
    logger.info(f"[Main] Analyzing a company with URL {company.url}.")
    is_infrastructure, comment, thoughts = answerer.answer_q1(
      company.name, company.description, company.page_summary)
    print(f"=== Thoughts ===\n{thoughts}\n")
    print(f"=== Infrastructure? === \n{is_infrastructure}\n")
    print(f"=== Comment ===\n{comment}\n")
    company.is_infrastructure = True if is_infrastructure.lower().startswith(
      'yes') else False
    if company.is_infrastructure:
      company.comment = comment
    else:
      company.comment = None
    company.status = 'Q1_Answered'
    table.update(company.id, company.to_airtable_fields())
    logger.info(f"[Analyze] Done. Processed company {company.name}")
  except Exception as e:
    table.update(company.id, {'Status': 'Error'})
    logger.error(f"[Main] Error while processing company {company.name}.")
    logger.error(e)


def answer_q1_for_all_companies():
  logger.info("[Main] Answering Q1 for companies from AirTable...")
  formula = match({'Status': 'Described'})
  rows = table.all(formula=formula)
  n = 0
  all = len(rows)
  for row in rows[:LIMIT]:
    n += 1
    logger.info(f"[Main] Processing the record [{n}/{all}]")
    company = Company.from_airtable_fields(row['id'], row['fields'])
    answer_q1_for_company(company)
    time.sleep(1)
  logger.info(f"[Main] Done. Processed {n} companies.")


# STEP 0: Clean up urls
# clean_up_urls()
# STEP 1: Read companies names and generate summaries
read_companies()
# STEP 2: Analyze companies
describe_companies()
# STEP 3: Answer questions
answer_q1_for_all_companies()
