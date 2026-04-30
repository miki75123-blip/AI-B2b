# Fly.io 迁移环境变量清单

## 需要设置的环境变量

在 Fly.io 部署时，需要设置以下环境变量：

```bash
# === AI 邮件生成 (智谱 GLM - 免费额度) ===
fly secrets set ZHIPU_API_KEY=6768e5603ed244cea0fb65dc48a419c1.Hpq0XAlFQrXIirmV
fly secrets set ZHIPU_MODEL=glm-4

# === 企业搜索 (Google Custom Search API) ===
fly secrets set GOOGLE_SEARCH_API_KEY=AIzaSyDBx7cO-jIBw8R-UJdfeSWoKFHKA4UKbG4
fly secrets set GOOGLE_SEARCH_ENGINE_ID=856b5a4da0e334858

# === 邮件发送 (Resend - 免费 3000封/月) ===
fly secrets set RESEND_API_KEY=re_PxnNBrb2_9b7fpQrYT4LbdgCQ5twxKL7i
fly secrets set RESEND_FROM_EMAIL=your-verified-email@example.com

# === 功能开关 ===
fly secrets set USE_FAKE_SCRAPER=false
fly secrets set USE_FAKE_EMAIL=false

# === JWT 密钥 (重要: 部署前生成新的!) ===
fly secrets set SECRET_KEY=your-super-secret-key-change-this
fly secrets set ALGORITHM=HS256
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 一键设置命令

```bash
# 创建文本文件保存所有命令
cat > fly-deploy.sh << 'EOF'
#!/bin/bash

# AI 邮件生成 (智谱 GLM)
fly secrets set ZHIPU_API_KEY=6768e5603ed244cea0fb65dc48a419c1.Hpq0XAlFQrXIirmV
fly secrets set ZHIPU_MODEL=glm-4

# 企业搜索 (Google Custom Search API)
fly secrets set GOOGLE_SEARCH_API_KEY=AIzaSyDBx7cO-jIBw8R-UJdfeSWoKFHKA4UKbG4
fly secrets set GOOGLE_SEARCH_ENGINE_ID=856b5a4da0e334858

# 邮件发送 (Resend)
fly secrets set RESEND_API_KEY=re_PxnNBrb2_9b7fpQrYT4LbdgCQ5twxKL7i
fly secrets set RESEND_FROM_EMAIL=your-verified-email@example.com

# 功能开关
fly secrets set USE_FAKE_SCRAPER=false
fly secrets set USE_FAKE_EMAIL=false

# JWT 密钥 (部署前修改!)
fly secrets set SECRET_KEY=change-to-a-random-secret-key
fly secrets set ALGORITHM=HS256
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES=30

echo "所有环境变量已设置完成!"
EOF
```

## 注意事项

1. **SECRET_KEY**: 部署前必须修改为新的随机密钥!
2. **RESEND_FROM_EMAIL**: 需要是在 Resend 平台验证过的邮箱
3. **API Keys**: 建议从 Railway 复制当前使用的值，确保一致性

## 验证部署

```bash
# 查看应用状态
fly status

# 查看日志
fly logs

# 测试 API
curl https://ai-leadgen-agent.fly.dev/health
```
