const employeeForm = document.querySelector("#employeeForm");
const reportForm = document.querySelector("#reportForm");
const reportDate = document.querySelector("#reportDate");
const employeeRows = document.querySelector("#employeeRows");
const reportRows = document.querySelector("#reportRows");
const employeeCount = document.querySelector("#employeeCount");
const todayLabel = document.querySelector("#todayLabel");
const toast = document.querySelector("#toast");

const dateFormatter = new Intl.DateTimeFormat("ja-JP", {
  year: "numeric",
  month: "long",
  day: "numeric",
  weekday: "short",
});

const timeFormatter = new Intl.DateTimeFormat("ja-JP", {
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function todayIso() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2400);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "通信に失敗しました");
  }
  return data;
}

function formatDateTime(value) {
  if (!value) return "-";
  return timeFormatter.format(new Date(value));
}

function renderEmployees(employees) {
  employeeCount.textContent = `${employees.length}名`;
  if (employees.length === 0) {
    employeeRows.innerHTML = `<tr><td class="empty" colspan="5">従業員はまだ登録されていません</td></tr>`;
    return;
  }

  employeeRows.innerHTML = employees
    .map(
      (employee) => `
        <tr>
          <td>${employee.id}</td>
          <td>${escapeHtml(employee.name)}</td>
          <td>${escapeHtml(employee.department)}</td>
          <td>${escapeHtml(employee.role)}</td>
          <td>
            <div class="actions">
              <button type="button" data-action="clock-in" data-id="${employee.id}">出勤</button>
              <button type="button" class="secondary" data-action="clock-out" data-id="${employee.id}">退勤</button>
            </div>
          </td>
        </tr>
      `,
    )
    .join("");
}

function renderReport(records) {
  if (records.length === 0) {
    reportRows.innerHTML = `<tr><td class="empty" colspan="4">選択日の勤怠記録はありません</td></tr>`;
    return;
  }

  reportRows.innerHTML = records
    .map((record) => {
      const isOpen = !record.clock_out;
      return `
        <tr>
          <td>${record.employee_id}</td>
          <td>${formatDateTime(record.clock_in)}</td>
          <td>${formatDateTime(record.clock_out)}</td>
          <td class="${isOpen ? "status-open" : "status-closed"}">${isOpen ? "勤務中" : "退勤済み"}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadEmployees() {
  renderEmployees(await request("/api/employees"));
}

async function loadReport() {
  const query = reportDate.value ? `?date=${encodeURIComponent(reportDate.value)}` : "";
  renderReport(await request(`/api/report${query}`));
}

employeeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(employeeForm);
  try {
    await request("/api/employees", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    employeeForm.reset();
    showToast("従業員を登録しました");
    await loadEmployees();
  } catch (error) {
    showToast(error.message);
  }
});

employeeRows.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const path = button.dataset.action === "clock-in" ? "/api/clock-in" : "/api/clock-out";
  try {
    await request(path, {
      method: "POST",
      body: JSON.stringify({ employee_id: button.dataset.id }),
    });
    showToast(button.dataset.action === "clock-in" ? "出勤を記録しました" : "退勤を記録しました");
    await loadReport();
  } catch (error) {
    showToast(error.message);
  }
});

reportForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await loadReport();
  } catch (error) {
    showToast(error.message);
  }
});

todayLabel.textContent = dateFormatter.format(new Date());
reportDate.value = todayIso();
loadEmployees().catch((error) => showToast(error.message));
loadReport().catch((error) => showToast(error.message));
