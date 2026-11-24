// Script do site (arquivo estático: sem JavaScript inline, compatível com a CSP).
(function () {
  // PWA: registra o service worker (o site pode ser instalado e abrir numa janela própria).
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(function () {});
  }
  // Notas de apresentação: o botão mostra/oculta; a escolha fica guardada neste navegador.
  var botao = document.querySelector("[data-alternar-apresentacao]");
  if (!botao) {
    return;
  }
  var chave = "apresentacao-oculta";
  var oculta = false;
  try { oculta = localStorage.getItem(chave) === "1"; } catch (erro) {}
  function aplicar() {
    document.querySelectorAll("[data-apresentacao]").forEach(function (nota) { nota.hidden = oculta; });
    botao.setAttribute("aria-pressed", String(!oculta));
    botao.textContent = oculta ? "mostrar notas de apresentação" : "ocultar notas de apresentação";
  }
  aplicar();
  botao.addEventListener("click", function () {
    oculta = !oculta;
    try { localStorage.setItem(chave, oculta ? "1" : "0"); } catch (erro) {}
    aplicar();
  });
})();
