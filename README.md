# CS 589 – Retrieval Models with ElasticSearch

## Overview

This project implements and evaluates three classical information retrieval models using ElasticSearch 7.9.0:

- TF-IDF (scripted similarity)
- BM25
- Dirichlet Language Model

The models are evaluated on three StackOverflow datasets:

- Python  
- Java  
- JavaScript  

Performance is measured using **NDCG@10** via the ElasticSearch Ranking Evaluation API.

---

## Dataset Description

Each language dataset contains:

- `$lang_qid2all.txt`  
  Contains all StackOverflow questions (title, body, and answers).

- `$lang_cosidf.txt`  
  Contains relevance judgments between `qid1` and `qid2`.

Total indices created:

```
3 languages × 3 similarity models = 9 indices
```

---

## Setup Instructions

### Install ElasticSearch 7.9.0

Download:  
https://www.elastic.co/downloads/past-releases/elasticsearch-7-9-0

Start ElasticSearch:

```bash
cd elasticsearch-7.9.0
bin/elasticsearch
```

Verify installation:

```
http://localhost:9200/
```

---

### Install Kibana 7.9.0

Download:  
https://www.elastic.co/downloads/past-releases/kibana-7-9-0

Start Kibana:

```bash
cd kibana-7.9.0
bin/kibana
```

Open:

```
http://localhost:5601
```

Navigate to:

```
Management → Dev Tools
```

---

## Step 1 – Create Index

Example (BM25 default):

```json
PUT /python_bm25
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "standard"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title":  { "type": "text", "analyzer": "my_analyzer" },
      "body":   { "type": "text", "analyzer": "my_analyzer" },
      "answer": { "type": "text", "analyzer": "my_analyzer" }
    }
  }
}
```

For other similarity models:

- **TF-IDF** → configure scripted similarity  
- **Dirichlet LM** → specify `"similarity": "LMDirichlet"` in index settings  

---

## Step 2 – Bulk Index Data

Convert `$lang_qid2all.txt` into JSON format compatible with ElasticSearch bulk indexing.

Bulk index:

```bash
curl -H "Content-Type: application/json" \
-XPOST localhost:9200/python_bm25/_bulk \
--data-binary "@python.json"
```

If the JSON file exceeds 100MB, split it into multiple batches.

Verify indexing:

```json
GET /python_bm25/_search
{
  "query": {
    "match_all": {}
  }
}
```

---

## Step 3 – Ranking and Evaluation

NDCG@10 is computed using ElasticSearch’s Ranking Evaluation API.

### Workflow

For each `qid1`:

1. Retrieve the corresponding question title  
2. Load 30 relevance judgments from `$lang_cosidf.txt`  
3. Execute ranking query  
4. Compute NDCG@10  
5. Aggregate scores across all queries  

---

## Ranking Function (Python)

```python
from elasticsearch import Elasticsearch

es = Elasticsearch()

def ranking(qid, qid_title, ratings):
    return {
        "requests": [
            {
                "id": str(qid),
                "request": {
                    "query": {
                        "bool": {
                            "must_not": {
                                "match": {"_id": qid}
                            },
                            "should": [
                                {"match": {"title": qid_title}},
                                {"match": {"body": qid_title}},
                                {"match": {"answer": qid_title}}
                            ]
                        }
                    }
                },
                "ratings": ratings
            }
        ],
        "metric": {
            "dcg": {
                "k": 10,
                "normalize": True
            }
        }
    }
```

---

## Results

| Dataset | TF-IDF | BM25 | Dirichlet LM |
|----------|--------|--------|--------------|
| Python | X.XXXX | X.XXXX | X.XXXX |
| Java   | X.XXXX | X.XXXX | X.XXXX |
| JS     | X.XXXX | X.XXXX | X.XXXX |

*(Replace placeholders with actual NDCG@10 values.)*

---

## Technologies Used

- Python  
- ElasticSearch 7.9.0  
- Kibana 7.9.0  
- ElasticSearch Ranking Evaluation API  

---

## Concepts Demonstrated

- Inverted indexing  
- Similarity scoring functions  
- TF-IDF vs BM25 vs Dirichlet LM  
- Bulk indexing large corpora  
- Ranking evaluation using NDCG  
- Information retrieval benchmarking  

---

## How to Run

1. Install ElasticSearch and Kibana  
2. Create indices for each language and similarity model  
3. Convert dataset to JSON  
4. Bulk index documents  
5. Run Python ranking script  
6. Compute and report NDCG@10  

---

## Recommended Repository Structure

```
/code
/data
/report
README.md
```

---

## Deliverables

- Python implementation  
- Index creation commands  
- Bulk indexing commands  
- NDCG@10 evaluation results  
