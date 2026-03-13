import { Project, TaskItem, UserProfile } from "../types/domain";

export const mockUser: UserProfile = {
  id: 11,
  username: "annotator_demo",
  role: "annotator",
  points: 235
};

export const mockProjects: Project[] = [
  {
    id: 1,
    name: "Pacman-MultiModal-SFT",
    clientName: "Pacman Lab",
    status: "in_progress",
    progress: 0.57
  },
  {
    id: 2,
    name: "RLHF-Ranking-Beta",
    clientName: "Pacman Lab",
    status: "blank",
    progress: 0.02
  }
];

export const mockTasks: TaskItem[] = [
  {
    id: 101,
    projectId: 1,
    title: "文本评分任务 #101",
    status: "pending",
    modality: "text",
    prompt: "请解释监督微调（SFT）与RLHF在大模型训练中的区别，并给一个实际例子。",
    responses: [
      "SFT通过高质量示例学习输入输出映射，而RLHF通过人类偏好学习奖励模型，进一步优化输出行为。",
      "SFT让模型学会基础能力，RLHF让模型更符合人类价值和偏好，两者常串联使用。"
    ]
  },
  {
    id: 102,
    projectId: 1,
    title: "文本对比任务 #102",
    status: "pending",
    modality: "text",
    prompt: "请给出一个用于评估多模态模型鲁棒性的测试方案。",
    responses: [
      "可以构建跨模态干扰集，并统计模型在噪声图像、错配文本条件下的性能下降。",
      "使用随机样本测试即可。"
    ]
  },
  {
    id: 103,
    projectId: 2,
    title: "图像标注占位任务 #103",
    status: "pending",
    modality: "image",
    prompt: "图像任务占位",
    responses: []
  }
];
