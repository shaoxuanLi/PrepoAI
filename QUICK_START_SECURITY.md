# 🚀 PropoAI 安全加固 — 快速参考指南

**日期**: 2026-03-29  
**状态**: ✅ 所有安全检查通过

---

## 📋 问题背景

学校IT发现你的账号(lsx24)在**2026-03-24 08:53**发起了一次Redis未授权访问攻击：
- **漏洞**: Redis无密码认证，端口暴露到校园网
- **风险**: 攻击者可读写数据、执行远程命令、获取服务器权限
- **来源**: PropoAI项目中的docker-compose.yml配置不安全

---

## ✅ 已修复的问题

| 服务 | 问题 | 解决方案 |
|------|------|--------|
| **Redis** | ❌ 无密码认证，端口0.0.0.0:6379暴露 | ✅ 设置requirepass，仅127.0.0.1:6379 |
| **MongoDB** | ❌ 无认证，端口0.0.0.0:27017暴露 | ✅ 启用--auth，根用户认证，仅127.0.0.1:27017 |
| **PostgreSQL** | ❌ 端口0.0.0.0:5432暴露 | ✅ 仅127.0.0.1:5432 |
| **MinIO** | ❌ 端口0.0.0.0:9000/9001暴露 | ✅ 仅127.0.0.1:9000/9001 |
| **后端API** | ❌ 端口0.0.0.0:8000暴露 | ✅ 仅127.0.0.1:8000 |

---

## 🔑 新增的文件

### 1. **docker-compose.yml** 📝
```diff
- ports: ["6379:6379"]  ❌
+ ports: ["127.0.0.1:6379:6379"]  ✅
+ command: redis-server --requirepass PASSWORD --bind 127.0.0.1
```

### 2. **.env** 🔐
自动生成的强密码文件（已设置600权限，仅所有者可读）
```env
POSTGRES_PASSWORD=Y1DJPq667B980XIoURR7sUrNDl4uu0YPNuVUMCXX/DE=
MONGO_ROOT_PASSWORD=WpfN7QhOR+t3zW+fZVDYJW4ZIT3Y5I+a/FtvVML3Ev4=
REDIS_PASSWORD=weKdlluPwle4RJOn/JHZYSatRav6Xl1bPGoW3tMyW2I=
...
```

### 3. **SECURITY.md** 📚
完整的安全加固指南和生产部署检查清单

### 4. **security_check.sh** ✔️
自动验证所有安全设置的脚本

### 5. **init_security.sh** 🔄
生成新密码和初始化.env的脚本

---

## 🚀 立即要做的事

### 步骤1：重启容器（应用新的安全配置）

```bash
cd "/Users/jadeons/Desktop/code/software engineering/PropoAI"

# 停止所有容器
docker-compose down

# 使用新的安全配置启动
docker-compose up -d
```

### 步骤2：验证连接

```bash
# 测试Redis（需要密码）
docker-compose exec redis redis-cli -a "weKdlluPwle4RJOn/JHZYSatRav6Xl1bPGoW3tMyW2I=" ping
# 预期输出: PONG

# 测试MongoDB（需要认证）
docker-compose exec mongodb mongosh \
  "mongodb://admin:WpfN7QhOR+t3zW+fZVDYJW4ZIT3Y5I+a/FtvVML3Ev4=@mongodb:27017/?authSource=admin" \
  --eval 'db.adminCommand({ping:1})'
# 预期输出: { ok: 1 }
```

### 步骤3：检查日志

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看Celery worker日志
docker-compose logs -f celery-worker
```

### 步骤4：验证前端连接

```bash
# 确保前端可以正常连接后端API
docker-compose logs -f frontend
```

---

## 📊 安全配置总结

### 网络隔离 🔒
```
之前:
  Redis:     0.0.0.0:6379 → 任何人都能访问
  MongoDB:   0.0.0.0:27017 → 任何人都能访问
  后端API:   0.0.0.0:8000 → 任何人都能访问

现在:
  Redis:     127.0.0.1:6379 → 仅本机访问
  MongoDB:   127.0.0.1:27017 → 仅本机访问
  后端API:   127.0.0.1:8000 → 仅本机访问
```

### 认证机制 🔑
```
之前:
  Redis:    无密码 ❌
  MongoDB:  无认证 ❌

现在:
  Redis:    requirepass + 强密码 ✅
  MongoDB:  admin用户 + 强密码 + authSource ✅
  PostgreSQL: prepoai用户 + 强密码 ✅
```

---

## ⚠️ 重要提醒

1. **`.env` 文件永远不要提交Git**
   ```bash
   $ cat .gitignore
   **/.env  ✅ 已配置
   ```

2. **定期更改密码**（建议每月一次）
   ```bash
   ./init_security.sh  # 重新生成密码
   docker-compose down && docker-compose up -d
   ```

3. **监控异常访问**
   ```bash
   docker logs prepoai-redis | grep "AUTH"
   docker logs prepoai-mongodb | grep "authentication"
   ```

4. **备份重要数据**
   ```bash
   # PostgreSQL备份
   docker-compose exec postgres pg_dump -U prepoai prepoai > backup.sql
   
   # MongoDB备份
   docker-compose exec mongodb mongodump --out=/backup
   ```

---

## 🛡️ 针对原始攻击的防护

**原始攻击**：`redis://redis:6379/0` 无密码访问
```
之前: 攻击者可以:
  ❌ 读取所有Redis数据
  ❌ 写入恶意数据
  ❌ 执行FLUSHALL清空数据库
  ❌ 通过MODULE LOAD执行代码

现在: 所有操作都需要:
  ✅ 正确的密码: weKdlluPwle4RJOn/JHZYSatRav6Xl1bPGoW3tMyW2I=
  ✅ 仅127.0.0.1可访问
  ✅ 防火墙阻止外部连接
```

---

## 📞 故障排除

### 容器无法启动？

```bash
# 查看详细错误
docker-compose logs backend

# 常见问题：密码包含特殊字符需要转义
# 解决：确保docker-compose.yml中的密码使用${REDIS_PASSWORD}变量
```

### 应用无法连接数据库？

```bash
# 检查连接字符串
grep REDIS_DSN .env
grep MONGO_DSN .env

# 验证密码是否正确
docker-compose exec redis redis-cli -a "YOUR_PASSWORD" ping
```

### 如何临时禁用安全设置（仅用于调试）？

```bash
# ⚠️ 仅用于开发调试，生产环境禁止
# 临时移除requirepass (不推荐)
docker-compose exec redis redis-cli CONFIG SET requirepass ""
```

---

## 📚 参考资源

- [Redis安全文档](https://redis.io/topics/security)
- [MongoDB认证官方指南](https://docs.mongodb.com/manual/core/authentication/)
- [Docker安全最佳实践](https://docs.docker.com/engine/security/)
- [OWASP安全检查清单](https://owasp.org/www-project-web-security-testing-guide/)

---

## ✅ 最终检查清单

- [x] Redis配置了密码和仅localhost绑定
- [x] MongoDB启用了认证和仅localhost绑定  
- [x] PostgreSQL密码已更新
- [x] 所有内部服务仅在127.0.0.1监听
- [x] 生成了强随机密码
- [x] .env文件权限设置为600
- [x] .gitignore正确配置防止提交密码
- [x] 安全检查脚本全部通过

**下一步**: 重启容器并在生产环境部署前进行安全审计

---

**问题联系**: 如有任何安全问题，请立即停止容器并进行备份
