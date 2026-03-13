import ReactMarkdown from "react-markdown";
import { useState } from "react";
import { useTranslation } from "react-i18next";

interface TextAnnotationPanelProps {
  prompt: string;
  responses: string[];
  score: number;
  ranking: number;
  sftText: string;
  aiSuggestion: string;
  onScoreChange: (score: number) => void;
  onRankingChange: (ranking: number) => void;
  onSftChange: (text: string) => void;
  onAcceptAi: () => void;
}

export function TextAnnotationPanel({
  prompt,
  responses,
  score,
  ranking,
  sftText,
  aiSuggestion,
  onScoreChange,
  onRankingChange,
  onSftChange,
  onAcceptAi
}: TextAnnotationPanelProps): JSX.Element {
  const { t } = useTranslation();
  const [preview, setPreview] = useState(false);

  return (
    <div className="workbench-grid">
      <div className="workbench-column sample-nav">
        <h3>Prompt</h3>
        <p className="muted">{prompt}</p>

        <h3>{t("score")}</h3>
        <div className="score-row">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              className={score === value ? "chip active" : "chip"}
              onClick={() => onScoreChange(value)}
            >
              {value}
            </button>
          ))}
        </div>

        <h3>{t("ranking")}</h3>
        <div className="score-row">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              className={ranking === value ? "chip active" : "chip"}
              onClick={() => onRankingChange(value)}
            >
              {value}
            </button>
          ))}
        </div>
      </div>

      <div className="workbench-column annotation-main">
        <div className="response-compare">
          <article>
            <h4>Response A</h4>
            <p>{responses[0] ?? "-"}</p>
          </article>
          <article>
            <h4>Response B</h4>
            <p>{responses[1] ?? "-"}</p>
          </article>
        </div>

        <div className="sft-panel">
          <div className="sft-head">
            <h4>SFT</h4>
            <button className="ghost-btn" onClick={() => setPreview(!preview)}>
              {preview ? "Raw" : "Markdown"}
            </button>
          </div>
          {preview ? (
            <div className="markdown-preview">
              <ReactMarkdown>{sftText || "_No content_"}</ReactMarkdown>
            </div>
          ) : (
            <textarea
              value={sftText}
              onChange={(event) => onSftChange(event.target.value)}
              placeholder="Enter for SFT response, or use AI suggestion and edit"
            />
          )}
        </div>
      </div>

      <div className="workbench-column property-panel">
        <h3>{t("aiAdvice")}</h3>
        <p className="muted">建议评分: 4 / 5，理由: 回答结构完整但缺少具体实验指标。</p>
        <div className="ai-suggestion">{aiSuggestion}</div>
        <button className="primary-btn" onClick={onAcceptAi}>
          {t("aiAgree")} (←)
        </button>
        <p className="hint">{t("aiEdit")} (→)</p>
      </div>
    </div>
  );
}
