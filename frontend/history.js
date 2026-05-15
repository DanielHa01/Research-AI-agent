/**
 * History Sidebar Module
 * Renders a collapsible sidebar listing all saved research reports.
 * Users can click any entry to reload it, delete entries, or search.
 * Import this in index.html just before </body>.
 */

const API_URL = window.API_URL || "http://localhost:8000";

/**
 * Call once on page load to inject the sidebar and load history.
 */
async function initHistory() {
  injectSidebarHTML();
  await loadHistory();
}

function injectSidebarHTML() {
  const sidebar = document.createElement("div");
  sidebar.id = "history-sidebar";
  sidebar.innerHTML = `
    <div class="history-header">
      <span>🗂 Past Research</span>
      <button class="history-toggle" onclick="toggleSidebar()">✕</button>
    </div>
    <div class="history-search-row">
      <input
        id="history-search"
        type="text"
        placeholder="Search topics..."
        oninput="handleHistorySearch(this.value)"
        autocomplete="off"
      />
    </div>
    <div id="history-list" class="history-list">
      <p class="history-empty">Loading...</p>
    </div>
  `;
  document.body.prepend(sidebar);

  // Add toggle button to main content area
  const toggleBtn = document.createElement("button");
  toggleBtn.id = "history-open-btn";
  toggleBtn.textContent = "🗂 History";
  toggleBtn.onclick = toggleSidebar;
  document.querySelector("main").prepend(toggleBtn);
}

async function loadHistory(query = "") {
  const listEl = document.getElementById("history-list");
  if (!listEl) return;
  listEl.innerHTML = '<p class="history-empty">Loading...</p>';

  try {
    const url = query
      ? `${API_URL}/history/search/${encodeURIComponent(query)}`
      : `${API_URL}/history`;

    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to load history");
    const reports = await res.json();

    if (reports.length === 0) {
      listEl.innerHTML = '<p class="history-empty">No saved reports yet.</p>';
      return;
    }

    listEl.innerHTML = reports
      .map((r) => `
        <div class="history-item" data-id="${r.id}">
          <div class="history-item-topic" onclick="loadReportById(${r.id})">
            ${escapeHtml(r.topic)}
          </div>
          <div class="history-item-meta">
            ${formatDate(r.created_at)}
            <button class="history-delete-btn" onclick="deleteReport(${r.id}, event)">✕</button>
          </div>
        </div>
      `)
      .join("");
  } catch (err) {
    listEl.innerHTML = `<p class="history-empty">Error: ${err.message}</p>`;
  }
}

async function loadReportById(id) {
  try {
    const res = await fetch(`${API_URL}/history/${id}`);
    if (!res.ok) throw new Error("Report not found");
    const data = await res.json();

    // Reuse existing showReport and showSubQuestions functions from index.html
    if (typeof showSubQuestions === 'function') showSubQuestions(data.sub_questions);
    if (typeof showReport === 'function') showReport(data.report);

    // Scroll to report
    const reportContainer = document.getElementById("report-container");
    if (reportContainer) reportContainer.scrollIntoView({ behavior: "smooth" });

    // Close sidebar on mobile
    if (window.innerWidth < 768) toggleSidebar();
  } catch (err) {
    alert(`Could not load report: ${err.message}`);
  }
}

async function deleteReport(id, event) {
  event.stopPropagation();
  if (!confirm("Delete this report?")) return;

  try {
    const res = await fetch(`${API_URL}/history/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Delete failed");

    // Remove from DOM immediately
    const item = document.querySelector(`.history-item[data-id="${id}"]`);
    if (item) item.remove();

    // Show empty state if no items left
    const list = document.getElementById("history-list");
    if (list && !list.querySelector(".history-item")) {
      list.innerHTML = '<p class="history-empty">No saved reports yet.</p>';
    }
  } catch (err) {
    alert(`Could not delete: ${err.message}`);
  }
}

let searchTimeout;
function handleHistorySearch(value) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadHistory(value.trim()), 300);
}

function toggleSidebar() {
  const sidebar = document.getElementById("history-sidebar");
  if (sidebar) sidebar.classList.toggle("open");
}

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Initialize on page load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initHistory);
} else {
  initHistory();
}
