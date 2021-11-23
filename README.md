# Search Engine for Sri Lankan Cricketers

## Folder Structure
```
.
├── data
│   ├── data.json     # Data scraped from ESPNCricInfo
│
├── app               # Folder containing the code
│  │
│  ├── app.py         # Flask app
│  ├── filter.py      # Class to represent a filtering by a numeric field
│  ├── scrapper.py    # Code used to scrap data
│  ├── search.py      # Code containing query processing and elasticsearch client for search
│  ├── seed.py        # Code used to seed elasticsearch with the data
│
│── queries.txt       # Examples of supported queries
├── requirements.txt  # Packages needed to run the code
.
```
## Data

- Source: Extracted from ESPNCricInfo and translated (Some translations were manual, and others were done using google translate)
- Fields:
    - Name – Text Field
    - Birth year – Text Field
    - Birthplace – Text Field
    - Role – Text Field
    - Batting Style – Text Field
    - Bowling Style – Text Field
    - Biography – Text Field
    - Teams Played In – Text Field
    - Matches Played – Integer Field
    - Runs Scored – Integer Field
    - Wickets – Integer Field
    - Highest Score– Integer Field

## Techniques Used for Querying and Indexing

- Elasticsearch was used for the index construction.
  - The standard configuration of Elasticsearch was used for indexing.
- Querying Method
  - The query is first stemmed.
  - Then the synonyms are replaced by a single class.
  - Before the query is sent to elastic search the priority of each text is changed based on the existence of certain keywords or similar words provided using a list.
  - The query is compared with all text fields and the results are sorted by the score of the best matching field.
  - Filtering is allowed with the Wickets, Highest Score, Runs Scored and Matches Played field.

## Advanced Techniques Used

- Supporting greater than, less than filter queries (with full symbol and limited natural language support) for Wickets, Runs Scored, Highest Score and Matches played by using a rule-based approach
- Support for synonyms
- Limited bilingual support for cricket jargon.
- Prioritizing fields based on the existence of keywords in the query
- Supports querying multiple text fields: Name, Birth Year, Birthplace, Role, Batting Style, Bowling Style, Biography, Teams Played In.
- Tolerate simple spelling errors and different forms of words due to use of stemming ("ගාල්ලේ" will match "ගාල්ල" etc.).

**GitHub URL** :[**https://github.com/thamidurm/IR-Project**](https://github.com/thamidurm/IR-Project)