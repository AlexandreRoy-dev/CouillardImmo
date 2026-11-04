/* Affiche les inscriptions d'un courtier à partir de data/listings-*.json */
(function () {
  function fmtPrix(n) {
    return new Intl.NumberFormat('fr-CA', { maximumFractionDigits: 0 }).format(n) + ' $';
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function card(l) {
    var media = l.photo
      ? '<img src="' + esc(l.photo) + '" alt="' + esc(l.adresse + ', ' + l.ville) + '" loading="lazy">'
      : '<div class="listing-placeholder"><i class="bi bi-house-door"></i><span>Photos sur Centris</span></div>';
    var badge = l.nouveau ? '<span class="listing-badge">Nouveau</span>' : '';
    var specs = [];
    if (l.chambres) specs.push('<span><i class="bi bi-door-closed"></i> ' + esc(l.chambres) + ' ch.</span>');
    if (l.sallesDeBain) specs.push('<span><i class="bi bi-droplet"></i> ' + esc(l.sallesDeBain) + ' sdb</span>');
    return '<div class="col-md-6 col-lg-4">' +
      '<a class="listing-card" href="' + esc(l.url) + '" target="_blank" rel="noopener">' +
      '<div class="listing-media">' + media + badge + '</div>' +
      '<div class="listing-body">' +
      '<div class="listing-price">' + fmtPrix(l.prix) + '</div>' +
      '<div class="listing-type">' + esc(l.type) + '</div>' +
      '<div class="listing-address">' + esc(l.adresse) + '</div>' +
      '<div class="listing-city"><i class="bi bi-geo-alt"></i> ' + esc(l.ville) + (l.region ? ', ' + esc(l.region) : '') + '</div>' +
      '<div class="listing-specs">' + specs.join('') + '</div>' +
      '<div class="listing-footer"><span>Centris n° ' + esc(l.mls) + '</span><span class="listing-cta">Voir la fiche <i class="bi bi-arrow-right"></i></span></div>' +
      '</div></a></div>';
  }
  document.querySelectorAll('[data-listings]').forEach(function (el) {
    var grid = el.querySelector('.listings-grid');
    fetch(el.getAttribute('data-listings'), { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var items = d.inscriptions || [];
        grid.innerHTML = items.length
          ? items.map(card).join('')
          : '<div class="col-12 listings-empty">Aucune propriété affichée pour le moment. Consultez ma page Centris pour les inscriptions à jour.</div>';
      })
      .catch(function () {
        grid.innerHTML = '<div class="col-12 listings-empty">Les propriétés n\'ont pas pu être chargées. Consultez ma page Centris.</div>';
      });
  });
})();
