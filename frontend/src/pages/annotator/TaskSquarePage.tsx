import { AudioLines, FileText, Image, Video } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { claimTask, fetchTaskSquare } from "../../api/client";
import { mockUser } from "../../mocks/data";
import { Modality, TaskItem } from "../../types/domain";

const iconByModality: Record<Modality, JSX.Element> = {
  text: <FileText size={18} />,
  image: <Image size={18} />,
  audio: <AudioLines size={18} />,
  video: <Video size={18} />
};

export function TaskSquarePage(): JSX.Element {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTaskSquare().then(setTasks);
  }, []);

  const onClaim = async (taskId: number) => {
    await claimTask(taskId, mockUser.id);
    navigate(`/annotator/workbench/${taskId}`);
  };

  return (
    <div className="card-grid">
      {tasks.map((task) => (
        <article className="task-card" key={task.id}>
          <div className="task-header">
            {iconByModality[task.modality]}
            <h3>{task.title}</h3>
          </div>
          <p>Project #{task.projectId}</p>
          <p>Status: {task.status}</p>
          <button className="primary-btn" onClick={() => onClaim(task.id)}>
            抢单进入任务
          </button>
        </article>
      ))}
    </div>
  );
}
