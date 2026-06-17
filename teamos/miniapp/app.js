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

tabs.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabs.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
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
    <h1>Главная</h1>
    <h2>Сегодня (${dueToday.length})</h2>
    ${dueToday.map(taskCard).join("") || "<p>Нет задач</p>"}
    <h2>Просрочено (${overdue.length})</h2>
    ${overdue.map(taskCard).join("") || "<p>Нет просроченных задач</p>"}
    <h2>Активные проекты</h2>
    ${projects.map(projectCard).join("") || "<p>Нет проектов</p>"}
  `;
}

async function renderTasks() {
  const tasks = await api.getTasks();
  const columns = ["todo", "in_progress", "review", "done"];
  app.innerHTML = `
    <h1>Задачи</h1>
    <button class="btn" id="new-task-btn">➕ Новая задача</button>
    <div class="kanban">
      ${columns
        .map(
          (status) => `
        <div class="kanban-col">
          <h3>${STATUS_LABELS[status]}</h3>
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
    <div class="card" data-task-id="${task.id}">
      <div class="title">${escapeHtml(task.title)}</div>
      <div class="meta">${task.assignee || "без исполнителя"} · ${task.due || "без срока"}</div>
      <span class="tag">${task.priority}</span>
    </div>
  `;
}

async function renderTaskDetail(taskId) {
  const task = await api.getTask(taskId);
  app.innerHTML = `
    <h1>${escapeHtml(task.title)}</h1>
    <p>${escapeHtml(task.description || "")}</p>
    <div class="meta">Исполнитель: ${task.assignee || "—"}</div>
    <div class="meta">Проект: ${task.project || "—"}</div>
    <div class="meta">Срок: ${task.due || "—"}</div>
    <div class="meta">Статус: ${STATUS_LABELS[task.status]}</div>
    <button class="btn" id="complete-btn">Завершить</button>
    <button class="btn" id="delete-btn">Удалить</button>
    <button class="btn" id="back-btn">← Назад</button>
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

function renderNewTaskForm() {
  app.innerHTML = `
    <h1>Новая задача</h1>
    <input id="f-title" placeholder="Название" />
    <textarea id="f-description" placeholder="Описание"></textarea>
    <input id="f-assignee" placeholder="Исполнитель" />
    <input id="f-due" type="date" />
    <input id="f-project" placeholder="Проект (id)" />
    <select id="f-priority">
      <option value="low">Низкий приоритет</option>
      <option value="medium" selected>Средний приоритет</option>
      <option value="high">Высокий приоритет</option>
    </select>
    <button class="btn" id="save-btn">Сохранить</button>
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
    <h1>Проекты</h1>
    ${projects.map(projectCard).join("") || "<p>Нет проектов</p>"}
  `;
}

function projectCard(project) {
  return `
    <div class="card">
      <div class="title">${escapeHtml(project.title)}</div>
      <div class="meta">${project.tasks.length} задач · ${project.members.join(", ") || "без участников"}</div>
    </div>
  `;
}

async function renderKnowledge() {
  app.innerHTML = `
    <h1>База знаний</h1>
    <input id="search-input" placeholder="Поиск..." />
    <div id="search-results"></div>
  `;
  const results = document.getElementById("search-results");
  const input = document.getElementById("search-input");

  const search = async () => {
    const docs = await api.searchKnowledge(input.value);
    results.innerHTML =
      docs
        .map(
          (d) => `<div class="card"><div class="title">${escapeHtml(d.title)}</div></div>`
        )
        .join("") || "<p>Ничего не найдено</p>";
  };
  input.addEventListener("input", search);
  search();
}

function renderProfile() {
  const user = tg?.initDataUnsafe?.user;
  app.innerHTML = `
    <h1>Профиль</h1>
    <div class="card">
      <div class="title">${user ? escapeHtml(user.first_name) : "Гость"}</div>
      <div class="meta">${user ? `@${user.username || ""}` : "Telegram-данные не получены"}</div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

render("home");
