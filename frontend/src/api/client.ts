import { AnnotationSubmission, TaskItem } from "../types/domain";
import { mockTasks } from "../mocks/data";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!resp.ok) {
    throw new Error(`API ${path} failed: ${resp.status}`);
  }

  return (await resp.json()) as T;
}

export async function fetchTaskSquare(): Promise<TaskItem[]> {
  try {
    const tasks = await request<any[]>("/tasks/square");
    return tasks.map((task) => ({
      id: task.id,
      projectId: task.project_id,
      title: `任务 #${task.id}`,
      status: task.status,
      modality: task.modality,
      prompt: "",
      responses: []
    }));
  } catch {
    return mockTasks;
  }
}

export async function claimTask(taskId: number, userId: number): Promise<void> {
  try {
    await request(`/tasks/${taskId}/claim`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId })
    });
  } catch {
    return;
  }
}

export async function submitAnnotation(payload: AnnotationSubmission): Promise<void> {
  try {
    await request(`/tasks/${payload.taskId}/submit`, {
      method: "POST",
      body: JSON.stringify({
        user_id: payload.userId,
        annotation_payload: payload
      })
    });
  } catch {
    return;
  }
}
