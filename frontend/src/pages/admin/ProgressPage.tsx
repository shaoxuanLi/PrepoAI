export function ProgressPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>标注进度</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>标注员</th>
              <th>已完成</th>
              <th>进行中</th>
              <th>准确率</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>alice</td>
              <td>345</td>
              <td>12</td>
              <td>92.3%</td>
            </tr>
            <tr>
              <td>bob</td>
              <td>296</td>
              <td>8</td>
              <td>89.7%</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}
