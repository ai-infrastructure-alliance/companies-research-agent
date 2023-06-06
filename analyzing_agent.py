import guidance


class AnalyzingAgent:

  def __init__(self, gpt, logger):
    self.gpt = gpt
    self.logger = logger

  def analyze_company(self, title, summary):
    self.logger.info(f"[Analyzer] Analyzing summary for {title}...")
    analyzer = guidance('''
    {{#system~}}
    You are a researcher who is exploring the companies in the AI sector.
    You have a lot of experience in AI, ML and DS. 
    {{~/system}}
  
    {{#user~}}
    I have found a company website and want you to explore it. The title of the 
    page is {{title}}. The summary of the page is here:
    
    {{summary}}.

    Your task is to find out the name of the company from this data and
    explain in one sentence, what this company does. Also, I would like to know,
    if this company is doing anything that can be used by software developers
    to create applications with AI.

    Examples of things that can be used by software developer include 
    platforms that host the machine learning models, managing the cloud
    infrastructure, and managing the databases. Python frameworks that allow
    communicating with databases, hosted API, models including LLMs, are also
    considered to be useful.

    Let's think step by step.
    {{~/user}}

    {{#assistant~}}
    {{gen 'thoughts' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}

    {{#user~}}
    Very well. Now, I need you to answer only the questions I ask, without 
    details and explanations.

    Question 1: What is the name of the company? Only output the name, without
    "The name of the company is".
    {{~/user}}

    {{#assistant~}}
    {{gen 'name' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}

    {{#user~}}
    Question 2: What does this company do, in one sentence?
    {{~/user}}
    
    {{#assistant~}}
    {{gen 'description' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}
    
    {{#user~}}
    Question 3: Does this company do anything that can be used by 
    software developers to create AI apps? Answer only Yes or No.
    {{~/user}}
    
    {{#assistant~}}
    {{gen 'is_infrastructure' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}''',
                        llm=self.gpt)
    result = analyzer(title=title, summary=summary)
    self.logger.info(f"[Analyzer] Analyzed summary for {title}.")
    return result["name"], result["description"], result[
      "is_infrastructure"], result["thoughts"]
