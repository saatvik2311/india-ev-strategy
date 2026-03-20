import os
import json
from pathlib import Path
import docx
import re

ROOT_DIR = Path(__file__).parent.parent
DOCX_PATH = ROOT_DIR / "context.docx"
DOCS_DIR = ROOT_DIR / "docs"

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def build_docs():
    print(f"Loading {DOCX_PATH}...")
    doc = docx.Document(DOCX_PATH)
    
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    # 1. Read all paragraphs
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    # 2. Chunking logic (Target ~3000 chars per chunk to fit comfortably in LLM context)
    chunks = []
    current_chunk = []
    current_length = 0
    TARGET_LENGTH = 3000  # ~500 words
    
    for p in paragraphs:
        current_chunk.append(p)
        current_length += len(p)
        
        # If we hit the target length and this paragraph ends with a sentence boundary, break chunk
        # Just breaking at the target length is fine as long as we keep the paragraph intact.
        if current_length >= TARGET_LENGTH:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            current_length = 0
            
    # Add any remaining text
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    print(f"Generated {len(chunks)} document chunks.")
    
    index_map = {}
    
    for i, chunk_text in enumerate(chunks):
        chunk_text = clean_text(chunk_text)
        filename = f"knowledge_node_{i+1:03d}.md"
        filepath = DOCS_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Knowledge Node {i+1}\n\n")
            f.write(chunk_text)
            
        # Extract a few naive keywords (top 10 longest words for the index mapping just as metadata)
        words = re.findall(r'\b[a-zA-Z]{5,}\b', chunk_text.lower())
        from collections import Counter
        keywords = [w for w, c in Counter(words).most_common(5) if w not in ['which', 'there', 'their', 'about', 'would', 'could']]
        
        index_map[filename] = {
            "id": i+1,
            "length_chars": len(chunk_text),
            "top_keywords": keywords
        }
        
    # Write the index mapping
    with open(DOCS_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index_map, f, indent=4)
        
    print(f"Successfully wrote {len(chunks)} Markdown nodes and index.json to {DOCS_DIR}/")

if __name__ == "__main__":
    if not DOCX_PATH.exists():
        print(f"Could not find {DOCX_PATH}")
    else:
        build_docs()
