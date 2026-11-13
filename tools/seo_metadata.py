"""One reviewed metadata source, shared by all HTML generators."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TITLE_MAX=60
DESCRIPTION_MAX=155
COPY=json.loads((ROOT/'content/seo-metadata.json').read_text())

def for_page(path):
    key=str(path).split('#',1)[0].lstrip('/')
    if not key or key.endswith('/'):key+='index.html'
    record=COPY[key]
    title,description=record['title'],record['description']
    assert 0<len(title)<=TITLE_MAX,(key,len(title))
    assert 0<len(description)<=DESCRIPTION_MAX,(key,len(description))
    assert title==title.strip() and description==description.strip(),key
    return title,description
