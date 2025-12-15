document.addEventListener('DOMContentLoaded', function() {
  // Lista degli URL da evidenziare - MODIFICA QUI
  const highlightUrls = [
    'openrailwaymap.org',
    // aggiungi altri URL qui
  ];
  
  // Trova tutti i risultati
  const results = document.querySelectorAll('#urls > div');
  
  results.forEach(function(resultDiv) {
    // Trova il link principale nel risultato
    const link = resultDiv.querySelector('a[href]');
    
    if (link) {
      const url = link.getAttribute('href');
      
      // Controlla se l'URL contiene uno degli URL da evidenziare
      highlightUrls.forEach(function(highlightUrl) {
        if (url.includes(highlightUrl)) {
          resultDiv.classList.add('highlight-url');
        }
      });
    }
  });
});
