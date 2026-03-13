export function DataDistributionPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>数据分布</h2>
        <p>文本: 72%</p>
        <p>图像: 18%</p>
        <p>音频: 6%</p>
        <p>视频: 4%</p>
      </section>
      <section className="panel">
        <h3>导出</h3>
        <button className="primary-btn">导出 JSONL (Llama)</button>
        <button className="ghost-btn">导出 COCO (Vision)</button>
      </section>
    </div>
  );
}
