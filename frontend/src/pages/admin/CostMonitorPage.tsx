export function CostMonitorPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>成本监控</h2>
        <p>本月人工成本: ¥118,000</p>
        <p>本月Token成本: ¥35,400</p>
      </section>
      <section className="panel">
        <h3>成本趋势（占位）</h3>
        <div className="fake-chart">
          <div style={{ height: "45%" }} />
          <div style={{ height: "70%" }} />
          <div style={{ height: "58%" }} />
          <div style={{ height: "78%" }} />
          <div style={{ height: "66%" }} />
        </div>
      </section>
    </div>
  );
}
