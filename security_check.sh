#!/bin/bash
# PropoAI 安全配置检查脚本
# 使用方法: ./security_check.sh

set -e

echo "🔒 PropoAI 安全配置检查"
echo "========================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_count=0
pass_count=0
fail_count=0

print_check() {
    check_count=$((check_count + 1))
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $1"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $1"
        fail_count=$((fail_count + 1))
    fi
}

# 1. 检查 .env 文件存在
echo "📋 基础文件检查："
[ -f ".env" ]
print_check ".env 文件存在"

[ -f ".env.example" ]
print_check ".env.example 文件存在"

echo ""
echo "🔐 安全配置检查:"

# 2. 检查 .env 中密码是否已更改
if grep -q "POSTGRES_PASSWORD=" .env; then
    POSTGRES_PASS=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
    if [ ${#POSTGRES_PASS} -ge 20 ] && [ "$POSTGRES_PASS" != "prepoai_secure_2026" ]; then
        echo -e "${GREEN}✅ PASS${NC}: Postgres密码已更改为强密码"
        pass_count=$((pass_count + 1))
    else
        echo -e "${YELLOW}⚠️  WARNING${NC}: Postgres密码强度不足或未更改"
        fail_count=$((fail_count + 1))
    fi
fi

if grep -q "MONGO_ROOT_PASSWORD=" .env; then
    MONGO_PASS=$(grep "^MONGO_ROOT_PASSWORD=" .env | cut -d'=' -f2)
    if [ ${#MONGO_PASS} -ge 20 ] && [ "$MONGO_PASS" != "mongo_secure_2026" ]; then
        echo -e "${GREEN}✅ PASS${NC}: MongoDB密码已更改为强密码"
        pass_count=$((pass_count + 1))
    else
        echo -e "${YELLOW}⚠️  WARNING${NC}: MongoDB密码强度不足或未更改"
        fail_count=$((fail_count + 1))
    fi
fi

if grep -q "REDIS_PASSWORD=" .env; then
    REDIS_PASS=$(grep "^REDIS_PASSWORD=" .env | cut -d'=' -f2)
    if [ ${#REDIS_PASS} -ge 20 ] && [ "$REDIS_PASS" != "redis_secure_2026" ]; then
        echo -e "${GREEN}✅ PASS${NC}: Redis密码已更改为强密码"
        pass_count=$((pass_count + 1))
    else
        echo -e "${YELLOW}⚠️  WARNING${NC}: Redis密码强度不足或未更改"
        fail_count=$((fail_count + 1))
    fi
fi

echo ""
echo "🐳 Docker配置检查:"

# 3. 检查 docker-compose.yml 配置
grep -q "127.0.0.1:6379" docker-compose.yml
print_check "Redis仅在localhost:6379监听"

grep -q "127.0.0.1:27017" docker-compose.yml
print_check "MongoDB仅在localhost:27017监听"

grep -q "127.0.0.1:5432" docker-compose.yml
print_check "PostgreSQL仅在localhost:5432监听"

grep -q "127.0.0.1:8000" docker-compose.yml
print_check "后端API仅在localhost:8000监听"

grep -q "requirepass" docker-compose.yml
print_check "Redis配置了requirepass"

grep -q "MONGO_INITDB_ROOT_USERNAME" docker-compose.yml
print_check "MongoDB配置了根用户认证"

echo ""
echo "📊 检查统计:"
echo -e "总计: $check_count | ${GREEN}通过: $pass_count${NC} | ${RED}失败: $fail_count${NC}"
echo ""

if [ $fail_count -gt 0 ]; then
    echo -e "${RED}❌ 发现安全问题！${NC}"
    echo ""
    echo "🔧 修复建议:"
    echo "1. 更新 .env 文件中的所有默认密码"
    echo "   示例: openssl rand -base64 32"
    echo ""
    echo "2. 确保 docker-compose.yml 中所有服务都配置了认证"
    echo ""
    echo "3. 运行: docker-compose down && docker-compose up -d"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ 所有安全检查通过！${NC}"
    echo ""
    echo "📝 后续步骤:"
    echo "1. 定期更新Docker镜像和依赖包"
    echo "2. 配置备份策略"
    echo "3. 启用监控和日志系统"
    echo "4. 考虑部署到生产环境前进行安全审计"
    echo ""
    exit 0
fi
