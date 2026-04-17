window.addEventListener("load", async function () {
    try {
        const [highlightResponse, unwantedResponse, favoriteResponse] =
            await Promise.all([
                fetch("/static/custom/highlight_urls.json"),
                fetch("/static/custom/unwanted_urls.json"),
                fetch("/static/custom/favorite_urls.json"),
            ]);

        const highlightUrls = new Set(await highlightResponse.json());
        const unwantedUrls = new Set(await unwantedResponse.json());
        const favoriteUrls = new Set(await favoriteResponse.json());

        const categories = [
            {
                set: favoriteUrls,
                borderClass: "border-cust-border-favorite",
                badgeClass: "url-badge-favorite",
                label: "preferiti",
            },
            {
                set: highlightUrls,
                borderClass: "border-cust-border-highlight",
                badgeClass: "url-badge-highlight",
                label: "visitati",
            },
            {
                set: unwantedUrls,
                borderClass: "border-cust-border-unwanted",
                badgeClass: "url-badge-unwanted",
                label: "indesiderati",
            },
        ];

        const urlsContainer = document.getElementById("urls");
        if (!urlsContainer) return;

        urlsContainer.querySelectorAll("article").forEach(function (article) {
            const links = article.querySelectorAll("a[href]");
            const matched = [];

            categories.forEach(function (cat) {
                for (const link of links) {
                    if (cat.set.has(link.href)) {
                        matched.push(cat);
                        break;
                    }
                }
            });

            if (matched.length === 0) return;

            article.classList.remove("border-gray-800");
            article.classList.add("url-tagged");

            const badgeContainer = document.createElement("div");
            badgeContainer.className = "url-badges";

            matched.forEach(function (cat) {
                article.classList.add(cat.borderClass);
                const badge = document.createElement("span");
                badge.className = "url-badge " + cat.badgeClass;
                badge.textContent = cat.label;
                badgeContainer.appendChild(badge);
            });

            article.appendChild(badgeContainer);
        });
    } catch (error) {
        console.error("Errore nel caricamento degli URL:", error);
    }
});
