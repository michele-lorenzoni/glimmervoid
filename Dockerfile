FROM searxng/searxng:latest

# Copia i file necessari per generare settings.yml
COPY settings.yml.template /tmp/settings.yml.template
COPY blocked_domains.txt /tmp/blocked_domains.txt

# Genera settings.yml durante il build (script inline)
USER root
RUN set -e && \
    echo "[INFO] Inizio generazione settings.yml" && \
    # Genera la lista di domini formattati in un file temporaneo
    > /tmp/domains_formatted.txt && \
    while IFS= read -r domain || [ -n "$domain" ]; do \
    domain=$(echo "$domain" | sed 's/#.*$//' | xargs); \
    if [ -n "$domain" ]; then \
    echo "      - ${domain}" >> /tmp/domains_formatted.txt; \
    fi; \
    done < /tmp/blocked_domains.txt && \
    # Sostituisci il placeholder nel template usando sed
    sed '/{{BLOCKED_DOMAINS}}/r /tmp/domains_formatted.txt' /tmp/settings.yml.template | \
    sed '/{{BLOCKED_DOMAINS}}/d' > /etc/searxng/settings.yml && \
    echo "[INFO] File settings.yml generato con successo!" && \
    # Verifica che il file non sia vuoto
    if [ ! -s /etc/searxng/settings.yml ]; then \
    echo "[ERROR] settings.yml è vuoto!"; \
    exit 1; \
    fi && \
    # Cleanup
    chown searxng:searxng /etc/searxng/settings.yml && \
    rm -f /tmp/settings.yml.template /tmp/blocked_domains.txt /tmp/domains_formatted.txt

# Crea la directory per i file JSON custom
RUN mkdir -p /usr/local/searxng/searx/static/custom && \
    chown searxng:searxng /usr/local/searxng/searx/static/custom

RUN mkdir -p /usr/local/searxng/searx/static/fonts && \
    chown searxng:searxng /usr/local/searxng/searx/static/fonts

# Copia i file JSON con gli URL
COPY searx/templates/static/custom/highlight_urls.json /usr/local/searxng/searx/static/custom/highlight_urls.json
COPY searx/templates/static/custom/unwanted_urls.json /usr/local/searxng/searx/static/custom/unwanted_urls.json
COPY searx/templates/static/custom/favorite_urls.json /usr/local/searxng/searx/static/custom/favorite_urls.json

COPY searx/templates/static/fonts/digital_dreamer.otf /usr/local/searxng/searx/static/fonts/digital_dreamer.otf
COPY searx/templates/static/fonts/ubuntu_r.ttf /usr/local/searxng/searx/static/fonts/ubuntu_r.ttf
COPY searx/templates/static/output.css /usr/local/searxng/searx/static/output.css

# Copia i file di personalizzazione
COPY searx/templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
COPY searx/templates/static/themes/simple/img/favicon.png /usr/local/searxng/searx/static/themes/simple/img/favicon.png
COPY searx/templates/static/themes/simple/img/favicon.svg /usr/local/searxng/searx/static/themes/simple/img/favicon.svg
COPY searx/templates/static/themes/simple/img/favicon.svg.gz /usr/local/searxng/searx/static/themes/simple/img/favicon.svg.gz
COPY searx/templates/static/themes/simple/img/favicon.svg.br /usr/local/searxng/searx/static/themes/simple/img/favicon.svg.br

COPY searx/templates/simple/searxng-wordmark.min.svg /usr/local/searxng/searx/templates/simple/searxng-wordmark.min.svg
COPY searx/templates/simple/simple_search.html /usr/local/searxng/searx/templates/simple/simple_search.html
COPY searx/templates/simple/base_index.html /usr/local/searxng/searx/templates/simple/base_index.html
COPY searx/templates/simple/index.html /usr/local/searxng/searx/templates/simple/index.html
COPY searx/templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY searx/templates/simple/icons.html /usr/local/searxng/searx/templates/simple/icons.html
COPY searx/templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png

USER searxng
