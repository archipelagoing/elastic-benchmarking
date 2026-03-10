"""
CS589 - Homework 2
Part 3: Ranking Evaluation using ElasticSearch

This script:
1. Loads relevance judgments from *_cosidf.txt
2. Retrieves query titles from ElasticSearch
3. Builds ranking query (Figure 2 of assignment)
4. Uses ES rank_eval API to compute NDCG@10
5. Prints final average NDCG@10 score

Usage:
    python part3_ranking.py --index java-bm25 --cosidf java_cosidf.txt
"""

import argparse
import json
import numpy as np
from elasticsearch import Elasticsearch


# -----------------------------------------------------------
# 1. Load Ratings (Algorithm 2 from assignment)
# -----------------------------------------------------------

def load_ratings(cosidf_file, index_name):
    """
    Reads cosidf file and builds ratings dictionary:
    {
        qid1: [
            {"_index": index_name, "_id": qid2, "rating": label},
            ...
        ]
    }
    """

    ratings_dict = {}

    with open(cosidf_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            qid1 = parts[0]

            ratings = []
            for i in range(1, len(parts), 2):
                qid2 = parts[i]
                label = int(parts[i + 1])

                ratings.append({
                    "_index": index_name,
                    "_id": qid2,
                    "rating": label
                })

            ratings_dict[qid1] = ratings

    return ratings_dict


# -----------------------------------------------------------
# 2. Ranking Query Builder (Figure 2 from assignment)
# -----------------------------------------------------------

def build_ranking_query(qid, qid_title, ratings):
    """
    Constructs ranking request body for ES rank_eval API.
    Implements:
    - Exclude query document itself
    - Match title (boost 3.0)
    - Match body (boost 0.5)
    - Match answer (boost 0.5)
    - Compute NDCG@10
    """

    search_body = {
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
                                {
                                    "match": {
                                        "title": {
                                            "query": qid_title,
                                            "boost": 3.0
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "body": {
                                            "query": qid_title,
                                            "boost": 0.5
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "answer": {
                                            "query": qid_title,
                                            "boost": 0.5
                                        }
                                    }
                                }
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

    return search_body


# -----------------------------------------------------------
# 3. Main Evaluation Loop (Algorithm 1)
# -----------------------------------------------------------

def evaluate(index_name, cosidf_file):
    """
    Computes average NDCG@10 across all qid1 queries.
    """

    es = Elasticsearch("http://localhost:9200")

    ratings_dict = load_ratings(cosidf_file, index_name)

    ndcg_scores = []

    print(f"\nEvaluating index: {index_name}")
    print(f"Using relevance file: {cosidf_file}\n")

    for qid1 in ratings_dict.keys():

        try:
            doc = es.get(index=index_name, id=qid1)
        except Exception:
            continue  # skip if document missing

        qid1_title = doc["_source"]["title"]
        ratings = ratings_dict[qid1]

        search_body = build_ranking_query(qid1, qid1_title, ratings)

        result = es.rank_eval(index=index_name, body=search_body)

        ndcg = result["metric_score"]
        ndcg_scores.append(ndcg)

    if len(ndcg_scores) == 0:
        print("No valid scores computed. Check index or data.")
        return 0.0

    average_ndcg = float(np.mean(ndcg_scores))

    print(f"Final NDCG@10 for {index_name}: {average_ndcg:.6f}\n")

    return average_ndcg


# -----------------------------------------------------------
# 4. CLI Entry Point
# -----------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, help="ElasticSearch index name")
    parser.add_argument("--cosidf", required=True, help="Path to cosidf file")

    args = parser.parse_args()

    evaluate(args.index, args.cosidf)


if __name__ == "__main__":
    main()