FROM searxng/searxng:latest
COPY settings.yml /etc/searxng/settings.yml
COPY searx/templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
COPY searx/templates/static/themes/simple/img/favicon.png /usr/local/searxng/searx/static/themes/simple/img/favicon.png
COPY searx/templates/static/themes/simple/img/favicon.svg /usr/local/searxng/searx/static/themes/simple/img/favicon.svg

USER root
# Scopri quale distro è e installa brotli
RUN echo "=== Checking OS ===" && \
    cat /etc/os-release && \
    echo "=== Trying to install brotli ===" && \
    (apt-get update && apt-get install -y brotli) || \
    (yum install -y brotli) || \
    (dnf install -y brotli) || \
    echo "Failed to install brotli" && \
    echo "=== Compressing favicon ===" && \
    cd /usr/local/searxng/searx/static/themes/simple/img/ && \
    rm -f favicon.svg.gz favicon.svg.br && \
    gzip -9 -k favicon.svg && \
    (brotli -9 -k favicon.svg || echo "Brotli not available, skipping")

COPY searx/templates/simple/base_index.html /usr/local/searxng/searx/templates/simple/base_index.html
COPY searx/templates/simple/index.html /usr/local/searxng/searx/templates/simple/index.html
COPY searx/templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY searx/templates/simple/icons.html /usr/local/searxng/searx/templates/simple/icons.html
COPY searx/templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
