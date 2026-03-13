export function AdminAccountManagementPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>账号管理</h2>
        <button className="primary-btn">新增用户</button>
        <button className="ghost-btn">批量导入用户</button>
      </section>
      <section className="panel">
        <table className="data-table">
          <thead>
            <tr>
              <th>用户名</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>annotator_01</td>
              <td>Annotator</td>
              <td>Active</td>
              <td>禁用 / 重置密码</td>
            </tr>
            <tr>
              <td>auditor_02</td>
              <td>Auditor</td>
              <td>Active</td>
              <td>升级权限</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}
