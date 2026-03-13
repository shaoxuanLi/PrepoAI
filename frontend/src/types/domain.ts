export type UserRole = "admin" | "employer" | "annotator" | "auditor";

export type ProjectStatus = "blank" | "in_progress" | "completed";

export type TaskStatus = "pending" | "in_progress" | "completed" | "under_review" | "finalized";

export type Modality = "text" | "image" | "audio" | "video";

export interface UserProfile {
  id: number;
  username: string;
  role: UserRole;
  points: number;
}

export interface Project {
  id: number;
  name: string;
  clientName: string;
  status: ProjectStatus;
  progress: number;
}

export interface TaskItem {
  id: number;
  projectId: number;
  title: string;
  status: TaskStatus;
  modality: Modality;
  prompt: string;
  responses: string[];
}

export interface AnnotationSubmission {
  taskId: number;
  userId: number;
  rating?: number;
  ranking?: number;
  sftResponse?: string;
  aiAgreement?: boolean;
}
