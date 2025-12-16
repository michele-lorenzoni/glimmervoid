FROM searxng/searxng:latest

# Build timestamp: 2025-12-15-23-30
COPY settings.yml /etc/searxng/settings.yml
COPY templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY static/themes/simple/custom.css /usr/local/searxng/searx/static/themes/simple/custom.css

USER root

# VERIFICA CHE IL FILE SIA STATO COPIATO E CONTENGA LO SCRIPT
RUN echo "==== VERIFICA results.html ====" && \
    ls -lh /usr/local/searxng/searx/templates/simple/results.html && \
    echo "==== CERCA <script> nel file ====" && \
    grep -n "SCRIPT LOADED" /usr/local/searxng/searx/templates/simple/results.html && \
    echo "==== FINE VERIFICA ===="

RUN chown -R searxng:searxng /etc/searxng/settings.yml

USER searxng
