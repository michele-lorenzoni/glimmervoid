FROM searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY templates/simple/base.html /usr/local/searxng/searx/templates/simple/base.html
COPY templates/static/themes/simple/custom.css /usr/local/searxng/searx/static/themes/simple/custom.css
COPY templates/static/themes/simple/highlight-urls.js /usr/local/searxng/searx/static/themes/simple/highlight-urls.js

USER root
RUN chown -R searxng:searxng /etc/searxng/settings.yml
USER searxng
