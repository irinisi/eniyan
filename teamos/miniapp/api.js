const API_BASE_URL = window.TEAMOS_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const resp = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) throw new Error(`API error ${resp.status}: ${await resp.text()}`);
  return resp.json();
}

const api = {
  getTasks: () => request("/api/tasks"),
  getTask: (id) => request(`/api/tasks/${id}`),
  createTask: (data) => request("/api/tasks", { method: "POST", body: JSON.stringify(data) }),
  updateTask: (id, data) => request(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteTask: (id) => request(`/api/tasks/${id}`, { method: "DELETE" }),

  getProjects: () => request("/api/projects"),
  getProject: (id) => request(`/api/projects/${id}`),

  searchKnowledge: (q) => request(`/api/knowledge?q=${encodeURIComponent(q || "")}`),
  getKnowledgeDoc: (id) => request(`/api/knowledge/${id}`),
};
