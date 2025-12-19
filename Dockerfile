FROM searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY templates/static/themes/simple/highlight.css /usr/local/searxng/searx/static/themes/simple/highlight.css
COPY logo.svg /usr/local/searxng/searx/static/themes/simple/img/searxng.svg

USER root
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
