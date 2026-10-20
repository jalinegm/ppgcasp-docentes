(function () {
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduz) return;
  document.querySelectorAll("[data-n]").forEach(function (el) {
    var alvo = parseInt(el.dataset.n, 10);
    var inicio = performance.now() + 300;
    var duracao = 1200;
    el.textContent = "0";
    function passo(t) {
      var p = Math.min(1, Math.max(0, (t - inicio) / duracao));
      el.textContent = Math.round(alvo * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(passo);
    }
    requestAnimationFrame(passo);
  });
})();
