read -rp "Eseguire 'git add -A' prima del commit? (y/n) " risposta
if [[ "$risposta" =~ ^[Yy]$ ]]; then
    git add -A
fi

mapfile -t files < <(git diff --cached --name-only)
for file in "${files[@]}"; do
    if [[ "$file" =~ "favorite_urls" ]]; then
        git commit -m "update: update favorite_urls file"
        break
    fi

    if [[ "$file" =~ "highlight_url" ]]; then
        git commit -m "update: update highlight_url file"
        break
    fi

    if [[ "$file" =~ "ignored_urls" ]]; then
        git commit -m "update: update ignored_urls file"
        break
    fi

    if [[ "$file" =~ "unwanted_urls" ]]; then
        git commit -m "update: update unwanted_urls file"
        break
    fi

    if [[ "$file" =~ "blocked_domains" ]]; then
        git commit -m "update: update blocked_domains file"
        break
    fi

    if [[ "$file" =~ "blocked_urls_prefixes" ]]; then
        git commit -m "update: update blocked_urls_prefixes file"
        break
    fi
done