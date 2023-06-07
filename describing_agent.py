import guidance


class DescribingAgent:

  def __init__(self, gpt, logger):
    self.gpt = gpt
    self.logger = logger

  def describe_company(self, title, summary):
    self.logger.info(f"[Describer] Describing the company from {title}...")
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
    explain in one sentence, what this company does. 
    
    First, let's think step by step.
    {{~/user}}

    {{#assistant~}}
    {{gen 'thoughts' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}

    {{#user~}}
    Very well. Now, I need you to answer only the questions I ask, without 
    details and explanations.

    Question 1: What is the name of the company? Only tell me the name.
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
    ''',
                        llm=self.gpt)
    result = analyzer(title=title, summary=summary)
    self.logger.info(f"[Describer] Described the company at {title}.")
    return result["name"], result["description"], result["thoughts"]
