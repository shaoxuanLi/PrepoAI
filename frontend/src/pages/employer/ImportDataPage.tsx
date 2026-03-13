import { FormEvent, useState } from "react";

export function EmployerImportDataPage(): JSX.Element {
  const [payload, setPayload] = useState(
    JSON.stringify(
      [
        {
          prompt: "Explain SFT",
          responses: ["A", "B"],
          modality: "text"
        }
      ],
      null,
      2
    )
  );

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    alert("数据导入任务已提交到ETL队列（占位）");
  };

  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>导入数据</h2>
        <p>支持 JSON / JSONL，后端将通过 Celery + Redis 异步处理导入。</p>
        <form onSubmit={onSubmit}>
          <textarea value={payload} onChange={(event) => setPayload(event.target.value)} rows={12} />
          <button className="primary-btn" type="submit">
            提交导入
          </button>
        </form>
      </section>
    </div>
  );
}
