FROM searxng/searxng:latest

# Copia i file necessari per generare settings.yml
COPY settings.yml.template /tmp/settings.yml.template
COPY blocked_domains.txt /tmp/blocked_domains.txt
COPY generate_settings.sh /tmp/generate_settings.sh

# Genera settings.yml durante il build
USER root
RUN chmod +x /tmp/generate_settings.sh && \
    cd /tmp && \
    ./generate_settings.sh && \
    mv /tmp/settings.yml /etc/searxng/settings.yml && \
    chown searxng:searxng /etc/searxng/settings.yml && \
    rm -f /tmp/settings.yml.template /tmp/blocked_domains.txt /tmp/generate_settings.sh

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
