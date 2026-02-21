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
