FROM searxng/searxng:latest
COPY settings.yml /etc/searxng/settings.yml
COPY searx/templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
COPY searx/templates/static/themes/simple/img/favicon.png /usr/local/searxng/searx/static/themes/simple/img/favicon.png
COPY searx/templates/static/themes/simple/img/favicon.svg /tmp/custom-favicon.svg

USER root

# Copia il favicon custom
RUN cp /tmp/custom-favicon.svg /usr/local/searxng/searx/static/themes/simple/img/favicon.svg && \
    cd /usr/local/searxng/searx/static/themes/simple/img/ && \
    rm -f favicon.svg.gz favicon.svg.br && \
    gzip -9 -k favicon.svg

# Crea wrapper per l'entrypoint che ricopia il favicon dopo l'avvio
RUN mv /usr/local/searxng/entrypoint.sh /usr/local/searxng/entrypoint-original.sh && \
    echo '#!/bin/sh' > /usr/local/searxng/entrypoint.sh && \
    echo '/usr/local/searxng/entrypoint-original.sh "$@" &' >> /usr/local/searxng/entrypoint.sh && \
    echo 'PID=$!' >> /usr/local/searxng/entrypoint.sh && \
    echo 'sleep 3' >> /usr/local/searxng/entrypoint.sh && \
    echo 'cp /tmp/custom-favicon.svg /usr/local/searxng/searx/static/themes/simple/img/favicon.svg' >> /usr/local/searxng/entrypoint.sh && \
    echo 'cd /usr/local/searxng/searx/static/themes/simple/img/' >> /usr/local/searxng/entrypoint.sh && \
    echo 'rm -f favicon.svg.gz favicon.svg.br' >> /usr/local/searxng/entrypoint.sh && \
    echo 'gzip -9 -k favicon.svg' >> /usr/local/searxng/entrypoint.sh && \
    echo 'wait $PID' >> /usr/local/searxng/entrypoint.sh && \
    chmod +x /usr/local/searxng/entrypoint.sh

COPY searx/templates/simple/base_index.html /usr/local/searxng/searx/templates/simple/base_index.html
COPY searx/templates/simple/index.html /usr/local/searxng/searx/templates/simple/index.html
COPY searx/templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY searx/templates/simple/icons.html /usr/local/searxng/searx/templates/simple/icons.html
COPY searx/templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
