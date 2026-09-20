mapfile -t files < <(git diff --cached --name-only)
for file in "${files[@]}"; do
    echo "$file"
    if [[ "$file" =~ "favorite_urls" ]]; then
        echo "DEBUG: match favorite_urls su $file"
        git commit -m "update: update favorite_urls file"
        break
    fi

    if [[ "$file" =~ "highlight_url" ]]; then
        echo "DEBUG: match highlight_url su $file"
        git commit -m "update: update highlight_url file"
        break
    fi

    if [[ "$file" =~ "ignored_urls" ]]; then
        echo "DEBUG: match ignored_urls su $file"
        git commit -m "update: update ignored_urls file"
        break
    fi

    if [[ "$file" =~ "unwanted_urls" ]]; then
        echo "DEBUG: match unwanted_urls su $file"
        git commit -m "update: update unwanted_urls file"
        break
    fi

    if [[ "$file" =~ "blocked_domains" ]]; then
        echo "DEBUG: match blocked_domains su $file"
        git commit -m "update: update blocked_domains file"
        break
    fi

    if [[ "$file" =~ "blocked_urls_prefixes" ]]; then
        echo "DEBUG: match blocked_urls_prefixes su $file"
        git commit -m "update: update blocked_urls_prefixes file"
        break
    fi
done