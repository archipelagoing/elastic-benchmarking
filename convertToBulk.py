import json
import sys
from pathlib import Path

# Usage: python convert_to_bulk.py java
#        python convert_to_bulk.py python
#        python convert_to_bulk.py javascript

if len(sys.argv) != 2:
    print("Usage: python convert_to_bulk.py <language>")
    sys.exit(1)

lang = sys.argv[1]

input_path = Path(f"dataset/{lang}_qid2all.txt")

if not input_path.exists():
    print(f"File not found: {input_path}")
    sys.exit(1)

max_docs = 50000
doc_count = 0
batch = 1

output_path = f"{lang}_batch{batch}.json"
out = open(output_path, "w", encoding="utf-8")

with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")

        if len(parts) != 4:
            continue

        qid, title, question, answer = parts

        # Bulk metadata line
        out.write(json.dumps({"index": {"_id": qid}}) + "\n")

        # Document line
        out.write(json.dumps({
            "title": title,
            "body": question,
            "answer": answer
        }) + "\n")

        doc_count += 1

        if doc_count >= max_docs:
            out.close()
            batch += 1
            doc_count = 0
            output_path = f"{lang}_batch{batch}.json"
            out = open(output_path, "w", encoding="utf-8")

out.close()
print(f"{lang} conversion complete.")