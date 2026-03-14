window.addEventListener("load", async function () {
    try {
        // Carica gli URL dai file JSON
        const [highlightResponse, unwantedResponse, favoriteResponse] =
            await Promise.all([
                fetch("/static/custom/highlight_urls.json"),
                fetch("/static/custom/unwanted_urls.json"),
                fetch("/static/custom/favorite_urls.json"),
            ]);

        const highlightUrls = await highlightResponse.json();
        const unwantedUrls = await unwantedResponse.json();
        const favoriteUrls = await favoriteResponse.json();

        const urlsContainer = document.getElementById("urls");

        if (urlsContainer) {
            const articles = urlsContainer.querySelectorAll("article");

            articles.forEach(function (article) {
                const parentDiv = article.closest("div");
                if (!parentDiv) return;

                const links = article.querySelectorAll("a[href]");
                let matched = false;

                Array.from(links).forEach(function (link) {
                    if (matched) return;
                    const url = link.href;

                    // Check UNWANTED (rosso)
                    unwantedUrls.forEach(function (unwantedUrl) {
                        if (url === unwantedUrl) {
                            article.classList.remove(
                                "bg-gray-900",
                                "border-gray-800",
                            );
                            article.classList.add(
                                "bg-cust-element-unwanted",
                                "border-cust-border-unwanted",
                            );
                            matched = true;
                        }
                    });
                    if (matched) return;

                    // Check FAVORITE (verde)
                    favoriteUrls.forEach(function (favoriteUrl) {
                        if (url === favoriteUrl) {
                            article.classList.remove(
                                "bg-gray-900",
                                "border-gray-800",
                            );
                            article.classList.add(
                                "bg-cust-element-favorite",
                                "border-cust-border-favorite",
                            );
                            matched = true;
                        }
                    });
                    if (matched) return;

                    // Check HIGHLIGHT (arancione)
                    highlightUrls.forEach(function (highlightUrl) {
                        if (url === highlightUrl) {
                            article.classList.remove(
                                "bg-gray-900",
                                "border-gray-800",
                            );
                            article.classList.add(
                                "bg-cust-element-highlight",
                                "border-cust-border-highlight",
                            );
                            matched = true;
                        }
                    });
                });
            });
        }
    } catch (error) {
        console.error("Errore nel caricamento degli URL:", error);
    }
});
