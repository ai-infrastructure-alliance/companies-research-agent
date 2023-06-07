import guidance


class QnAAgent:

  def __init__(self, gpt, logger):
    self.gpt = gpt
    self.logger = logger

  # Q1: Does the product refer to AI Infrastructure?
  def answer_q1(self, name, description, summary):
    self.logger.info(f"[Answerer] Answering Q1 for {name}...")
    answerer = guidance('''
    {{#system~}}
    You are a researcher who is exploring the companies in the AI sector.
    You have a lot of experience in AI, ML and DS. 
    {{~/system}}
  
    {{#user~}}
    I have found a company called {{name}}. 
    
    The brief desciption of this company is: 
    
    {{description}}
    
    The summary of the company web page is here:
    
    {{summary}}

    Your task is figure out whether this company's target audience is 
    software developers create applications with AI.

    Examples of solutions that are targeted to software developers include 
    platforms that host the machine learning models, cloud infrastructure
    managament, and database managment, including vector database. 
    Python frameworks that allow communicating with databases, hosted API, 
    models including LLMs, are also considered to be useful.

    On the contrary, the companies that build somlutions for end-user, 
    e.g. for designers, copywriters, sales persons, HR, etc, and provide
    API to their solutions, are NOT considered to be targeting software
    developers.

    Let's think step by step.
    {{~/user}}

    {{#assistant~}}
    {{gen 'thoughts' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}

    {{#user~}}
    Very well. Now, answer the question: Is the company's target audience
    sofware developers? Only answer Yes or No. 
    {{~/user}}
    
    {{#assistant~}}
    {{gen 'is_infrastructure' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}
    
    {{#user~}}
    If the answer to the previous question is Yes, explain
    in one sentence, why do you think so. Otherwise just asnwer "No".
    {{~/user}}
    
    {{#assistant~}}
    {{gen 'comment' temperature=0.5 max_tokens=1000}}
    {{~/assistant}}
    ''',
                        llm=self.gpt)
    result = answerer(name=name, description=description, summary=summary)
    self.logger.info(f"[Answerer] Answered Q1 for {name}")
    return result["is_infrastructure"], result["comment"], result["thoughts"]
