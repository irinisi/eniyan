const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

const app = document.getElementById("app");
const tabs = document.querySelectorAll(".tabbar button");

const STATUS_LABELS = {
  todo: "Todo",
  in_progress: "In Progress",
  review: "Review",
  done: "Done",
};

function setActiveTab(activeBtn) {
  tabs.forEach((b) => {
    const isActive = b === activeBtn;
    b.classList.toggle("active", isActive);
    b.classList.toggle("tos-hint", !isActive);
    b.classList.toggle("text-[var(--button)]", isActive);
  });
}

tabs.forEach((btn) => {
  btn.addEventListener("click", () => {
    setActiveTab(btn);
    render(btn.dataset.tab);
  });
});

async function render(tab) {
  app.innerHTML = "<p>Загрузка...</p>";
  try {
    if (tab === "home") return renderHome();
    if (tab === "tasks") return renderTasks();
    if (tab === "projects") return renderProjects();
    if (tab === "knowledge") return renderKnowledge();
    if (tab === "profile") return renderProfile();
  } catch (err) {
    app.innerHTML = `<p>Ошибка: ${err.message}</p>`;
  }
}

async function renderHome() {
  const tasks = await api.getTasks();
  const today = new Date().toISOString().slice(0, 10);
  const dueToday = tasks.filter((t) => t.due === today && t.status !== "done");
  const overdue = tasks.filter((t) => t.due && t.due < today && t.status !== "done");
  const projects = await api.getProjects();

  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Главная</h1>
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2">Сегодня (${dueToday.length})</h2>
    ${dueToday.map(taskCard).join("") || emptyState("Нет задач")}
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2 mt-5">Просрочено (${overdue.length})</h2>
    ${overdue.map(taskCard).join("") || emptyState("Нет просроченных задач")}
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2 mt-5">Активные проекты</h2>
    ${projects.map(projectCard).join("") || emptyState("Нет проектов")}
  `;
}

function emptyState(text) {
  return `<p class="tos-hint text-sm py-2">${text}</p>`;
}

async function renderTasks() {
  const tasks = await api.getTasks();
  const columns = ["todo", "in_progress", "review", "done"];
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Задачи</h1>
    <button class="tos-accent w-full rounded-lg py-2.5 px-4 text-sm font-medium mb-4 hover:opacity-90 transition" id="new-task-btn">➕ Новая задача</button>
    <div class="flex gap-3 overflow-x-auto pb-2">
      ${columns
        .map(
          (status) => `
        <div class="min-w-[230px] flex-1">
          <h3 class="text-xs font-semibold tos-hint uppercase tracking-wide mb-2">${STATUS_LABELS[status]}</h3>
          ${tasks
            .filter((t) => t.status === status)
            .map(taskCard)
            .join("")}
        </div>`
        )
        .join("")}
    </div>
  `;
  document.getElementById("new-task-btn").addEventListener("click", renderNewTaskForm);
  app.querySelectorAll(".card[data-task-id]").forEach((card) => {
    card.addEventListener("click", () => renderTaskDetail(card.dataset.taskId));
  });
}

function taskCard(task) {
  return `
    <div class="card tos-surface rounded-xl p-4 mb-3 shadow-sm hover:shadow-md transition cursor-pointer" data-task-id="${task.id}">
      <div class="font-medium">${escapeHtml(task.title)}</div>
      <div class="tos-hint text-xs mt-1">${task.assignee || "без исполнителя"} · ${task.due || "без срока"}</div>
      <span class="tos-accent inline-block text-[11px] font-medium px-2.5 py-0.5 rounded-full mt-2">${task.priority}</span>
    </div>
  `;
}

async function renderTaskDetail(taskId) {
  const task = await api.getTask(taskId);
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-2">${escapeHtml(task.title)}</h1>
    <p class="text-sm mb-4">${escapeHtml(task.description || "")}</p>
    <div class="tos-surface rounded-xl p-4 mb-4 space-y-1 text-sm">
      <div><span class="tos-hint">Исполнитель:</span> ${task.assignee || "—"}</div>
      <div><span class="tos-hint">Проект:</span> ${task.project || "—"}</div>
      <div><span class="tos-hint">Срок:</span> ${task.due || "—"}</div>
      <div><span class="tos-hint">Статус:</span> ${STATUS_LABELS[task.status]}</div>
    </div>
    <button class="tos-accent w-full rounded-lg py-2.5 px-4 text-sm font-medium mb-2 hover:opacity-90 transition" id="complete-btn">Завершить</button>
    <button class="w-full rounded-lg py-2.5 px-4 text-sm font-medium mb-2 border tos-border text-red-600 hover:bg-red-50 transition" id="delete-btn">Удалить</button>
    <button class="w-full rounded-lg py-2.5 px-4 text-sm font-medium tos-hint" id="back-btn">← Назад</button>
  `;
  document.getElementById("complete-btn").addEventListener("click", async () => {
    await api.updateTask(taskId, { status: "done" });
    renderTasks();
  });
  document.getElementById("delete-btn").addEventListener("click", async () => {
    await api.deleteTask(taskId);
    renderTasks();
  });
  document.getElementById("back-btn").addEventListener("click", renderTasks);
}

const FORM_FIELD = "tos-input w-full rounded-lg border px-3 py-2 mb-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--button)]";

function renderNewTaskForm() {
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Новая задача</h1>
    <input id="f-title" class="${FORM_FIELD}" placeholder="Название" />
    <textarea id="f-description" class="${FORM_FIELD}" placeholder="Описание"></textarea>
    <input id="f-assignee" class="${FORM_FIELD}" placeholder="Исполнитель" />
    <input id="f-due" class="${FORM_FIELD}" type="date" />
    <input id="f-project" class="${FORM_FIELD}" placeholder="Проект (id)" />
    <select id="f-priority" class="${FORM_FIELD}">
      <option value="low">Низкий приоритет</option>
      <option value="medium" selected>Средний приоритет</option>
      <option value="high">Высокий приоритет</option>
    </select>
    <button class="tos-accent w-full rounded-lg py-2.5 px-4 text-sm font-medium hover:opacity-90 transition" id="save-btn">Сохранить</button>
  `;
  document.getElementById("save-btn").addEventListener("click", async () => {
    const payload = {
      title: document.getElementById("f-title").value,
      description: document.getElementById("f-description").value,
      assignee: document.getElementById("f-assignee").value || null,
      due: document.getElementById("f-due").value || null,
      project: document.getElementById("f-project").value || null,
      priority: document.getElementById("f-priority").value,
    };
    if (!payload.title) return;
    await api.createTask(payload);
    renderTasks();
  });
}

async function renderProjects() {
  const projects = await api.getProjects();
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Проекты</h1>
    ${projects.map(projectCard).join("") || emptyState("Нет проектов")}
  `;
}

function projectCard(project) {
  return `
    <div class="tos-surface rounded-xl p-4 mb-3 shadow-sm">
      <div class="font-medium">${escapeHtml(project.title)}</div>
      <div class="tos-hint text-xs mt-1">${project.tasks.length} задач · ${project.members.join(", ") || "без участников"}</div>
    </div>
  `;
}

async function renderKnowledge() {
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">База знаний</h1>
    <input id="search-input" class="${FORM_FIELD}" placeholder="Поиск..." />
    <div id="search-results"></div>
  `;
  const results = document.getElementById("search-results");
  const input = document.getElementById("search-input");

  const search = async () => {
    const docs = await api.searchKnowledge(input.value);
    results.innerHTML =
      docs
        .map(
          (d) => `<div class="tos-surface rounded-xl p-4 mb-3 shadow-sm"><div class="font-medium">${escapeHtml(d.title)}</div></div>`
        )
        .join("") || emptyState("Ничего не найдено");
  };
  input.addEventListener("input", search);
  search();
}

function renderProfile() {
  const user = tg?.initDataUnsafe?.user;
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Профиль</h1>
    <div class="tos-surface rounded-xl p-4 shadow-sm">
      <div class="font-medium">${user ? escapeHtml(user.first_name) : "Гость"}</div>
      <div class="tos-hint text-xs mt-1">${user ? `@${user.username || ""}` : "Telegram-данные не получены"}</div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

render("home");
