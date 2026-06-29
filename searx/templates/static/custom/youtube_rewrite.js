// Riscrive i link dei risultati che iniziano con https://www.youtube.com/watch
// incapsulandoli nel viewer michael.team. Opt-in: attivo solo se la preferenza
// `yt-rewrite` (localStorage) vale "1". Salvata dal tab "User interface" delle
// preferenze. Il link viene passato GREZZO (letterale) nel parametro `yt=`.
(function () {
    "use strict";

    var PREFIX = "https://www.youtube.com/watch";
    var WRAP = "https://michael.team/yt/?yt=";

    function rewrite() {
        try {
            if (localStorage.getItem("yt-rewrite") !== "1") return;
        } catch (e) {
            return;
        }

        var urls = document.getElementById("urls");
        if (!urls) return;

        urls.querySelectorAll('a[href^="' + PREFIX + '"]').forEach(function (a) {
            if (a.dataset.ytWrapped) return;
            // getAttribute preserva l'URL esattamente come fornito da YouTube
            // (raw, con tutti i suoi ?v=…&list=…&t=… intatti).
            a.href = WRAP + a.getAttribute("href");
            a.dataset.ytWrapped = "1";
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", rewrite);
    } else {
        rewrite();
    }
})();
