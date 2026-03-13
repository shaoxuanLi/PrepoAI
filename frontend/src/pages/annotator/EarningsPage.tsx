export function EarningsPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>收益总览</h2>
        <p>本月累计收益: ¥4,210</p>
        <p>本周预计收益: ¥1,080</p>
      </section>

      <section className="panel">
        <h2>任务收益明细</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>任务类型</th>
              <th>数量</th>
              <th>收益</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2026-03-10</td>
              <td>文本评分</td>
              <td>180</td>
              <td>¥450</td>
            </tr>
            <tr>
              <td>2026-03-11</td>
              <td>文本对比</td>
              <td>120</td>
              <td>¥360</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}
