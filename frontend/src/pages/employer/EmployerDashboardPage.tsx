export function EmployerDashboardPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>项目看板</h2>
        <p>总任务数: 12,540</p>
        <p>已完成: 7,138</p>
        <p>平均单样本耗时: 22s</p>
      </section>
      <section className="panel">
        <h3>质量监控</h3>
        <p>Human F1: 0.89</p>
        <p>Golden Dataset 命中率: 96.4%</p>
      </section>
    </div>
  );
}
