(function () {
  function renderMath() {
    if (typeof katex === "undefined") {
      return;
    }

    const inline = document.querySelectorAll(".math-inline");
    const block = document.querySelectorAll(".math-block");

    inline.forEach((el) => {
      const tex = el.getAttribute("data-tex");
      if (!tex) return;
      katex.render(tex, el, { displayMode: false, throwOnError: false });
    });

    block.forEach((el) => {
      const tex = el.getAttribute("data-tex");
      if (!tex) return;
      katex.render(tex, el, { displayMode: true, throwOnError: false });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderMath);
  } else {
    renderMath();
  }
})();
