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

  const colorize = () => {
    // Low disk: >90% usage (more than 90% filled = <10% free)
    document.querySelectorAll(".information-widget-resource .resource-usage > div").forEach((bar) => {
      const width = parseFloat(bar.style.width) || 0;
      const parent = bar.closest(".information-widget-resource");
      const label = parent?.querySelector(".pr-1")?.textContent?.toLowerCase() || "";
      const icon = parent?.querySelector("svg")?.outerHTML || "";

      bar.classList.remove("low-disk", "high-temp", "warning");

      // Disk: red if >90% full
      if (label.includes("disk") || icon.includes("HardDrive")) {
        if (width > 90) bar.classList.add("low-disk");
        else if (width > 75) bar.classList.add("warning");
      }

      // Temperature: red if >80°C (shown as >80% of bar if maxTemp=100)
      if (label.includes("temp") || icon.includes("Thermometer")) {
        if (width > 80) bar.classList.add("high-temp");
        else if (width > 60) bar.classList.add("warning");
      }

      // CPU: warning if >90%
      if (label.includes("cpu") || icon.includes("Cpu")) {
        if (width > 90) bar.classList.add("warning");
      }
    });
  };

  const start = () => {
    if (!document.body) return void setTimeout(start, 50);
    unwrap();
    colorize();
    const observer = new MutationObserver(() => {
      unwrap();
      colorize();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Re-check periodically for live data updates
    setInterval(colorize, 2000);
  };
  start();
})();
