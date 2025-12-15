FROM searxng/searxng:latest

# Aggiungi un commento random per forzare rebuild
# Build timestamp: 2025-12-15-21-45

COPY settings.yml /etc/searxng/settings.yml
COPY templates/result_templates/default.html /usr/local/searxng/searx/templates/result_templates/default.html
COPY templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY templates/static/themes/simple/custom.css /usr/local/searxng/searx/static/themes/simple/custom.css

USER root

# STAMPA INFO - dovresti vedere questo nei logs
RUN echo "============================================" && \
    echo "INIZIO VERIFICA FILE" && \
    echo "============================================" && \
    ls -lah /usr/local/searxng/searx/templates/result_templates/ && \
    echo "---" && \
    head -10 /usr/local/searxng/searx/templates/result_templates/default.html && \
    echo "============================================"

RUN chown -R searxng:searxng /etc/searxng/settings.yml

USER searxng
