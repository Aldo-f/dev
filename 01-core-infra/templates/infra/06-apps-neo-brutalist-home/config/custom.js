// Unwrap info-widget links: gethomepage wraps info widgets (e.g. glances) in
// <a href="widget-url">. Our glances URL is a LAN-only endpoint
// (http://192.168.0.5:61208) that must not be exposed or clickable.
(function () {
  const unwrap = () => {
    document.querySelectorAll("a[href]").forEach((a) => {
      if (!a.querySelector(".information-widget-resource")) return;
      const parent = a.parentNode;
      while (a.firstChild) parent.insertBefore(a.firstChild, a);
      parent.removeChild(a);
    });
  };
  const start = () => {
    if (!document.body) return void setTimeout(start, 50);
    unwrap();
    new MutationObserver(unwrap).observe(document.body, {
      childList: true,
      subtree: true,
    });
  };
  start();
})();
