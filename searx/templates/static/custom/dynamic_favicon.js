// Favicon dinamica: legge il seed da <meta name="favicon-seed"> e genera
// un identicon 5x5 simmetrico (mirror verticale) in stile DiceBear.
// base.html setta il seed = endpoint; le pagine che vogliono un seed
// diverso (es. results.html = query) overrridano il block `favicon_seed`.
(function () {
    var seedMeta = document.querySelector('meta[name="favicon-seed"]');
    var seed = seedMeta && seedMeta.content ? seedMeta.content.trim().toLowerCase() : '';
    if (!seed) return;

    function fnv1a(s) {
        var h = 0x811c9dc5;
        for (var i = 0; i < s.length; i++) {
            h ^= s.charCodeAt(i);
            h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
        }
        return h >>> 0;
    }

    function makeRng(seed) {
        var state = seed || 1;
        return function () {
            state ^= state << 13; state >>>= 0;
            state ^= state >>> 17;
            state ^= state << 5;  state >>>= 0;
            return state >>> 0;
        };
    }

    var rng = makeRng(fnv1a(seed));
    var color = '#d81b60';
    var rects = '';
    for (var y = 0; y < 5; y++) {
        for (var x = 0; x < 3; x++) {
            if ((rng() & 1) === 1) {
                rects += '<rect x="' + x + '" y="' + y + '" width="1" height="1" fill="' + color + '"/>';
                if (x < 2) {
                    rects += '<rect x="' + (4 - x) + '" y="' + y + '" width="1" height="1" fill="' + color + '"/>';
                }
            }
        }
    }

    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 5" shape-rendering="crispEdges">' + rects + '</svg>';
    var href = 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);

    function apply() {
        document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]').forEach(function (l) { l.remove(); });
        var link = document.createElement('link');
        link.rel = 'icon';
        link.type = 'image/svg+xml';
        link.href = href;
        document.head.appendChild(link);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', apply);
    } else {
        apply();
    }
})();
