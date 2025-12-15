import re

webapp_file = '/usr/local/searxng/searx/webapp.py'

with open(webapp_file, 'r') as f:
    content = f.read()

# Trova la riga dove viene chiamato render() nella funzione search()
# e aggiungi highlight_urls ai parametri

# Pattern per trovare return render( nella funzione search
pattern = r"(return render\([^)]*)"

# Aggiunge highlight_urls prima della chiusura
replacement = r"\1, highlight_urls=settings.get('ui', {}).get('highlight_urls', [])"

content = re.sub(pattern, replacement, content, count=1)

with open(webapp_file, 'w') as f:
    f.write(content)

print("✅ webapp.py patched successfully")
