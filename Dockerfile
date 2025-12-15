FROM searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY templates/simple/results.html /usr/local/searxng/searx/templates/simple/results.html
COPY templates/static/themes/simple/custom.css /usr/local/searxng/searx/static/themes/simple/custom.css
COPY webapp_patch.py /tmp/webapp_patch.py

USER root

RUN chown -R searxng:searxng /etc/searxng/settings.yml

# Patch webapp.py per passare highlight_urls al template
RUN python3 /tmp/webapp_patch.py

USER searxng
