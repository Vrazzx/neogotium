import axios from "axios";

const api = axios.create({
  baseURL: "/",
  headers: { "Content-Type": "application/json" },
});
export const BOARD_ID = 1; // в MVP используем одну доску

export type Priority = "low" | "medium" | "high";
export type Status = "backlog" | "todo" | "in_progress" | "done";

export interface Task {
  id: number;
  board_id: number;
  title: string;
  description?: string;
  assignee?: string;
  status: Status;
  priority: Priority;
  tag?: string;
  created_by_ai: boolean;
  created_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  assignee?: string;
  status?: Status;
  priority?: Priority;
  tag?: string;
}

export const tasksApi = {
  getAll: () => api.get<Task[]>(`/api/tasks/board/${BOARD_ID}`),

  create: (data: TaskCreate) =>
    api.post<Task>(`/api/tasks/board/${BOARD_ID}`, data),

  move: (taskId: number, status: Status) =>
    api.patch<Task>(`/api/tasks/${taskId}/move?status=${status}`),

  update: (taskId: number, data: Partial<TaskCreate>) =>
    api.patch<Task>(`/api/tasks/${taskId}`, data),

  delete: (taskId: number) => api.delete(`/api/tasks/${taskId}`),
};