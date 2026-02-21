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
                                "bg-red-700/50",
                                "border-red-600/50",
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
                                "bg-green-700/50",
                                "border-green-600/50",
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
                                "bg-yellow-700/50",
                                "border-yellow-600/50",
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
