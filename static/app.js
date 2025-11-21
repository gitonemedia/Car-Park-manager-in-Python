const loginCard = document.getElementById("login-card");
const dashboard = document.getElementById("dashboard");
const logoutBtn = document.getElementById("logout-btn");
const toast = document.getElementById("toast");
const adminCard = document.querySelector(".admin-only");

const parkTable = document.getElementById("parked-table");
const txTable = document.getElementById("transactions-table");
const removeModal = document.getElementById("remove-modal");
const removeModalForm = document.getElementById("remove-modal-form");
const openRemoveModalBtn = document.getElementById("open-remove-modal");
const removeHoursInput = document.getElementById("remove-hours");
const removeAmountInput = document.getElementById("remove-amount");
const removeSpotInput = document.getElementById("remove-spot");
const searchForm = document.getElementById("search-form");
const searchResults = document.getElementById("search-results");
const commentModal = document.getElementById("comment-modal");
const commentForm = document.getElementById("comment-form");
const commentTextarea = document.getElementById("comment-text");
const commentSpotLabel = document.getElementById("comment-spot-label");

let currentRate = 0;
let amountTouched = false;
let latestState = null;
let commentSpot = null;

async function apiRequest(path, options = {}) {
  const opts = {
    method: options.method || "GET",
    headers: Object.assign(
      { "Content-Type": "application/json" },
      options.headers || {}
    ),
    credentials: "same-origin",
  };

  if (options.body && typeof options.body === "object") {
    opts.body = JSON.stringify(options.body);
  } else if (options.body) {
    opts.body = options.body;
  }

  const res = await fetch(path, opts);
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = {};
  }

  if (!res.ok) {
    const error = new Error(data.error || "Request failed");
    error.status = res.status;
    error.payload = data;
    throw error;
  }

  return data;
}

function showLogin() {
  dashboard.classList.add("hidden");
  logoutBtn.classList.add("hidden");
  loginCard.classList.remove("hidden");
}

function showToast(message, type = "info") {
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 4000);
}

function renderState(state) {
  latestState = state;
  loginCard.classList.add("hidden");
  dashboard.classList.remove("hidden");
  logoutBtn.classList.remove("hidden");
  currentRate = Number(state.rate_per_hour) || 0;
  amountTouched = false;
  removeHoursInput.value = "";
  removeAmountInput.value = "";
  if (searchResults) {
    searchResults.textContent = "Enter a plate to search.";
    searchResults.classList.add("muted");
  }
  if (searchResults) {
    searchResults.textContent = "Enter a plate to search.";
    searchResults.classList.add("muted");
  }

  document.getElementById("summary-user").textContent = state.current_user;
  document.getElementById("summary-role").textContent = state.is_admin
    ? "Admin"
    : "User";
  document.getElementById("summary-capacity").textContent = state.capacity;
  document.getElementById("summary-available").textContent =
    state.available_spots;
  document.getElementById("summary-rate").textContent = Number(
    state.rate_per_hour
  ).toFixed(2);
  document.getElementById("parked-count").textContent = state.parked_cars.length;

  adminCard.classList.toggle("hidden", !state.is_admin);
  document
    .querySelectorAll(".admin-only input[name='rate']")
    .forEach((input) => (input.value = state.rate_per_hour));

  const parkedRows = state.parked_cars
    .map(
      (car) => `<tr data-spot="${car.spot}">
        <td>${car.spot}</td>
        <td>${car.plate || "-"}</td>
        <td>${(car.time_in || "").slice(0, 19)}</td>
        <td>${(car.comments || "").replace(/\n/g, "<br>")}</td>
        <td>
          <div class="table-actions">
            <button type="button" class="link-btn" data-action="comment" data-spot="${car.spot}">Note</button>
            <button type="button" class="link-btn" data-action="remove" data-spot="${car.spot}">Remove</button>
          </div>
        </td>
      </tr>`
    )
    .join("");

  parkTable.innerHTML =
    parkedRows ||
    `<tr><td colspan="5" class="muted">No cars parked.</td></tr>`;

  const txRows = state.transactions
    .slice()
    .reverse()
    .map(
      (tx) => `<tr>
        <td>${tx.spot ?? "-"}</td>
        <td>${tx.plate || "-"}</td>
        <td>${(tx.time_in || "").slice(0, 19)}</td>
        <td>${(tx.time_out || "").slice(0, 19)}</td>
        <td>$${Number(tx.amount || 0).toFixed(2)}</td>
      </tr>`
    )
    .join("");

  txTable.innerHTML =
    txRows ||
    `<tr><td colspan="5" class="muted">No transactions.</td></tr>`;
}

async function refreshState() {
  try {
    const state = await apiRequest("/api/state");
    renderState(state);
  } catch (err) {
    if (err.status === 401) {
      showLogin();
    } else {
      showToast(err.message || "Failed to load state", "error");
    }
  }
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const username = form.username.value.trim();
  const password = form.password.value;
  try {
    await apiRequest("/api/login", {
      method: "POST",
      body: { username, password },
    });
    form.reset();
    showToast("Login successful");
    refreshState();
  } catch (err) {
    showToast(err.message || "Login failed", "error");
  }
});

logoutBtn.addEventListener("click", async () => {
  try {
    await apiRequest("/api/logout", { method: "POST" });
    showToast("Logged out");
  } catch (err) {
    showToast(err.message || "Logout failed", "error");
  } finally {
    showLogin();
  }
});

document.getElementById("park-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const plate = e.target.plate.value.trim();
  if (!plate) {
    showToast("License plate required", "error");
    return;
  }
  try {
    const res = await apiRequest("/api/park", {
      method: "POST",
      body: { plate },
    });
    showToast("Car parked");
    e.target.reset();
    renderState(res.state);
  } catch (err) {
    showToast(err.message || "Failed to park car", "error");
  }
});

function openRemoveModal(prefillSpot = "") {
  removeSpotInput.value = prefillSpot;
  removeHoursInput.value = "";
  removeAmountInput.value = "";
  amountTouched = false;
  removeModal.classList.remove("hidden");
  removeSpotInput.focus();
}

function closeRemoveModal() {
  removeModal.classList.add("hidden");
}

openRemoveModalBtn?.addEventListener("click", () => openRemoveModal());

removeModal.addEventListener("click", (e) => {
  const target = e.target;
  if (target.dataset.close === "remove-modal") {
    closeRemoveModal();
  }
});

removeAmountInput.addEventListener("input", () => {
  amountTouched = removeAmountInput.value.length > 0;
});

removeAmountInput.addEventListener("focus", () => {
  amountTouched = true;
});

removeHoursInput.addEventListener("input", () => {
  if (amountTouched) {
    return;
  }
  const hours = parseFloat(removeHoursInput.value);
  if (!isNaN(hours) && hours >= 0 && currentRate > 0) {
    removeAmountInput.value = (hours * currentRate).toFixed(2);
  } else if (!amountTouched) {
    removeAmountInput.value = "";
  }
});

removeModalForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const spot = Number(removeSpotInput.value);
  if (!Number.isInteger(spot)) {
    showToast("Spot number required", "error");
    return;
  }
  const hoursVal = removeHoursInput.value.trim();
  const amountVal = removeAmountInput.value.trim();
  const payload = { spot };
  if (hoursVal !== "") {
    payload.hours_override = Number(hoursVal);
  }
  if (amountVal !== "") {
    payload.amount_override = Number(amountVal);
  }
  try {
    const res = await apiRequest("/api/remove", {
      method: "POST",
      body: payload,
    });
    showToast("Car removed");
    closeRemoveModal();
    renderState(res.state);
  } catch (err) {
    showToast(err.message || "Failed to remove car", "error");
  }
});

parkTable.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const spot = btn.dataset.spot;
  if (btn.dataset.action === "comment") {
    const car = latestState?.parked_cars.find((c) => String(c.spot) === String(spot));
    openCommentModal(car);
  } else if (btn.dataset.action === "remove") {
    openRemoveModal(spot);
  }
});

function openCommentModal(car) {
  if (!car) {
    showToast("Unable to find that car", "error");
    return;
  }
  commentSpot = car.spot;
  commentTextarea.value = car.comments || "";
  commentSpotLabel.textContent = `Spot ${car.spot} — ${car.plate || "No registration"}`;
  commentModal.classList.remove("hidden");
  commentTextarea.focus();
}

function closeCommentModal() {
  commentModal.classList.add("hidden");
  commentSpot = null;
  commentTextarea.value = "";
}

commentModal?.addEventListener("click", (e) => {
  if (e.target.dataset.close === "comment-modal") {
    closeCommentModal();
  }
});

commentForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (commentSpot == null) {
    showToast("Spot not selected", "error");
    return;
  }
  try {
    const res = await apiRequest(`/api/spot/${commentSpot}/comments`, {
      method: "POST",
      body: { comments: commentTextarea.value },
    });
    showToast("Comments saved");
    closeCommentModal();
    renderState(res.state);
  } catch (err) {
    showToast(err.message || "Failed to save comments", "error");
  }
});

if (searchForm && searchResults) {
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!latestState) {
      showToast("State not loaded yet", "error");
      return;
    }
    const query = e.target.query.value.trim().toLowerCase();
    if (!query) {
      searchResults.textContent = "Enter a plate to search.";
      searchResults.classList.add("muted");
      return;
    }
    const matches = latestState.parked_cars.filter((car) =>
      (car.plate || "").toLowerCase().includes(query)
    );

    if (matches.length === 0) {
      searchResults.textContent = "No parked cars match that registration.";
      searchResults.classList.add("muted");
      return;
    }

    const list = matches
      .map(
        (car) => `
          <div class="search-hit">
            <div>
              <strong>${car.plate || "Unknown"}</strong> — Spot ${car.spot}<br>
              <span class="muted">${(car.time_in || "").slice(0, 19)}</span>
            </div>
            <div class="table-actions">
              <button type="button" class="link-btn" data-search-action="comment" data-spot="${car.spot}">Note</button>
              <button type="button" class="link-btn" data-search-action="remove" data-spot="${car.spot}">Remove</button>
            </div>
          </div>`
      )
      .join("");

    searchResults.innerHTML = list;
    searchResults.classList.remove("muted");
  });

  searchResults.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-search-action]");
    if (!btn) return;
    const spot = btn.dataset.spot;
    const car = latestState?.parked_cars.find((c) => String(c.spot) === String(spot));
    if (btn.dataset.search-action === "comment") {
      openCommentModal(car);
    } else {
      openRemoveModal(spot);
    }
  });
}

document.getElementById("rate-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const rate = Number(e.target.rate.value);
  if (!rate || rate <= 0) {
    showToast("Enter a valid rate", "error");
    return;
  }
  try {
    const res = await apiRequest("/api/rate", {
      method: "POST",
      body: { rate_per_hour: rate },
    });
    showToast("Rate updated");
    renderState(res.state);
  } catch (err) {
    showToast(err.message || "Failed to update rate", "error");
  }
});

document.getElementById("setup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const capacity = Number(e.target.capacity.value);
  if (!Number.isInteger(capacity) || capacity <= 0) {
    showToast("Capacity must be positive integer", "error");
    return;
  }
  if (!confirm("This will reset the car park. Continue?")) {
    return;
  }
  try {
    const res = await apiRequest("/api/setup", {
      method: "POST",
      body: { capacity },
    });
    showToast("Car park reset");
    renderState(res.state);
  } catch (err) {
    showToast(err.message || "Failed to reset park", "error");
  }
});

document.getElementById("save-btn").addEventListener("click", async () => {
  try {
    await apiRequest("/api/save", { method: "POST" });
    showToast("State saved");
  } catch (err) {
    showToast(err.message || "Failed to save state", "error");
  }
});

document.getElementById("load-btn").addEventListener("click", async () => {
  try {
    const res = await apiRequest("/api/load", { method: "POST" });
    showToast("State loaded");
    renderState(res.state);
  } catch (err) {
    showToast(err.message || "Failed to load state", "error");
  }
});

refreshState();

