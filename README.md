# Companies Research Agent

This is a set of scripts to automate the process of researching companies. It's based on GPT-3.5 and GPT-4
and uses [OpenAI API](https://beta.openai.com/). It's designed to work with [Airtable](https://airtable.com/).
Please take these scripts as a template for your own research and read the [Customization](#customization) section
to adjust them to your needs.

## Running the research

### Prerequisites
* You have an Airtable base, which has a table `Automagic` with following fields:
    - `URL` (URL)
    - `Name` (Single line text)
    - `Description` (Long text)
    - `Infrastructure?` (Boolean)
    - `Comment` (Long text)
    - `Status` (Single select; 'New' - default, 'Error', 'Read', 'Described', 'Q1_Answered')
    - `Page title` (Single line text)
    - `Page summary` (Long text)
**Note**: Airtable base is super handy for post-processing and collaboration, but unfortunately it
doesn't have the API for bases or tables creation or modification. So you'll need to create it manually.

* You have a list of URLs in the `URL` column of the table, and all records you want to research have `New` status.

* You have an `.env` file containing the following fields: 

```
AIRTABLE_API_KEY=<your Airtable API key>
BASE_ID=<your Airtable base ID>
OPEN_AI_KEY=<your OpenAI API key>
```

### Running the script

If you want to see how these scripts work for AIIA, you can run [main.py](main.py) with the following command:

```
poetry install
python main.py
```

### Customization

The script is tailored towards specific AIIA research: determining whether a company is a goof fit for
the AI Infrastructure Alliance. You'll likely need to customize it for your own research. Here are some
things to consider:

```python
# STEP 1: Read companies names and generate summaries
read_companies()
# STEP 2: Analyze companies
describe_companies()
# STEP 3: Answer questions
answer_q1_for_all_companies()
```

* `read_companies()` reads the company web page and fills in the `Page title` and `Page summary` (summarized with GPT-3.5).
You'll likely leave it as is.
* `describe_companies()` analyzes the fields `Page title` and `Page summary` and fills in the `Name` and `Description` fields
(using GPT-4). This step is also pretty universal and is needed to retrieve the company name from the web page and the short description based on summary.
* `answer_q1_for_all_companies()` answers the question "Is this company a good fit for AIIA?" (using GPT-4). This step is specific to AIIA, but you can easily replace it with your own question. To do that you'll need to do two changes:
    - Change the prompt in [q_n_a_agent.py](q_n_a_agent.py).
    - Rename the field in the table and in the `Company` class in [main.py](main.py). 
    It's not required, but it may help with clarity.

## Additional scripts

### Getting URLs from other AirTable base

Run [retrieve_from_airtable.py](retrieve_from_airtable.py). This script is useful when you have a list of URLs
coming from some other AirTable base. You'll need to point the target and source tables in the script, as well as
the name of the column where URLs are stored in the source table. This process is quick and resource-light.

### Getting URLs from an HTML page

Run [retrieve_from_html.py](retrieve_from_html.py). You'll need point the correct file 
in the script and a target table to put URLs into. There are two potential scenarios:

* Your URLs are "clean", i.e. they are just direct links to the companies web pages. In this case, 
you can comment the `step2()` call at the bottom of the page.

* Your URLs come from some sources like newsletters. In this case, they may be "dirty", i.e. contain
JS redirects, UTM tags, etc. In this case, you need `step2()` to clean them up. However, this step is 
resource-heavy, so be cautious and set proper `LIMIT` to avoid your computer freezing.