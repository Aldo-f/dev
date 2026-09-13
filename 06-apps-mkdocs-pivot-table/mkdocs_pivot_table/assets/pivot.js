/**
 * mkdocs-pivot-table — Interactive sortable/filterable comparison tables
 *
 * Features:
 *   - Click headers to sort ascending/descending
 *   - Drag columns to reorder
 *   - Gear icon (⚙️) opens settings panel
 *   - Sort by column
 *   - Hide/show columns and rows
 *   - Swap rows/columns
 *   - Reset state
 *   - State saved to URL query params (shareable links)
 */
(function() {
  "use strict";

  if (window.__pivotTableInit) return;
  window.__pivotTableInit = true;

  // ── State Management ────────────────────────────────────────────────────────

  function getState(tableId) {
    const urlParams = new URLSearchParams(location.search);
    let hidden = urlParams.get("hide")
      ? urlParams.get("hide").split(",").filter(Boolean)
      : [];
    let hiddenRows = urlParams.get("hiderows")
      ? urlParams.get("hiderows").split(",").filter(Boolean)
      : [];
    let swapped = urlParams.get("swap") === "1";
    let sort = null;
    const sortParam = urlParams.get("sort");
    if (sortParam) {
      try { sort = JSON.parse(sortParam); } catch(e) { sort = null; }
    }

    // Override with localStorage if available
    const saved = localStorage.getItem("pivot_table_state_" + tableId);
    if (saved) {
      try {
        const s = JSON.parse(saved);
        if (Array.isArray(s.hidden)) hidden = s.hidden;
        if (Array.isArray(s.hiddenRows)) hiddenRows = s.hiddenRows;
        if (typeof s.swapped === "boolean") swapped = s.swapped;
        if (s.sort) sort = s.sort;
      } catch (e) { /* ignore corrupt state */ }
    }

    return {
      hidden: new Set(hidden),
      hiddenRows: new Set(hiddenRows),
      swapped: swapped,
      sort: sort || null
    };
  }

  function saveState(tableId, state) {
    const hiddenArr = Array.from(state.hidden);
    const hiddenRowsArr = Array.from(state.hiddenRows);
    const params = new URLSearchParams();
    if (hiddenArr.length) params.set("hide", hiddenArr.join(","));
    if (hiddenRowsArr.length) params.set("hiderows", hiddenRowsArr.join(","));
    if (state.swapped) params.set("swap", "1");
    if (state.sort) params.set("sort", JSON.stringify(state.sort));
    history.replaceState(null, "", location.pathname + (params.toString() ? "?" + params.toString() : ""));
    localStorage.setItem(
      "pivot_table_state_" + tableId,
      JSON.stringify({
        hidden: hiddenArr,
        hiddenRows: hiddenRowsArr,
        swapped: state.swapped,
        sort: state.sort
      })
    );
  }

  // ── Helpers ─────────────────────────────────────────────────────────────────

  function getColKey(headerText) {
    return headerText.toLowerCase().replace(/\s+/g, "");
  }

  function getRowKey(firstCell) {
    return firstCell.toLowerCase().replace(/\s+/g, "");
  }

  // ── Rendering ───────────────────────────────────────────────────────────────

  function render(table, state) {
    const thead = table.querySelector("thead tr");
    const tbody = table.querySelector("tbody");
    if (!thead || !tbody) return;

    // Store original data on first render
    if (!table._original) {
      table._original = {
        headers: Array.from(thead.querySelectorAll("th")).map(h => h.textContent.trim()),
        rows: Array.from(tbody.querySelectorAll("tr")).map(tr =>
          Array.from(tr.children).map(td => td.textContent.trim())
        )
      };
    }

    const origHeaders = table._original.headers;
    const origRows = table._original.rows;

    thead.innerHTML = "";
    tbody.innerHTML = "";

    if (state.swapped) {
      // Swapped view: rows become columns, columns become rows
      const th0 = document.createElement("th");
      th0.textContent = "Attribute";
      thead.appendChild(th0);

      // Show rows that are NOT hidden
      const visibleTools = origRows.filter(r => !state.hiddenRows.has(getRowKey(r[0])));
      visibleTools.forEach(row => {
        const th = document.createElement("th");
        th.textContent = row[0];
        thead.appendChild(th);
      });

      // Show columns that are NOT hidden
      const labels = origHeaders.slice(1);
      labels.forEach((label, i) => {
        const colKey = getColKey(label);
        if (state.hidden.has(colKey)) return;

        const tr = document.createElement("tr");
        const td0 = document.createElement("td");
        td0.textContent = label;
        tr.appendChild(td0);

        visibleTools.forEach(row => {
          const td = document.createElement("td");
          td.textContent = row[i + 1];
          tr.appendChild(td);
        });

        tbody.appendChild(tr);
      });
    } else {
      // Normal view
      const visibleCols = origHeaders.slice(1).map((h, i) => ({ key: getColKey(h), header: h }));
      
      // Sort columns if needed
      const sortedCols = [...visibleCols].sort((a, b) => {
        if (!state.sort) return 0;
        if (state.sort.colKey === a.key) return state.sort.dir === "asc" ? -1 : 1;
        if (state.sort.colKey === b.key) return state.sort.dir === "asc" ? 1 : -1;
        return 0;
      });

      // Always show first column
      const firstTh = document.createElement("th");
      firstTh.textContent = origHeaders[0];
      thead.appendChild(firstTh);

      sortedCols.forEach(({ key, header }, index) => {
        if (state.hidden.has(key)) return;
        const th = document.createElement("th");
        th.textContent = header;
        th.setAttribute("data-key", key);
        if (state.sort && state.sort.colKey === key) {
          th.classList.add(state.sort.dir === "asc" ? "sorted-asc" : "sorted-desc");
        }
        th.addEventListener("click", () => {
          const s = getState(table.id);
          if (s.sort && s.sort.colKey === key) {
            // Toggle sort direction
            s.sort.dir = s.sort.dir === "asc" ? "desc" : "asc";
          } else {
            s.sort = { colKey: key, dir: "asc" };
          }
          saveState(table.id, s);
          render(table, s);
        });
        thead.appendChild(th);
      });

      const visibleRows = origRows.filter(r => !state.hiddenRows.has(getRowKey(r[0])));
      visibleRows.forEach(row => {
        const tr = document.createElement("tr");
        const td0 = document.createElement("td");
        td0.textContent = row[0];
        tr.appendChild(td0);

        let colIndex = 1;
        visibleCols.forEach(({ key, header }, origIndex) => {
          if (state.hidden.has(key)) return;
          const td = document.createElement("td");
          td.textContent = row[origIndex + 1];
          tr.appendChild(td);
          colIndex++;
        });

        tbody.appendChild(tr);
      });
    }

    // Reinitialize drag and drop after re-render
    initDragDrop(table);
    
    // Reopen settings if panel was open
    const settingsPanel = table.closest(".pivot-table-wrap").querySelector(".pivot-settings");
    if (settingsPanel && settingsPanel.classList.contains("pivot-open")) {
      renderSettings(table, state);
    }
  }

  // ── Settings Panel ──────────────────────────────────────────────────────────

  function createSettingsPanel(table, state) {
    const wrap = table.closest(".pivot-table-wrap");
    let panel = wrap.querySelector(".pivot-settings");
    
    if (panel) {
      panel.remove();
      panel = null;
    }
    
    panel = document.createElement("div");
    panel.className = "pivot-settings";
    panel.setAttribute("data-for", table.id);
    
    // Close button
    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "pivot-settings-close";
    closeBtn.innerHTML = "✕";
    closeBtn.title = "Close settings";
    closeBtn.addEventListener("click", () => {
      panel.classList.remove("pivot-open");
    });
    panel.appendChild(closeBtn);
    
    // Title
    const title = document.createElement("h4");
    title.className = "pivot-settings-title";
    title.textContent = "Table Settings";
    panel.appendChild(title);
    
    // Sort section
    const sortSection = createSortSection(table, state);
    panel.appendChild(sortSection);
    
    // Columns section
    const colSection = createToggleSection(table, state, "Columns", state.hidden, "hide");
    panel.appendChild(colSection);
    
    // Rows section
    const rowSection = createToggleSection(table, state, "Rows", state.hiddenRows, "hiderows");
    panel.appendChild(rowSection);
    
    // Swap button
    const swapBtn = document.createElement("button");
    swapBtn.type = "button";
    swapBtn.className = "pivot-settings-btn";
    swapBtn.textContent = state.swapped ? "⟲ Switch Back to Normal View" : "⟶ Swap Rows/Columns";
    swapBtn.addEventListener("click", () => {
      const s = getState(table.id);
      s.swapped = !s.swapped;
      saveState(table.id, s);
      render(table, s);
      renderSettings(table, s);
    });
    panel.appendChild(swapBtn);
    
    // Reset button
    const resetBtn = document.createElement("button");
    resetBtn.type = "button";
    resetBtn.className = "pivot-settings-btn pivot-settings-btn-reset";
    resetBtn.textContent = "↺ Reset All";
    resetBtn.addEventListener("click", () => {
      const s = getState(table.id);
      s.hidden = new Set();
      s.hiddenRows = new Set();
      s.swapped = false;
      s.sort = null;
      saveState(table.id, s);
      render(table, s);
      panel.classList.remove("pivot-open");
    });
    panel.appendChild(resetBtn);
    
    wrap.appendChild(panel);
    return panel;
  }

  function createSortSection(table, state) {
    const section = document.createElement("div");
    section.className = "pivot-settings-section";
    
    const label = document.createElement("label");
    label.className = "pivot-settings-label";
    label.textContent = "Sort:";
    section.appendChild(label);
    
    const origHeaders = table._original?.headers || [];
    
    // Sort by column selector
    const select = document.createElement("select");
    select.className = "pivot-settings-select";
    
    const noneOption = document.createElement("option");
    noneOption.value = "";
    noneOption.textContent = "None";
    select.appendChild(noneOption);
    
    origHeaders.slice(1).forEach(h => {
      const opt = document.createElement("option");
      opt.value = getColKey(h);
      opt.textContent = h;
      select.appendChild(opt);
    });
    
    if (state.sort) {
      select.value = state.sort.colKey;
    }
    
    select.addEventListener("change", () => {
      const s = getState(table.id);
      if (select.value) {
        s.sort = { colKey: select.value, dir: s.sort?.dir || "asc" };
      } else {
        s.sort = null;
      }
      saveState(table.id, s);
      render(table, s);
      // Update sort direction display
      const dirBtn = section.querySelector(".pivot-settings-dir");
      if (dirBtn && s.sort) {
        dirBtn.textContent = s.sort.dir === "asc" ? "↑" : "↓";
        dirBtn.title = "Switch to " + (s.sort.dir === "asc" ? "descending" : "ascending");
      }
    });
    section.appendChild(select);
    
    // Sort direction button
    if (state.sort) {
      const dirBtn = document.createElement("button");
      dirBtn.type = "button";
      dirBtn.className = "pivot-settings-dir";
      dirBtn.textContent = state.sort.dir === "asc" ? "↑" : "↓";
      dirBtn.title = "Switch to " + (state.sort.dir === "asc" ? "descending" : "ascending");
      dirBtn.addEventListener("click", () => {
        const s = getState(table.id);
        if (s.sort) {
          s.sort.dir = s.sort.dir === "asc" ? "desc" : "asc";
          saveState(table.id, s);
          render(table, s);
          dirBtn.textContent = s.sort.dir === "asc" ? "↑" : "↓";
        }
      });
      section.appendChild(dirBtn);
    }
    
    return section;
  }

  function createToggleSection(table, state, title, hiddenSet, paramKey) {
    const section = document.createElement("div");
    section.className = "pivot-settings-section";
    
    const label = document.createElement("label");
    label.className = "pivot-settings-label";
    label.textContent = title + ":";
    section.appendChild(label);
    
    const items = title === "Columns" 
      ? table._original?.headers.slice(1) || [] 
      : table._original?.rows.map(r => r[0]) || [];
    
    items.forEach(item => {
      const key = getColKey(item) || getRowKey(item);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pivot-settings-toggle" + (hiddenSet.has(key) ? " pivot-settings-toggle-hidden" : "");
      btn.textContent = item;
      btn.title = hiddenSet.has(key) ? "Show " + item : "Hide " + item;
      
      btn.addEventListener("click", () => {
        const s = getState(table.id);
        if (hiddenSet.has(key)) {
          hiddenSet.delete(key);
        } else {
          hiddenSet.add(key);
        }
        saveState(table.id, s);
        render(table, s);
        // Update button state
        btn.classList.toggle("pivot-settings-toggle-hidden", hiddenSet.has(key));
      });
      
      section.appendChild(btn);
    });
    
    return section;
  }

  function renderSettings(table, state) {
    const panel = table.closest(".pivot-table-wrap").querySelector(".pivot-settings");
    if (!panel) return;
    
    // Destroy and recreate to keep state accurate
    panel.remove();
    createSettingsPanel(table, state);
  }

  // ── Gear Button ─────────────────────────────────────────────────────────────

  function createGearButton(table) {
    const wrap = table.closest(".pivot-table-wrap");
    const existing = wrap.querySelector(".pivot-gear-btn");
    if (existing) existing.remove();
    
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "pivot-gear-btn";
    btn.title = "Table settings";
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7.5 1C7.22 1 7 1.22 7 1.5V2.5C7 2.78 7.22 3 7.5 3H8.5C8.78 3 9 2.78 9 2.5V1.5C9 1.22 8.78 1 8.5 1H7.5ZM5 3C4.72 3 4.5 3.22 4.5 3.5V4.5C4.5 4.78 4.72 5 5 5H6C6.28 5 6.5 4.78 6.5 4.5V3.5C6.5 3.22 6.28 3 6 3H5ZM10 3C9.72 3 9.5 3.22 9.5 3.5V4.5C9.5 4.78 9.72 5 10 5H11C11.28 5 11.5 4.78 11.5 4.5V3.5C11.5 3.22 11.28 3 11 3H10ZM4.5 6C4.22 6 4 6.22 4 6.5V7.5C4 7.78 4.22 8 4.5 8H5.5C5.78 8 6 7.78 6 7.5V6.5C6 6.22 5.78 6 5.5 6H4.5ZM10.5 6C10.22 6 10 6.22 10 6.5V7.5C10 7.78 10.22 8 10.5 8H11.5C11.78 8 12 7.78 12 7.5V6.5C12 6.22 11.78 6 11.5 6H10.5ZM5 9C4.72 9 4.5 9.22 4.5 9.5V10.5C4.5 10.78 4.72 11 5 11H6C6.28 11 6.5 10.78 6.5 10.5V9.5C6.5 9.22 6.28 9 6 9H5ZM10 9C9.72 9 9.5 9.22 9.5 9.5V10.5C9.5 10.78 9.72 11 10 11H11C11.28 11 11.5 10.78 11.5 10.5V9.5C11.5 9.22 11.28 9 11 9H10ZM7 11C7 10.72 7.22 10.5 7.5 10.5H8.5C8.78 10.5 9 10.72 9 11V12C9 12.28 8.78 12.5 8.5 12.5H7.5C7.22 12.5 7 12.28 7 12V11ZM7.5 0C6.4 0 5.5 0.9 5.5 2V2.5H4.5C3.39 2.5 2.5 3.39 2.5 4.5V5H2C0.9 5 0 5.9 0 7V7.5H0.5C0.5 8.61 1.39 9.5 2.5 9.5H3V10.5C3 11.61 3.89 12.5 5 12.5H5.5V13.5C5.5 14.61 6.39 15.5 7.5 15.5H8.5C9.61 15.5 10.5 14.61 10.5 13.5V12.5H11C12.11 12.5 13 11.61 13 10.5V10H13.5C14.61 10 15.5 9.11 15.5 8V7.5C15.5 6.39 14.61 5.5 13.5 5.5H13V5C13 3.89 12.11 3 11 3H10.5V2.5C10.5 1.39 9.61 0.5 8.5 0.5H7.5V0Z" fill="currentColor"/>
    </svg>`;
    
    let panel = null;
    
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      
      if (!panel) {
        panel = createSettingsPanel(table, getState(table.id));
      }
      
      panel.classList.toggle("pivot-open");
      btn.classList.toggle("pivot-gear-active");
    });
    
    wrap.appendChild(btn);
    return btn;
  }

  // ── Column Reordering (Drag & Drop) ─────────────────────────────────────────

  function initDragDrop(table) {
    const thead = table.querySelector("thead tr");
    if (!thead) return;

    let dragSrcEl = null;

    thead.querySelectorAll("th[data-key]").forEach(th => {
      th.draggable = true;

      th.addEventListener("dragstart", function(e) {
        dragSrcEl = this;
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/html", this.innerHTML);
        this.classList.add("dragging");
      });

      th.addEventListener("dragover", function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        this.classList.add("drag-over");
      });

      th.addEventListener("dragleave", function() {
        this.classList.remove("drag-over");
      });

      th.addEventListener("drop", function(e) {
        e.stopPropagation();
        e.preventDefault();

        if (dragSrcEl !== this) {
          const rows = table.querySelectorAll("tbody tr, thead tr");
          rows.forEach(row => {
            const cells = Array.from(row.children).filter(c => c !== rows[0]?.children[0]);
            const srcIdx = cells.indexOf(dragSrcEl);
            const destIdx = cells.indexOf(this);
            if (srcIdx > -1 && destIdx > -1) {
              if (srcIdx < destIdx) {
                this.after(dragSrcEl);
              } else {
                this.before(dragSrcEl);
              }
            }
          });
        }

        this.classList.remove("drag-over");
        dragSrcEl.classList.remove("dragging");
      });

      th.addEventListener("dragend", function() {
        this.classList.remove("dragging");
        thead.querySelectorAll("th").forEach(h => h.classList.remove("drag-over"));
      });
    });
  }

  // ── Initialization ──────────────────────────────────────────────────────────

  function init() {
    document.querySelectorAll("table.pivot-table").forEach(table => {
      const tableId = table.id;
      if (!tableId) return;

      const state = getState(tableId);
      
      // Create gear button
      createGearButton(table);

      // Initialize drag and drop
      initDragDrop(table);

      // Initial render
      render(table, state);
    });
    
    // Close settings when clicking outside
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".pivot-gear-btn") && !e.target.closest(".pivot-settings")) {
        document.querySelectorAll(".pivot-settings.pivot-open").forEach(panel => {
          panel.classList.remove("pivot-open");
        });
        document.querySelectorAll(".pivot-gear-btn.pivot-gear-active").forEach(btn => {
          btn.classList.remove("pivot-gear-active");
        });
      }
    });
  }

  // Start when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
