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

function icon(name, cls = "size-4") {
  return `<i data-lucide="${name}" class="${cls} inline-block"></i>`;
}

async function render(tab) {
  app.innerHTML = "<p>Загрузка...</p>";
  try {
    if (tab === "home") await renderHome();
    else if (tab === "tasks") await renderTasks();
    else if (tab === "projects") await renderProjects();
    else if (tab === "knowledge") await renderKnowledge();
    else if (tab === "profile") await renderProfile();
  } catch (err) {
    app.innerHTML = `<p>Ошибка: ${err.message}</p>`;
  }
  window.lucide?.createIcons();
}

function initials(name) {
  if (!name) return "?";
  const clean = name.trim().replace(/^@/, "");
  return clean
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join("");
}

function avatar(name, size = "size-7") {
  return `<div class="${size} rounded-full tos-accent flex items-center justify-center text-[11px] font-semibold shrink-0">${initials(
    name
  )}</div>`;
}

function statCard(iconName, label, count, id) {
  return `
    <button data-stat="${id}" class="stat-card tos-surface rounded-xl p-3 text-left shadow-sm hover:shadow-md transition flex flex-col gap-1">
      <div class="flex items-center justify-between h-5">
        ${icon(iconName, "size-5")}
        <span class="text-xl font-semibold">${count}</span>
      </div>
      <span class="text-xs tos-hint">${label}</span>
    </button>
  `;
}

function newTaskCard() {
  return `
    <button id="new-task-btn" class="stat-card tos-accent rounded-xl p-3 text-left shadow-sm hover:opacity-90 transition flex flex-col gap-1">
      <div class="flex items-center justify-between h-5">
        ${icon("plus", "size-5")}
      </div>
      <span class="text-xs font-medium">Новая задача</span>
    </button>
  `;
}

async function renderHome() {
  const tasks = await api.getTasks();
  const today = new Date().toISOString().slice(0, 10);
  const open = tasks.filter((t) => t.status !== "done");
  const dueToday = open.filter((t) => t.due === today);
  const scheduled = open.filter((t) => t.due && t.due > today);
  const flagged = open.filter((t) => t.priority === "high");
  const completed = tasks.filter((t) => t.status === "done");

  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Главная</h1>
    <div class="grid grid-cols-2 gap-3 mb-5">
      ${newTaskCard()}
      ${statCard("calendar-days", "Сегодня", dueToday.length, "today")}
      ${statCard("calendar-clock", "Запланировано", scheduled.length, "scheduled")}
      ${statCard("clipboard-list", "Все", open.length, "all")}
      ${statCard("flag", "Срочные", flagged.length, "flagged")}
      ${statCard("check-circle", "Выполнено", completed.length, "completed")}
    </div>
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2">К выполнению</h2>
    ${taskGroup(open.filter((t) => t.status === "todo"))}
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2 mt-5">В работе</h2>
    ${taskGroup(open.filter((t) => t.status === "in_progress"))}
  `;

  document.getElementById("new-task-btn").addEventListener("click", renderNewTaskForm);

  const statFilters = {
    today: (t) => t.due === today && t.status !== "done",
    scheduled: (t) => t.due && t.due > today && t.status !== "done",
    all: (t) => t.status !== "done",
    flagged: (t) => t.priority === "high",
    completed: (t) => t.status === "done",
  };
  app.querySelectorAll("[data-stat]").forEach((btn) => {
    btn.addEventListener("click", () => renderTasks(statFilters[btn.dataset.stat]));
  });
  app.querySelectorAll(".card[data-task-id]").forEach((card) => {
    card.addEventListener("click", () => renderTaskDetail(card.dataset.taskId));
  });
  window.lucide?.createIcons();
}

function byDueDate(a, b) {
  if (!a.due && !b.due) return 0;
  if (!a.due) return 1;
  if (!b.due) return -1;
  return a.due < b.due ? -1 : a.due > b.due ? 1 : 0;
}

function taskGroup(tasks) {
  return [...tasks].sort(byDueDate).map(taskRow).join("") || emptyState("Нет задач");
}

function taskRow(task) {
  return `
    <div class="card tos-surface rounded-xl p-3 mb-2 shadow-sm hover:shadow-md transition cursor-pointer flex items-center gap-3" data-task-id="${task.id}">
      ${avatar(task.assignee)}
      <div class="flex-1 min-w-0">
        <div class="font-medium text-sm truncate">${escapeHtml(task.title)}</div>
        <div class="tos-hint text-xs mt-0.5">${task.due || "без срока"}</div>
      </div>
      ${priorityBadge(task.priority)}
    </div>
  `;
}

function emptyState(text) {
  return `<p class="tos-hint text-sm py-2">${text}</p>`;
}

const PRIORITY_STYLE = {
  high: "bg-red-100 text-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-emerald-100 text-emerald-700",
};

const PRIORITY_LABEL = { high: "Высокий", medium: "Средний", low: "Низкий" };

function priorityBadge(priority) {
  const cls = PRIORITY_STYLE[priority] || "bg-gray-100 text-gray-700";
  return `<span class="inline-block text-[11px] font-medium px-2.5 py-0.5 rounded-full shrink-0 ${cls}">${
    PRIORITY_LABEL[priority] || priority
  }</span>`;
}

const COLUMN_PROGRESS = { todo: 0, in_progress: 50, review: 80, done: 100 };

async function renderTasks(filter) {
  const allTasks = await api.getTasks();
  const tasks = filter ? allTasks.filter(filter) : allTasks;
  const columns = ["todo", "in_progress", "review", "done"];
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Задачи</h1>
    <button class="tos-accent w-full rounded-lg py-2.5 px-4 text-sm font-medium mb-4 hover:opacity-90 transition flex items-center justify-center gap-2" id="new-task-btn">${icon("plus")} Новая задача</button>
    <div class="flex gap-3 overflow-x-auto pb-2">
      ${columns
        .map((status) => {
          const colTasks = tasks.filter((t) => t.status === status);
          return `
        <div class="min-w-[250px] flex-1">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-semibold tos-hint uppercase tracking-wide">${STATUS_LABELS[status]} <span class="tos-hint">(${colTasks.length})</span></h3>
            <button data-new-status="${status}" class="text-xs tos-accent rounded-full px-2 py-0.5 flex items-center gap-1">${icon("plus", "size-3")} Новая</button>
          </div>
          ${colTasks.map((t) => taskCard(t)).join("") || emptyState("Нет задач")}
        </div>`;
        })
        .join("")}
    </div>
  `;
  document.getElementById("new-task-btn").addEventListener("click", () => renderNewTaskForm());
  app.querySelectorAll("[data-new-status]").forEach((btn) => {
    btn.addEventListener("click", () => renderNewTaskForm(btn.dataset.newStatus));
  });
  app.querySelectorAll(".card[data-task-id]").forEach((card) => {
    card.addEventListener("click", () => renderTaskDetail(card.dataset.taskId));
  });
  window.lucide?.createIcons();
}

function taskCard(task) {
  const progress = COLUMN_PROGRESS[task.status] ?? 0;
  return `
    <div class="card tos-surface rounded-xl p-4 mb-3 shadow-sm hover:shadow-md transition cursor-pointer" data-task-id="${task.id}">
      <div class="flex items-start justify-between gap-2 mb-2">
        <div class="font-medium text-sm">${escapeHtml(task.title)}</div>
        ${priorityBadge(task.priority)}
      </div>
      ${task.project ? `<div class="tos-hint text-xs mb-2 flex items-center gap-1">${icon("folder", "size-3.5")} ${escapeHtml(task.project)}</div>` : ""}
      <div class="w-full h-1.5 rounded-full bg-black/10 overflow-hidden mb-3">
        <div class="h-full tos-accent" style="width:${progress}%"></div>
      </div>
      <div class="flex items-center justify-between">
        ${avatar(task.assignee, "size-6")}
        <div class="tos-hint text-xs">${task.due || "без срока"}</div>
      </div>
    </div>
  `;
}

async function renderTaskDetail(taskId) {
  const task = await api.getTask(taskId);
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-2">${escapeHtml(task.title)}</h1>
    <p class="text-sm mb-4">${escapeHtml(task.description || "")}</p>
    <div class="tos-surface rounded-xl p-4 mb-4 space-y-1 text-sm">
      <div><span class="tos-hint">Исполнитель:</span> ${assigneeLink(task.assignee)}</div>
      <div><span class="tos-hint">Проект:</span> ${task.project || "—"}</div>
      <div><span class="tos-hint">Срок:</span> ${task.due || "—"}</div>
    </div>
    <label class="text-sm tos-hint block mb-1">Статус</label>
    <select id="status-select" class="${FORM_FIELD}">
      ${Object.entries(STATUS_LABELS)
        .map(
          ([value, label]) =>
            `<option value="${value}" ${value === task.status ? "selected" : ""}>${label}</option>`
        )
        .join("")}
    </select>
    <button class="w-full rounded-lg py-2.5 px-4 text-sm font-medium mb-2 border tos-border text-red-600 hover:bg-red-50 transition" id="delete-btn">Удалить</button>
    <button class="w-full rounded-lg py-2.5 px-4 text-sm font-medium tos-hint" id="back-btn">← Назад</button>
  `;
  document.getElementById("status-select").addEventListener("change", async (e) => {
    await api.updateTask(taskId, { status: e.target.value });
    renderTasks();
  });
  document.getElementById("delete-btn").addEventListener("click", async () => {
    await api.deleteTask(taskId);
    renderTasks();
  });
  document.getElementById("back-btn").addEventListener("click", () => renderTasks());
  window.lucide?.createIcons();
}

function assigneeLink(assignee) {
  if (!assignee) return "—";
  const username = assignee.trim().replace(/^@/, "");
  if (!/^[A-Za-z0-9_]+$/.test(username)) return escapeHtml(assignee);
  return `<a href="https://t.me/${username}" target="_blank" class="text-[var(--button)] underline">${escapeHtml(assignee)}</a>`;
}

const FORM_FIELD = "tos-input w-full rounded-lg border px-3 py-2 mb-3 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--button)]";

async function renderNewTaskForm(initialStatus) {
  const [projects, tasks] = await Promise.all([api.getProjects(), api.getTasks()]);
  const assignees = [...new Set(tasks.map((t) => t.assignee).filter(Boolean))];
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Новая задача</h1>
    <input id="f-title" class="${FORM_FIELD}" placeholder="Название" />
    <textarea id="f-description" class="${FORM_FIELD}" placeholder="Описание"></textarea>
    <input id="f-assignee" class="${FORM_FIELD}" placeholder="Исполнитель" list="f-assignee-list" />
    <datalist id="f-assignee-list">
      ${assignees.map((a) => `<option value="${escapeHtml(a)}"></option>`).join("")}
    </datalist>
    <input id="f-due" class="${FORM_FIELD}" type="date" />
    <select id="f-project" class="${FORM_FIELD}">
      <option value="">Без проекта</option>
      ${projects.map((p) => `<option value="${p.id}">${escapeHtml(p.title)}</option>`).join("")}
    </select>
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
      status: initialStatus || "todo",
    };
    if (!payload.title) return;
    try {
      await api.createTask(payload);
      renderTasks();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  });
  window.lucide?.createIcons();
}

function newProjectCard() {
  return `
    <button id="new-project-btn" class="tos-accent w-full rounded-lg py-2.5 px-4 text-sm font-medium mb-4 hover:opacity-90 transition flex items-center justify-center gap-2">${icon("plus")} Новый проект</button>
  `;
}

async function renderProjects() {
  const projects = await api.getProjects();
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Проекты</h1>
    ${newProjectCard()}
    ${projects.map(projectCard).join("") || emptyState("Нет проектов")}
  `;
  document.getElementById("new-project-btn").addEventListener("click", renderNewProjectForm);
  app.querySelectorAll(".card[data-project-id]").forEach((card) => {
    card.addEventListener("click", () => renderProjectDetail(card.dataset.projectId));
  });
  app.querySelectorAll("[data-delete-project]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        await api.deleteProject(btn.dataset.deleteProject);
        renderProjects();
      } catch (err) {
        alert(`Ошибка: ${err.message}`);
      }
    });
  });
  window.lucide?.createIcons();
}

function projectCard(project) {
  return `
    <div class="card tos-surface rounded-xl p-4 mb-3 shadow-sm hover:shadow-md transition cursor-pointer flex items-center justify-between gap-2" data-project-id="${project.id}">
      <div class="min-w-0">
        <div class="font-medium truncate">${escapeHtml(project.title)}</div>
        <div class="tos-hint text-xs mt-1">${project.tasks.length} задач · ${project.members.join(", ") || "без участников"}</div>
      </div>
      <button data-delete-project="${project.id}" class="shrink-0 text-red-600 hover:bg-red-50 rounded-lg p-2 transition">${icon("trash-2", "size-4")}</button>
    </div>
  `;
}

function renderNewProjectForm() {
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Новый проект</h1>
    <input id="f-title" class="${FORM_FIELD}" placeholder="Название" />
    <textarea id="f-description" class="${FORM_FIELD}" placeholder="Описание"></textarea>
    <input id="f-members" class="${FORM_FIELD}" placeholder="Участники (через запятую)" />
    <button class="tos-accent w-full rounded-lg py-2.5 px-4 text-sm font-medium hover:opacity-90 transition" id="save-btn">Сохранить</button>
  `;
  document.getElementById("save-btn").addEventListener("click", async () => {
    const title = document.getElementById("f-title").value;
    if (!title) return;
    const members = document
      .getElementById("f-members")
      .value.split(",")
      .map((m) => m.trim())
      .filter(Boolean);
    try {
      await api.createProject({
        title,
        description: document.getElementById("f-description").value,
        members,
        links: [],
      });
      renderProjects();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  });
  window.lucide?.createIcons();
}

async function renderProjectDetail(projectId) {
  const [project, allTasks] = await Promise.all([api.getProject(projectId), api.getTasks()]);
  const tasks = allTasks.filter((t) => t.project === projectId);
  app.innerHTML = `
    <button id="back-btn" class="tos-hint text-sm mb-4 flex items-center gap-1">${icon("arrow-left", "size-4")} Назад</button>
    <h1 class="text-2xl font-semibold mb-1">${escapeHtml(project.title)}</h1>
    <p class="text-sm tos-hint mb-4">${escapeHtml(project.description || "")}</p>
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2">К выполнению</h2>
    ${taskGroup(tasks.filter((t) => t.status === "todo"))}
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2 mt-5">В работе</h2>
    ${taskGroup(tasks.filter((t) => t.status === "in_progress"))}
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2 mt-5">Ревью</h2>
    ${taskGroup(tasks.filter((t) => t.status === "review"))}
    <h2 class="text-sm font-medium tos-hint uppercase tracking-wide mb-2 mt-5">Выполнено</h2>
    ${taskGroup(tasks.filter((t) => t.status === "done"))}
    <button class="w-full rounded-lg py-2.5 px-4 text-sm font-medium mt-4 border tos-border text-red-600 hover:bg-red-50 transition" id="delete-project-btn">Удалить проект</button>
  `;
  document.getElementById("back-btn").addEventListener("click", renderProjects);
  document.getElementById("delete-project-btn").addEventListener("click", async () => {
    await api.deleteProject(projectId);
    renderProjects();
  });
  app.querySelectorAll(".card[data-task-id]").forEach((card) => {
    card.addEventListener("click", () => renderTaskDetail(card.dataset.taskId));
  });
  window.lucide?.createIcons();
}

async function renderKnowledge() {
  app.innerHTML = `
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-2xl font-semibold">База знаний</h1>
      <button id="new-doc-btn" class="tos-btn flex items-center gap-1 text-sm px-3 py-1.5">
        ${icon("plus", "size-4")} Новый
      </button>
    </div>
    <input id="search-input" class="${FORM_FIELD} mb-3" placeholder="Поиск..." />
    <div id="search-results"></div>
  `;
  const results = document.getElementById("search-results");
  const input = document.getElementById("search-input");

  const search = async () => {
    const docs = await api.searchKnowledge(input.value);
    results.innerHTML =
      docs.map((d) => `
        <div class="tos-surface rounded-xl p-4 mb-3 shadow-sm flex items-center justify-between cursor-pointer doc-card" data-id="${escapeHtml(d.id)}">
          <div class="font-medium">${escapeHtml(d.title)}</div>
          <button class="doc-delete text-red-500 ml-3 shrink-0" data-id="${escapeHtml(d.id)}">${icon("trash-2", "size-4")}</button>
        </div>`).join("") || emptyState("Ничего не найдено");

    results.querySelectorAll(".doc-card").forEach((card) => {
      card.addEventListener("click", (e) => {
        if (e.target.closest(".doc-delete")) return;
        renderKnowledgeDetail(card.dataset.id);
      });
    });
    results.querySelectorAll(".doc-delete").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        if (!confirm("Удалить документ?")) return;
        try {
          await api.deleteKnowledgeDoc(btn.dataset.id);
          await search();
        } catch (err) {
          alert(err.message);
        }
      });
    });
    window.lucide?.createIcons();
  };

  input.addEventListener("input", search);
  document.getElementById("new-doc-btn").addEventListener("click", () => renderNewDocForm());
  await search();
  window.lucide?.createIcons();
}

async function renderKnowledgeDetail(docId) {
  const doc = await api.getKnowledgeDoc(docId);
  app.innerHTML = `
    <div class="flex items-center gap-2 mb-4">
      <button id="back-btn" class="tos-hint text-sm">${icon("arrow-left", "size-4")} Назад</button>
    </div>
    <h1 class="text-2xl font-semibold mb-2">${escapeHtml(doc.title)}</h1>
    <div class="tos-surface rounded-xl p-4 shadow-sm prose prose-sm max-w-none text-sm" id="doc-body"></div>
  `;
  document.getElementById("back-btn").addEventListener("click", () => renderKnowledge());
  const bodyEl = document.getElementById("doc-body");
  if (doc.body) {
    bodyEl.innerHTML = window.marked ? marked.parse(doc.body) : `<pre class="whitespace-pre-wrap">${escapeHtml(doc.body)}</pre>`;
  } else {
    bodyEl.innerHTML = '<span class="tos-hint">Документ пустой</span>';
  }
  window.lucide?.createIcons();
}

async function renderNewDocForm() {
  app.innerHTML = `
    <div class="flex items-center gap-2 mb-4">
      <button id="back-btn" class="tos-hint text-sm">${icon("arrow-left", "size-4")} Назад</button>
    </div>
    <h1 class="text-2xl font-semibold mb-4">Новый документ</h1>
    <input id="doc-title" class="${FORM_FIELD} mb-3" placeholder="Название" />
    <textarea id="doc-body" class="${FORM_FIELD} mb-4 h-48 resize-none" placeholder="Текст документа..."></textarea>
    <button id="save-btn" class="tos-btn w-full py-2">Сохранить</button>
  `;
  document.getElementById("back-btn").addEventListener("click", () => renderKnowledge());
  document.getElementById("save-btn").addEventListener("click", async () => {
    const title = document.getElementById("doc-title").value.trim();
    if (!title) { alert("Введи название"); return; }
    try {
      await api.createKnowledgeDoc({ title, body: document.getElementById("doc-body").value });
      await renderKnowledge();
    } catch (err) {
      alert(err.message);
    }
  });
  window.lucide?.createIcons();
}

function renderProfile() {
  const user = tg?.initDataUnsafe?.user;
  const photoHtml = user?.photo_url
    ? `<img src="${user.photo_url}" class="size-14 rounded-full object-cover shrink-0" />`
    : avatar(user?.first_name || user?.username, "size-14");
  app.innerHTML = `
    <h1 class="text-2xl font-semibold mb-4">Профиль</h1>
    <div class="tos-surface rounded-xl p-4 shadow-sm flex items-center gap-4">
      ${photoHtml}
      <div>
        <div class="font-medium">${user ? escapeHtml(user.first_name) : "Гость"}</div>
        <div class="tos-hint text-xs mt-1">${user ? `@${user.username || ""}` : "Telegram-данные не получены"}</div>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

window.lucide?.createIcons();
render("home");
