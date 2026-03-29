# 🔒 PropoAI 安全加固指南

## 已进行的安全加固 (2026-03-29)

### 1. **Redis 安全加固** ✅
- ✅ 启用密码认证 (`requirepass`)
- ✅ 关闭网络暴露（`--bind 127.0.0.1`）
- ✅ 添加 Redis 数据卷持久化

**漏洞修复:**
```
之前: redis://redis:6379/0  (无密码，端口0.0.0.0:6379开放)
现在: redis://:PASSWORD@redis:6379/0  (有密码，仅127.0.0.1:6379)
```

### 2. **MongoDB 安全加固** ✅
- ✅ 启用认证 (`--auth` flag)
- ✅ 配置根用户 (`MONGO_INITDB_ROOT_USERNAME/PASSWORD`)
- ✅ 限制网络暴露 (`127.0.0.1:27017`)
- ✅ 连接字符串包含 `authSource=admin`

**漏洞修复:**
```
之前: mongodb://mongodb:27017  (无认证，端口0.0.0.0:27017开放)
现在: mongodb://admin:PASSWORD@mongodb:27017/?authSource=admin
```

### 3. **PostgreSQL 安全加固** ✅
- ✅ 密码环境变量化
- ✅ 限制网络暴露 (`127.0.0.1:5432`)
- ✅ SSL支持配置（可选，需证书）

### 4. **MinIO 安全加固** ✅
- ✅ 密码环境变量化
- ✅ 限制网络暴露 (`127.0.0.1:9000/9001`)

### 5. **etcd 安全加固** ✅
- ✅ 限制监听地址

### 6. **后端服务加固** ✅
- ✅ 后端API仅在127.0.0.1:8000监听
- ✅ 所有数据库连接使用加密认证

---

## 🔧 生产部署前必做清单

### 立即行动 (必须)
- [ ] **更改所有默认密码** — 编辑`.env`文件中的所有密码
  ```bash
  POSTGRES_PASSWORD=  # 改为强密码
  MONGO_ROOT_PASSWORD=  # 改为强密码
  REDIS_PASSWORD=  # 改为强密码
  MINIO_ROOT_PASSWORD=  # 改为强密码
  SECRET_KEY=  # 改为长随机字符串
  ```

- [ ] **生成强密码:**
  ```bash
  # 生成32字节的随机密码
  openssl rand -base64 32
  ```

- [ ] **重启所有容器使用新密码:**
  ```bash
  docker-compose down
  docker-compose up -d
  ```

- [ ] **验证连接:**
  ```bash
  # 测试Redis连接
  redis-cli -h 127.0.0.1 -p 6379 -a YOUR_REDIS_PASSWORD ping
  
  # 测试MongoDB连接
  mongosh "mongodb://admin:YOUR_MONGO_PASSWORD@127.0.0.1:27017/?authSource=admin"
  ```

### 生产环境配置 (强烈推荐)
- [ ] **设置防火墙规则** — 仅允许必要的入站端口
  ```bash
  # 仅允许前端和API访问
  ufw allow 80/tcp   # HTTP
  ufw allow 443/tcp  # HTTPS
  ufw allow 22/tcp   # SSH
  ```

- [ ] **使用反向代理** (Nginx/Traefik)
  - 不直接暴露后端端口
  - 启用SSL/TLS加密
  - 添加请求限流

- [ ] **启用SSL/TLS**
  - 为PostgreSQL生成证书
  - 使用HTTPS访问所有服务

- [ ] **隐藏容器暴露**
  ```yaml
  # 示例：仅保留前端和反向代理的端口
  ports:
    - "80:80"    # Nginx/反向代理
    - "443:443"  # HTTPS
  ```

- [ ] **定期备份**
  ```bash
  # 备份PostgreSQL
  docker-compose exec postgres pg_dump -U prepoai propoai > backup.sql
  
  # 备份MongoDB
  docker-compose exec mongodb mongodump --out=/backup
  ```

- [ ] **监控和日志**
  - 启用容器日志收集
  - 监控异常访问尝试
  - 定期检查安全日志

- [ ] **网络隔离**
  - 为容器使用自定义Docker网络
  - 将内部服务与外部隔离

### 可选的高级安全措施
- [ ] 使用密钥管理服务 (HashiCorp Vault, AWS Secrets Manager)
- [ ] 启用数据库加密 (TDE for PostgreSQL, WiredTiger for MongoDB)
- [ ] 配置RBAC权限 (基于角色的访问控制)
- [ ] 安装入侵检测系统 (IDS/IPS)

---

## 📝 环境变量配置示例

创建安全的`.env`文件 (切勿提交到Git):

```env
# 🔐 强密码示例（使用 openssl rand -base64 32 生成）
POSTGRES_PASSWORD=aBc123DeFgHiJkLmNoPqRsTuVwXyZ1234=
MONGO_ROOT_PASSWORD=xYz789AbCdEfGhIjKlMnOpQrStUvWxYz5678=
REDIS_PASSWORD=QwErTyUiOpAsDfGhJkLzXcVbNmMqWeRt1234=
MINIO_ROOT_PASSWORD=PoIuYtReDwAsQzXcVbNmMqWsEdRfTgYhUjI=
SECRET_KEY=LqFgHjKlPwErTyUiOpAsQzXcVbNmAsDfGhJkLzXcVbNm=

# 数据库连接字符串（自动生成，匹配上面的密码）
POSTGRES_DSN=postgresql+asyncpg://prepoai:aBc123DeFgHiJkLmNoPqRsTuVwXyZ1234=@postgres:5432/prepoai
MONGO_DSN=mongodb://admin:xYz789AbCdEfGhIjKlMnOpQrStUvWxYz5678=@mongodb:27017/?authSource=admin
REDIS_DSN=redis://:QwErTyUiOpAsDfGhJkLzXcVbNmMqWeRt1234=@redis:6379/0
```

---

## 🚨 安全事件响应

### 如果发现未授权访问：

1. **立即停止容器**
   ```bash
   docker-compose down
   ```

2. **检查日志**
   ```bash
   docker logs prepoai-redis
   docker logs prepoai-mongodb
   docker logs prepoai-postgres
   ```

3. **更改所有密码**
   ```bash
   # 编辑.env文件，更改所有密码
   # 重新启动容器
   docker-compose up -d
   ```

4. **备份和审查数据**
   - 导出所有数据
   - 检查是否有异常记录
   - 考虑数据完整性

5. **寻求安全审计**
   - 聘请专业安全渗透测试人员
   - 进行完整的系统安全审查

---

## 📚 参考资源

- [Redis 安全指南](https://redis.io/topics/security)
- [MongoDB 安全最佳实践](https://docs.mongodb.com/manual/security/)
- [PostgreSQL 主机认证](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [Docker 安全最佳实践](https://docs.docker.com/engine/security/)
- [OWASP 安全指南](https://owasp.org/www-project-web-security-testing-guide/)

---

**最后更新**: 2026-03-29
**状态**: ✅ 已修复关键漏洞，待生产环境部署前最终配置
