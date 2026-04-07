document.querySelectorAll("article a").forEach((link) => {
    link.addEventListener("click", function (e) {
        // Trova il primo <article> genitore del link cliccato
        const articleAttivo = this.closest("article");

        if (articleAttivo) {
            // Rimuovi 'active' da TUTTI gli article
            document.querySelectorAll("article").forEach((article) => {
                article.classList.remove("border-sky-800");
            });

            // Aggiungi 'active' solo all'article cliccato
            articleAttivo.classList.add("border-sky-800");
        }
    });
});

// --- Keyboard navigation ---------------------------------------------------
(function () {
    const ACTIVE = "border-sky-800";
    const getArticles = () => Array.from(document.querySelectorAll("#urls article"));

    const isTyping = (el) =>
        el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable);

    const currentIndex = () => {
        const articles = getArticles();
        return articles.findIndex((a) => a.classList.contains(ACTIVE));
    };

    const setActive = (idx) => {
        const articles = getArticles();
        if (!articles.length) return;
        const i = Math.max(0, Math.min(idx, articles.length - 1));
        articles.forEach((a) => a.classList.remove(ACTIVE));
        articles[i].classList.add(ACTIVE);
        articles[i].scrollIntoView({ block: "nearest", behavior: "smooth" });
    };

    document.addEventListener("keydown", (e) => {
        // Esc: sempre attivo, anche dentro un input
        if (e.key === "Escape" && document.activeElement) {
            document.activeElement.blur();
            return;
        }
        if (isTyping(document.activeElement)) return;
        if (e.ctrlKey || e.metaKey || e.altKey) return;

        switch (e.key) {
            case "j":
            case "ArrowDown": {
                e.preventDefault();
                const i = currentIndex();
                setActive(i < 0 ? 0 : i + 1);
                break;
            }
            case "k":
            case "ArrowUp": {
                e.preventDefault();
                const i = currentIndex();
                setActive(i < 0 ? 0 : i - 1);
                break;
            }
            case "Enter": {
                const i = currentIndex();
                if (i < 0) return;
                const link = getArticles()[i].querySelector("a[href]");
                if (link) {
                    e.preventDefault();
                    link.click();
                }
                break;
            }
            case "/": {
                e.preventDefault();
                const search = document.querySelector('input[name="q"]');
                if (search) { search.focus(); search.select(); }
                break;
            }
            case "n": {
                const next = document.querySelector(".next_page button");
                if (next) next.click();
                break;
            }
            case "p": {
                const prev = document.querySelector(".previous_page button");
                if (prev) prev.click();
                break;
            }
        }
    });
})();
