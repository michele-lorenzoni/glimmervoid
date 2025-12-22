FROM searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
# COPY searx/templates/simple/page_with_header.html /usr/local/searxng/searx/templates/simple/page_with_header.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png

USER root
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
