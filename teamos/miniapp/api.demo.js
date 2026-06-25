const DEMO_TASKS = [
  { id: "task-001", title: "Подготовить лендинг", description: "Собрать лендинг для проекта \"Новый сайт\" по макету.", status: "in_progress", assignee: "max", project: "website", priority: "high", due: new Date().toISOString().slice(0, 10), tags: [] },
  { id: "task-002", title: "Зафиналить позиции травин", description: "Финальные позиции для иллюстрации.", status: "todo", assignee: "vasya", project: "website", priority: "medium", due: "2026-06-20", tags: [] },
  { id: "task-003", title: "Концепты завернуть нейронкой", description: "Сгенерировать набор концептов.", status: "todo", assignee: "vasya", project: null, priority: "low", due: null, tags: [] },
  { id: "task-004", title: "Согласовать бриф", description: "Бриф с клиентом по новому проекту.", status: "review", assignee: "max", project: "website", priority: "high", due: "2026-06-10", tags: [] },
  { id: "task-005", title: "Завести репозиторий", description: "Создать структуру проекта.", status: "done", assignee: "max", project: "website", priority: "medium", due: "2026-06-05", tags: [] },
];

const DEMO_PROJECTS = [
  { id: "website", title: "Новый сайт", description: "Редизайн лендинга компании.", members: ["max", "vasya"], links: ["Design System"], tasks: ["task-001", "task-002", "task-004", "task-005"] },
  { id: "brand", title: "Брендинг", description: "Обновление визуальной идентичности.", members: ["vasya"], links: [], tasks: [] },
];

const DEMO_KNOWLEDGE = [
  { id: "design-system", title: "Design System", body: "Базовые принципы дизайн-системы проекта [[website]].", links: ["website"] },
  { id: "onboarding", title: "Онбординг новых участников", body: "Как начать работать в команде.", links: [] },
];

let demoIdCounter = 0;

const api = {
  getTasks: () => Promise.resolve(DEMO_TASKS),
  getTask: (id) => Promise.resolve(DEMO_TASKS.find((t) => t.id === id)),
  createTask: (data) => {
    const task = { id: `task-new-${++demoIdCounter}`, status: "todo", tags: [], ...data };
    DEMO_TASKS.push(task);
    return Promise.resolve(task);
  },
  updateTask: (id, data) => {
    const task = DEMO_TASKS.find((t) => t.id === id);
    Object.assign(task, data);
    return Promise.resolve(task);
  },
  deleteTask: (id) => {
    const index = DEMO_TASKS.findIndex((t) => t.id === id);
    if (index !== -1) DEMO_TASKS.splice(index, 1);
    return Promise.resolve({ ok: true });
  },

  getProjects: () => Promise.resolve(DEMO_PROJECTS),
  getProject: (id) => Promise.resolve(DEMO_PROJECTS.find((p) => p.id === id)),
  createProject: (data) => {
    const project = { id: `project-new-${++demoIdCounter}`, tasks: [], ...data };
    DEMO_PROJECTS.push(project);
    return Promise.resolve(project);
  },
  deleteProject: (id) => {
    const index = DEMO_PROJECTS.findIndex((p) => p.id === id);
    if (index !== -1) DEMO_PROJECTS.splice(index, 1);
    return Promise.resolve({ ok: true });
  },

  searchKnowledge: (q) =>
    Promise.resolve(
      !q ? DEMO_KNOWLEDGE : DEMO_KNOWLEDGE.filter((d) => d.title.toLowerCase().includes(q.toLowerCase()))
    ),
  getKnowledgeDoc: (id) => Promise.resolve(DEMO_KNOWLEDGE.find((d) => d.id === id)),
};
