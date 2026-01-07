FROM searxng/searxng:latest
COPY settings.yml /etc/searxng/settings.yml
COPY searx/templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
COPY searx/templates/static/themes/simple/img/favicon.png /usr/local/searxng/searx/static/themes/simple/img/favicon.png
COPY searx/templates/static/themes/simple/img/favicon.svg /tmp/custom-favicon.svg

USER root

# Trova l'entrypoint
RUN echo "=== Looking for entrypoint ===" && \
    find /usr/local/searxng -name "*entrypoint*" 2>/dev/null && \
    find / -name "entrypoint.sh" 2>/dev/null | head -5

# Copia il favicon custom
RUN cp /tmp/custom-favicon.svg /usr/local/searxng/searx/static/themes/simple/img/favicon.svg && \
    cd /usr/local/searxng/searx/static/themes/simple/img/ && \
    rm -f favicon.svg.gz favicon.svg.br && \
    gzip -9 -k favicon.svg

COPY searx/templates/simple/base_index.html /usr/local/searxng/searx/templates/simple/base_index.html
COPY searx/templates/simple/index.html /usr/local/searxng/searx/templates/simple/index.html
COPY searx/templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY searx/templates/simple/icons.html /usr/local/searxng/searx/templates/simple/icons.html
COPY searx/templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
