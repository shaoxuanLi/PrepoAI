import { AudioLines, FileText, Image, Timer, Video } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { submitAnnotation } from "../../api/client";
import { TextAnnotationPanel } from "../../components/workbench/TextAnnotationPanel";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import { mockTasks, mockUser } from "../../mocks/data";
import { Modality } from "../../types/domain";

const modalityTabs: { key: Modality; label: string; icon: JSX.Element }[] = [
  { key: "text", label: "Text", icon: <FileText size={16} /> },
  { key: "image", label: "Image", icon: <Image size={16} /> },
  { key: "audio", label: "Audio", icon: <AudioLines size={16} /> },
  { key: "video", label: "Video", icon: <Video size={16} /> }
];

export function WorkbenchPage(): JSX.Element {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const selectedTask = mockTasks.find((task) => task.id === Number(taskId)) ?? mockTasks[0];
  const [sampleIndex, setSampleIndex] = useState(0);
  const [score, setScore] = useState(3);
  const [ranking, setRanking] = useState(3);
  const [sftText, setSftText] = useState("");
  const [activeModality, setActiveModality] = useState<Modality>(selectedTask.modality);
  const [submittedCount, setSubmittedCount] = useState(0);
  const [statusMessage, setStatusMessage] = useState("快捷键：1~5评分，W/S切换，Space提交，Esc提示")
  const [lockTask, setLockTask] = useState(true);

  const samples = useMemo(() => mockTasks.filter((task) => task.modality === activeModality), [activeModality]);
  const currentSample = samples[sampleIndex] ?? selectedTask;

  const averageSeconds = 22;
  const remaining = Math.max(samples.length - submittedCount, 0);

  useEffect(() => {
    const blockExit = (event: BeforeUnloadEvent) => {
      if (!lockTask) {
        return;
      }
      event.preventDefault();
      event.returnValue = "当前任务正在进行中，暂不允许退出。";
    };

    window.addEventListener("beforeunload", blockExit);
    return () => window.removeEventListener("beforeunload", blockExit);
  }, [lockTask]);

  const onSubmit = async () => {
    await submitAnnotation({
      taskId: currentSample.id,
      userId: mockUser.id,
      rating: score,
      ranking,
      sftResponse: sftText,
      aiAgreement: sftText.length > 0
    });

    setSubmittedCount((value) => value + 1);
    setStatusMessage(`样本 #${currentSample.id} 已提交`);

    if (submittedCount + 1 >= samples.length) {
      setLockTask(false);
      navigate("/annotator/task-square");
      return;
    }

    setSampleIndex((index) => Math.min(index + 1, samples.length - 1));
  };

  useKeyboardShortcuts(
    {
      "1": () => setScore(1),
      "2": () => setScore(2),
      "3": () => setScore(3),
      "4": () => setScore(4),
      "5": () => setScore(5),
      w: () => {
        setSampleIndex((index) => Math.max(0, index - 1));
        setStatusMessage("切换到上一条样本");
      },
      s: () => {
        setSampleIndex((index) => Math.min(samples.length - 1, index + 1));
        setStatusMessage("切换到下一条样本");
      },
      " ": () => {
        onSubmit();
      },
      escape: () => {
        setStatusMessage("任务进行中，禁止退出。请先提交当前样本。");
      },
      enter: () => {
        const textarea = document.querySelector("textarea");
        if (textarea) {
          (textarea as HTMLTextAreaElement).focus();
        }
      },
      arrowleft: () => {
        setSftText("AI建议：建议从定义、流程和应用场景三个层次作答，并给出SFT+RLHF联用示例。");
        setStatusMessage("已接受AI建议内容");
      },
      arrowright: () => {
        setSftText((prev) => `${prev}\n\n[人工补充]: 增加了实验评测与业务落地细节。`.trim());
        setStatusMessage("已基于AI建议进入人工编辑");
      }
    },
    true
  );

  return (
    <div className="panel-stack">
      <section className="panel">
        <div className="modality-tabs">
          {modalityTabs.map((item) => (
            <button
              key={item.key}
              className={activeModality === item.key ? "chip active" : "chip"}
              onClick={() => {
                setActiveModality(item.key);
                setSampleIndex(0);
              }}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>

        {activeModality === "text" ? (
          <TextAnnotationPanel
            prompt={currentSample.prompt}
            responses={currentSample.responses}
            score={score}
            ranking={ranking}
            sftText={sftText}
            aiSuggestion="建议答案：SFT用于让模型学习专家示范，RLHF用于通过偏好优化输出可用性和安全性。"
            onScoreChange={setScore}
            onRankingChange={setRanking}
            onSftChange={setSftText}
            onAcceptAi={() =>
              setSftText("建议答案：SFT用于让模型学习专家示范，RLHF用于通过偏好优化输出可用性和安全性。")
            }
          />
        ) : (
          <div className="placeholder-box">
            <h3>{activeModality.toUpperCase()} 标注界面预留</h3>
            <p>当前版本保留空白框架，后续将接入多模态采样与AI辅助标注能力。</p>
          </div>
        )}
      </section>

      <section className="status-bar">
        <div>
          <strong>已完成:</strong> {submittedCount}
        </div>
        <div>
          <strong>未完成:</strong> {remaining}
        </div>
        <div>
          <strong>平均效率:</strong> {averageSeconds}s/样本
        </div>
        <div>
          <Timer size={14} />
          <strong>预计完成:</strong> {remaining * averageSeconds}s
        </div>
        <div className="status-message">{statusMessage}</div>
      </section>
    </div>
  );
}
