import os
import markdown
from pathlib import Path
from bs4 import BeautifulSoup
import json

RAW_DIR = Path("/home/siddharth/TDS-Virtual-Teaching-Assistant/rawdata/tools-in-data-science-public")
OUT_DIR = Path("/home/siddharth/TDS-Virtual-Teaching-Assistant/processed_data")
OUT_DIR.mkdir(exist_ok=True)

def markdown_to_text(md_content):
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def process_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    text = markdown_to_text(md_content)
    title = file_path.stem.replace("-", " ").title()

    chunks = []
    words = text.split()
    for i in range(0, len(words), 500):
        chunk_words = words[i:i+500]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
    
    return [{
        "filename": file_path.name,
        "title": title,
        "chunk_id": i,
        "content": chunk
    } for i, chunk in enumerate(chunks)]

all_docs = []

for file in RAW_DIR.glob("*.md"):
    print(f"Processing {file.name}")
    chunks = process_markdown_file(file)
    all_docs.extend(chunks)

# Save as JSON
output_path = OUT_DIR / "tds-course-content.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_docs, f, indent=2)

print(f"Saved {len(all_docs)} chunks to {output_path}")
