/* Steel Works · vista del asistente (navegador). Dibuja los mensajes del motor (bot/engine.js):
 * texto, opciones, tarjetas con fotos reales, cotización y pago. La usan el sitio y la propuesta.
 *   const chat = SteelChat.mount(el, { foto: key => url, onTurn: (state, input) => {} });
 *   chat.send("Quiero un portón"); chat.play(["hola", "..."]); chat.reset(); */
(function (root) {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const md = s => esc(s).replace(/\*([^*\n]+)\*/g, "<b>$1</b>").replace(/\n/g, "<br>");
  const wait = ms => new Promise(r => setTimeout(r, ms));

  function mount(el, opt) {
    const B = root.SteelBot, foto = opt.foto, onTurn = opt.onTurn || (() => {});
    el.classList.add("sc");
    el.innerHTML = `<div class="sc-log" aria-live="polite"></div>
      <form class="sc-in"><input type="text" placeholder="Escriba aquí, con sus palabras…" aria-label="Mensaje"><button aria-label="Enviar">
      <svg viewBox="0 0 24 24" width="18" height="18"><path d="M4 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button></form>`;
    const log = el.querySelector(".sc-log"), form = el.querySelector("form"), input = form.querySelector("input");
    let state = null, busy = false;

    const add = (html, cls) => {
      const d = document.createElement("div");
      d.className = "sc-m " + cls; d.innerHTML = html; log.appendChild(d);
      requestAnimationFrame(() => d.classList.add("on"));
      log.scrollTo({ top: log.scrollHeight, behavior: opt.instant ? "instant" : "smooth" });
      return d;
    };
    const clearChoices = () => log.querySelectorAll(".sc-chips,.sc-cards").forEach(x => x.classList.add("used"));

    function render(m) {
      if (m.userImage) return add(`<img src="${foto(m.userImage)}" alt="Foto enviada por el cliente">`, "me pic");
      if (m.text) add(md(m.text), "bot");
      if (m.cards) {
        const d = add(m.cards.map(c => `<button class="sc-card" data-v="${esc(c.id)}">
          <span class="ph"><img src="${foto(c.img)}" alt=""></span>
          <span class="t">${esc(c.title)}</span><span class="s">${esc(c.sub)}</span>${c.price ? `<span class="p">${esc(c.price)}</span>` : ""}</button>`).join(""), "sc-cards");
        d.classList.toggle("one", m.cards.length === 1);
      }
      if (m.quote) {
        const q = m.quote;
        add(`<div class="q-h"><span>Cotización preliminar</span><b>${esc(q.n)}</b></div>
          ${q.proyecto ? `<div class="q-p">${q.img ? `<img src="${foto(q.img)}" alt="">` : ""}<div><b>${esc(q.proyecto)}</b><span>${esc(q.medidas)}${q.ciudad ? " · " + esc(q.ciudad) : ""}</span></div></div>` : ""}
          ${q.lines.map(l => `<div class="q-l"><img src="${foto(l.img)}" alt=""><span>${l.qty} × ${esc(l.name)}<small>${esc(l.unit)} c/u · ${esc(l.code)}</small></span><b>${esc(l.total)}</b></div>`).join("")}
          ${q.lines.length ? `<div class="q-t"><span>Piezas</span><b>${esc(q.piezas)}</b></div>` : ""}
          ${q.fabricacion ? `<div class="q-t f"><span>Fabricación</span><b>${esc(q.fabricacion)}</b></div>` : ""}`, "sc-quote");
      }
      if (m.pay) add(`<span>Pago seguro con tarjeta</span><b>${esc(m.pay.amount)}</b><i>Pagar ahora</i>`, "sc-pay");
      if (m.chips) add(m.chips.map(c => `<button data-v="${esc(c)}">${esc(c)}</button>`).join(""), "sc-chips");
    }

    async function send(text, shown) {
      if (busy || !text.trim()) return;
      busy = true; clearChoices();
      add(esc(shown || text), "me");
      const r = B.handle(state, text);
      state = r.state; onTurn(state, text);
      const typing = add("<i></i><i></i><i></i>", "bot typing");
      await wait(opt.instant ? 0 : 650);
      typing.remove();
      for (const m of r.messages) { render(m); if (!opt.instant) await wait(260); }
      busy = false;
    }
    function reset() {
      log.innerHTML = ""; state = null;
      const r = B.handle(null, "");
      state = r.state; r.messages.forEach(render); onTurn(state, "");
    }
    async function play(script, gap) {
      reset();
      for (const x of script) { await wait(gap || 900); await send(x, labelFor(x)); }
    }
    const labelFor = v => { const b = log.querySelector(`.sc-cards:not(.used) [data-v="${CSS.escape(v)}"] .t`); return b ? b.textContent : v; };

    log.addEventListener("click", e => {
      const b = e.target.closest("button[data-v]");
      if (b && !b.closest(".used")) send(b.dataset.v, b.querySelector(".t") ? b.querySelector(".t").textContent : b.dataset.v);
    });
    form.addEventListener("submit", e => { e.preventDefault(); const v = input.value; input.value = ""; send(v); });
    reset();
    return { send: (t, shown) => send(t, shown || labelFor(t)), play, reset, get state() { return state; } };
  }
  root.SteelChat = { mount };
})(typeof self !== "undefined" ? self : this);
