FROM searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY searx/templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY searx/templates/simple/icons.html /usr/local/searxng/searx/templates/simple/icons.html
COPY searx/templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY logo.png /usr/local/searxng/searx/static/themes/simple/img/searxng.png
COPY templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css

USER root
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
