import requests
from bs4 import BeautifulSoup

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain


class ReadingAgent:

  def __init__(self, llm, logger):
    self.llm = llm
    self.logger = logger
    self.text_splitter = RecursiveCharacterTextSplitter()
    prompt_template = """
    Write a concise summary of the following text.
    This is a landing page of a company. 
    I want you to provide me with bullet points explaining what this company does,
    and what the features of its solution are.
    Keep each bullet point under one or two sentences.

      {text}

    Bullet points:"""
    self.summarizer_prompt = PromptTemplate(template=prompt_template,
                                            input_variables=["text"])

  def define_title_by_link(self, link):
    try:
      response = requests.get(link)
      soup = BeautifulSoup(response.content, 'html.parser')
      title = soup.find('title').text.strip()
      return title
    except:
      self.logger.error(
        f"[Reader] Failed to load {link}, status code: {response.status_code}")

  def define_summary_by_link(self, link):
    self.logger.info(f"[Reader] Getting content from a link: {link}...")
    # Get the content of the link
    headers = {
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }
    response = requests.get(link, headers=headers)

    if response.status_code != 200:
      self.logger.error(
        f"[Reader] Failed to load {link}, status code: {response.status_code}")
      return None

    content = response.text
    soup = BeautifulSoup(content, "html.parser")

    # Remove any script or style tags
    for script in soup(["script", "style"]):
      script.decompose()

    # Get the plain text
    text = soup.get_text()

    try:
      self.logger.info("[Reader] Summarizing...")
      texts = self.text_splitter.split_text(text)
      docs = [Document(page_content=t) for t in texts]
      chain = load_summarize_chain(self.llm,
                                   chain_type="map_reduce",
                                   map_prompt=self.summarizer_prompt,
                                   combine_prompt=self.summarizer_prompt)
      summary = chain.run(docs)
      self.logger.info(f"[Reader] Generated summary for {link}.")
      return summary
    except Exception as e:
      self.logger.error(
        f"[Reader] Error while summarizing the link {link}: {e}")
      return None
