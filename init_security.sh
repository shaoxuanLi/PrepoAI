#!/bin/bash
# 🔒 PreproAI 安全配置初始化脚本
# 此脚本帮助您安全地设置所有密码

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

echo "🔒 PreproAI 安全密码配置"
echo "========================"
echo ""
echo "⚠️  重要提示："
echo "- 此脚本将生成并设置随机密码"
echo "- 请勿将.env文件提交到Git"
echo "- 生产环境请定期更换密码"
echo ""

# 生成随机密码使用openssl
generate_password() {
    openssl rand -base64 32 2>/dev/null || head -c 32 < /dev/urandom | base64
}

echo "🔐 生成安全密码..."
POSTGRES_PASSWORD=$(generate_password)
MONGO_ROOT_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
MINIO_ROOT_PASSWORD=$(generate_password)
SECRET_KEY=$(generate_password)

echo ""
echo "📝 生成的密码（保存在.env中）："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Postgres: $POSTGRES_PASSWORD"
echo "MongoDB:  $MONGO_ROOT_PASSWORD"
echo "Redis:    $REDIS_PASSWORD"
echo "MinIO:    $MINIO_ROOT_PASSWORD"
echo "Secret:   $SECRET_KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 生成新的.env文件
cat > "$ENV_FILE" << EOF
# 🔐 安全密码配置 - 自动生成于 $(date)
# 警告: 请勿提交此文件到版本控制系统

POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=$MONGO_ROOT_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD
SECRET_KEY=$SECRET_KEY

# 自动生成的数据库连接字符串
POSTGRES_DSN=postgresql+asyncpg://preproai:$POSTGRES_PASSWORD@postgres:5432/preproai
MONGO_DSN=mongodb://admin:$MONGO_ROOT_PASSWORD@mongodb:27017/?authSource=admin
MONGO_DB_NAME=preproai
REDIS_DSN=redis://:$REDIS_PASSWORD@redis:6379/0
VITE_API_BASE=http://localhost:8000/api/v1
EOF

echo "✅ .env 文件已生成"
echo ""

# 设置权限
chmod 600 "$ENV_FILE"
echo "✅ 已设置 .env 文件权限为 600 (仅所有者可读)"
echo ""

# 提示后续步骤
echo "📋 后续步骤："
echo "1️⃣  验证 .env 文件内容:"
echo "   cat .env"
echo ""
echo "2️⃣  重启容器使用新密码:"
echo "   docker-compose down"
echo "   docker-compose up -d"
echo ""
echo "3️⃣  验证连接:"
echo "   docker-compose exec redis redis-cli -a '$REDIS_PASSWORD' ping"
echo "   docker-compose exec mongodb mongosh 'mongodb://admin:$MONGO_ROOT_PASSWORD@127.0.0.1:27017/?authSource=admin' --eval 'db.adminCommand({ping:1})'"
echo ""
echo "4️⃣  运行安全检查:"
echo "   ./security_check.sh"
echo ""
echo "✅ 安全配置初始化完成！"
