
FROM	searxng/searxng:latest
EXPOSE	8080
COPY	settings.yml.template	/tmp/settings.yml.template
COPY	blocked_domains.txt	/tmp/blocked_domains.txt
USER	root
RUN	set -e \
	&& echo "[INFO] Inizio generazione settings.yml" \
	&& > /tmp/domains_formatted.txt \
	&& while IFS= read -r domain || [ -n "$domain" ]; do     domain=$(echo "$domain" | sed 's/#.*$//' | xargs);     if [ -n "$domain" ]; then     echo "      - ${domain}" >> /tmp/domains_formatted.txt;     fi;     done < /tmp/blocked_domains.txt \
	&& sed '/{{BLOCKED_DOMAINS}}/r /tmp/domains_formatted.txt' /tmp/settings.yml.template |     sed '/{{BLOCKED_DOMAINS}}/d' > /etc/searxng/settings.yml \
	&& echo "[INFO] File settings.yml generato con successo!" \
	&& if [ ! -s /etc/searxng/settings.yml ]; then     echo "[ERROR] settings.yml è vuoto!";     exit 1;     fi \
	&& chown searxng:searxng /etc/searxng/settings.yml \
	&& rm -f /tmp/settings.yml.template /tmp/blocked_domains.txt /tmp/domains_formatted.txt
RUN	mkdir -p /usr/local/searxng/searx/static/custom \
	&& chown searxng:searxng /usr/local/searxng/searx/static/custom
RUN	mkdir -p /usr/local/searxng/searx/static/fonts \
	&& chown searxng:searxng /usr/local/searxng/searx/static/fonts
COPY	searx/templates/static/custom/	/usr/local/searxng/searx/static/custom/
COPY	searx/templates/static/fonts/	/usr/local/searxng/searx/static/fonts/
COPY	searx/templates/simple/filters/	/usr/local/searxng/searx/templates/simple/filters/
COPY	searx/templates/static/output.css	/usr/local/searxng/searx/static/output.css
COPY	searx/templates/static/themes/simple/highlight.css	/usr/local/searxng/searx/static/themes/simple/highlight.css
COPY	searx/templates/static/themes/simple/sxng-core.min.js	/usr/local/searxng/searx/static/themes/simple/sxng-core.min.js
COPY	searx/templates/static/themes/simple/img/favicon.png	/usr/local/searxng/searx/static/themes/simple/img/favicon.png
COPY	searx/templates/static/themes/simple/img/favicon.svg	/usr/local/searxng/searx/static/themes/simple/img/favicon.svg
COPY	searx/templates/static/themes/simple/img/favicon.svg.gz	/usr/local/searxng/searx/static/themes/simple/img/favicon.svg.gz
COPY	searx/templates/static/themes/simple/img/favicon.svg.br	/usr/local/searxng/searx/static/themes/simple/img/favicon.svg.br
COPY	searx/templates/simple/searxng-wordmark.min.svg	/usr/local/searxng/searx/templates/simple/searxng-wordmark.min.svg
COPY	searx/templates/simple/base_preferences.html	/usr/local/searxng/searx/templates/simple/base_preferences.html
COPY	searx/templates/simple/categories.html	/usr/local/searxng/searx/templates/simple/categories.html
COPY	searx/templates/simple/page_with_header.html	/usr/local/searxng/searx/templates/simple/page_with_header.html
COPY	searx/templates/simple/preferences.html	/usr/local/searxng/searx/templates/simple/preferences.html
COPY	searx/templates/simple/simple_search.html	/usr/local/searxng/searx/templates/simple/simple_search.html
COPY	searx/templates/simple/base_index.html	/usr/local/searxng/searx/templates/simple/base_index.html
COPY	searx/templates/simple/index.html	/usr/local/searxng/searx/templates/simple/index.html
COPY	searx/templates/simple/results.html	/usr/local/searxng/searx/templates/simple/results.html
COPY	searx/templates/simple/icons.html	/usr/local/searxng/searx/templates/simple/icons.html
COPY	searx/templates/simple/base.html	/usr/local/searxng/searx/templates/simple/base.html
COPY	searx/templates/simple/macros.html	/usr/local/searxng/searx/templates/simple/macros.html
COPY	searx/templates/simple/search.html	/usr/local/searxng/searx/templates/simple/search.html
COPY	searx/templates/simple/result_templates/videos.html	/usr/local/searxng/searx/templates/simple/result_templates/videos.html
COPY	searx/engines/brave_api.py	/usr/local/searxng/searx/engines/brave_api.py
COPY	searx/templates/simple/preferences/footer.html	/usr/local/searxng/searx/templates/simple/preferences/footer.html
COPY	searx/templates/simple/preferences/cookies.html	/usr/local/searxng/searx/templates/simple/preferences/cookies.html
COPY	searx/templates/simple/preferences/answerers.html	/usr/local/searxng/searx/templates/simple/preferences/answerers.html
COPY	searx/templates/simple/messages/no_cookies.html	/usr/local/searxng/searx/templates/simple/messages/no_cookies.html
USER	searxng
