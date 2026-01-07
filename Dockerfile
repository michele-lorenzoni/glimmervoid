FROM searxng/searxng:latest

# Copia i file necessari per generare settings.yml
COPY settings.yml.template /tmp/settings.yml.template
COPY blocked_domains.txt /tmp/blocked_domains.txt

# Genera settings.yml durante il build (script inline)
USER root
RUN set -e && \
    echo "[INFO] Inizio generazione settings.yml" && \
    # Genera la lista di domini formattati
    DOMAINS_YAML="" && \
    while IFS= read -r domain || [ -n "$domain" ]; do \
        domain=$(echo "$domain" | sed 's/#.*$//' | xargs); \
        if [ -n "$domain" ]; then \
            DOMAINS_YAML="${DOMAINS_YAML}      - ${domain}\n"; \
        fi; \
    done < /tmp/blocked_domains.txt && \
    # Sostituisci il placeholder nel template
    if grep -q "{{BLOCKED_DOMAINS}}" /tmp/settings.yml.template; then \
        perl -pe "s/\{\{BLOCKED_DOMAINS\}\}/${DOMAINS_YAML}/g" /tmp/settings.yml.template > /etc/searxng/settings.yml; \
        echo "[INFO] File settings.yml generato con successo!"; \
    else \
        echo "[ERROR] Placeholder {{BLOCKED_DOMAINS}} non trovato!"; \
        exit 1; \
    fi && \
    # Cleanup
    chown searxng:searxng /etc/searxng/settings.yml && \
    rm -f /tmp/settings.yml.template /tmp/blocked_domains.txt

# Copia i file di personalizzazione
COPY searx/templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
COPY searx/templates/static/themes/simple/img/favicon.png /usr/local/searxng/searx/static/themes/simple/img/favicon.png
COPY searx/templates/static/themes/simple/img/favicon.svg /usr/local/searxng/searx/static/themes/simple/img/favicon.svg
COPY searx/templates/static/themes/simple/img/favicon.svg.gz /usr/local/searxng/searx/static/themes/simple/img/favicon.svg.gz
COPY searx/templates/static/themes/simple/img/favicon.svg.br /usr/local/searxng/searx/static/themes/simple/img/favicon.svg.br

COPY searx/templates/simple/base_index.html /usr/local/searxng/searx/templates/simple/base_index.html
COPY searx/templates/simple/index.html /usr/local/searxng/searx/templates/simple/index.html
COPY searx/templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY searx/templates/simple/icons.html /usr/local/searxng/searx/templates/simple/icons.html
COPY searx/templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png

USER searxng
