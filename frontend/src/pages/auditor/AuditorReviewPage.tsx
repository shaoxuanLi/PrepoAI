export function AuditorReviewPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>仲裁与质检</h2>
        <p>待仲裁任务: 42</p>
        <p>Golden Dataset 抽检通过率: 95.1%</p>
      </section>
      <section className="panel">
        <table className="data-table">
          <thead>
            <tr>
              <th>任务ID</th>
              <th>分歧类型</th>
              <th>标注员A</th>
              <th>标注员B</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>#4901</td>
              <td>RLHF排序冲突</td>
              <td>2</td>
              <td>5</td>
              <td>进入仲裁</td>
            </tr>
            <tr>
              <td>#4902</td>
              <td>Golden不一致</td>
              <td>3</td>
              <td>1</td>
              <td>重审</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}
