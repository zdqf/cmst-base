# 草木沈塘 — 系统架构设计文档

## 一、系统架构总览

```
┌─────────────────────────────────────────────────────────┐
│                      客户端层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ Web 端   │  │ 小程序端  │  │ Admin 管理端         │   │
│  │ React 19 │  │ Vue 3    │  │ React 19 + Ant Design│   │
│  │ Ant Design│  │ uni-app  │  │                      │   │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │
└───────┼──────────────┼──────────────────┼───────────────┘
        │              │                  │
        ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                    Nginx 反向代理                         │
│              SSL 终止 / 静态资源 / 负载均衡               │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI 应用层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ 认证模块  │  │ 用户端API │  │ 管理端API │              │
│  │ JWT Auth │  │ /api/v1/ │  │ /api/v1/ │               │
│  │          │  │          │  │ admin/   │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │              │              │                    │
│       ▼              ▼              ▼                    │
│  ┌──────────────────────────────────────────────┐       │
│  │              Service 业务逻辑层                │       │
│  │  auth_service / herb_service / ai_service    │       │
│  │  order_service / cart_service / ...           │       │
│  └──────────────────┬───────────────────────────┘       │
│                     │                                    │
│       ┌─────────────┼─────────────┐                     │
│       ▼             ▼             ▼                     │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐               │
│  │ ORM 层  │  │ AI 适配器 │  │ 合规过滤  │               │
│  │SQLAlchemy│  │ OpenAI / │  │Compliance│               │
│  │ (async) │  │ Private  │  │ Filter   │               │
│  └────┬────┘  └────┬─────┘  └──────────┘               │
└───────┼─────────────┼───────────────────────────────────┘
        │             │
        ▼             ▼
┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  OpenAI API  │
│  数据库       │  │  / 私有模型   │
└──────────────┘  └──────────────┘
```

## 二、技术选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| Web 前端 | React + TypeScript | 19.x | 生态成熟，Ant Design 支持好 |
| UI 框架 | Ant Design | 5.x | 企业级组件库，中文友好 |
| 动画 | Framer Motion | 11.x | 声明式动画，React 原生支持 |
| 小程序 | Vue 3 + uni-app | 3.x | 跨端能力，微信生态 |
| 后端框架 | FastAPI | 0.110+ | 异步高性能，自动文档 |
| ORM | SQLAlchemy | 2.x | 异步支持，类型安全 |
| 数据库 | PostgreSQL | 15+ | JSON 支持，全文搜索 |
| 认证 | JWT (python-jose) | - | 无状态，适合分布式 |
| AI | OpenAI API | GPT-4o-mini | 性价比高，中文能力强 |
| 部署 | Docker + Nginx | - | 容器化，易于扩展 |

## 三、数据库设计

### 3.1 现有表结构

| 表名 | 说明 | 核心字段 |
|------|------|---------|
| users | 用户表 | id, phone, nickname, status, is_admin, last_login_at |
| herbs | 中药表 | id, name, category, origin_and_form, flavor_meridian, status |
| products | 商品表 | id, name, category, price, stock, status, image_url |
| orders | 订单表 | id, user_id, order_no, total_amount, status |
| order_items | 订单明细 | id, order_id, product_id, quantity, unit_price |
| cart_items | 购物车 | id, user_id, product_id, quantity |
| consultations | 咨询记录 | id, user_id, name, contact, subject, status |
| ai_diagnosis_logs | 问诊日志 | id, user_id, input_data(JSON), ai_output |
| prompt_templates | Prompt 模板 | id, type, content, version, is_active |
| compliance_words | 合规词 | id, forbidden_word, replacement |
| stock_logs | 库存变动日志 | id, product_id, change_amount, reason |

### 3.2 待新增表

| 表名 | 说明 | 核心字段 |
|------|------|---------|
| addresses | 收货地址 | id, user_id, name, phone, province, city, district, detail, is_default |
| member_levels | 会员等级配置 | id, name, threshold, discount, benefits(JSON) |
| member_points_log | 积分流水 | id, user_id, change, type, description |
| coupons | 优惠券模板 | id, name, type, value, min_amount, valid_days |
| user_coupons | 用户优惠券 | id, user_id, coupon_id, status, used_at |
| product_reviews | 商品评价 | id, user_id, product_id, order_id, rating, content |
| banners | 首页 Banner | id, title, image_url, link, sort_order, status |
| articles | 文章/公告 | id, title, content, category, status |
| payments | 支付记录 | id, order_id, method, amount, status, trade_no |
| logistics | 物流信息 | id, order_id, company, tracking_no, status |

### 3.3 ER 关系图（核心）

```
User 1──N Order 1──N OrderItem N──1 Product
User 1──N CartItem N──1 Product
User 1──N AIDiagnosisLog
User 1──N Consultation
User 1──N Address (待开发)
User 1──N MemberPointsLog (待开发)
User 1──N UserCoupon (待开发)
User 1──N ProductReview (待开发)
Product 1──N StockLog
Product 1──N ProductReview (待开发)
Order 1──1 Payment (待开发)
Order 1──1 Logistics (待开发)
```

## 四、API 架构

### 4.1 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

- code = 0: 成功
- code > 0: 业务错误（400 参数错误, 401 未认证, 403 无权限, 404 不存在）
- code = 500: 服务器错误

### 4.2 分页格式

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

### 4.3 认证方式

- Bearer Token (JWT)
- Header: `Authorization: Bearer <token>`
- Token 有效期: 7 天
- 管理端额外校验 `is_admin` 字段

## 五、AI 服务架构

```
用户输入 → Prompt 模板组合 → AI 适配器工厂
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              OpenAI Adapter   Private Adapter   (可扩展)
                    │               │
                    ▼               ▼
              OpenAI API      私有模型 HTTP
                    │               │
                    └───────┬───────┘
                            ▼
                    合规词过滤 (ComplianceFilter)
                            │
                            ▼
                    追加免责声明
                            │
                            ▼
                    记录问诊日志
                            │
                            ▼
                    返回给用户
```

**Prompt 模板类型**:
- `health_advisor` (健康顾问): AI 问诊使用
- `pairing_assistant` (科普助手): 搭配建议使用
- `content_generator` (科普内容生成): 管理端生成中药内容

## 六、部署架构

```
┌─────────────────────────────────────┐
│           Docker Compose            │
│                                     │
│  ┌─────────┐  ┌─────────────────┐  │
│  │  Nginx  │  │  FastAPI (×2)   │  │
│  │  :80    │──│  :8000          │  │
│  │  :443   │  │  uvicorn        │  │
│  └─────────┘  └─────────────────┘  │
│                                     │
│  ┌─────────────────┐               │
│  │  PostgreSQL      │               │
│  │  :5432           │               │
│  └─────────────────┘               │
│                                     │
│  ┌─────────────────┐               │
│  │  Redis (可选)    │               │
│  │  :6379           │               │
│  └─────────────────┘               │
└─────────────────────────────────────┘
```

## 七、安全设计

| 维度 | 措施 |
|------|------|
| 传输安全 | HTTPS (Let's Encrypt) |
| 认证 | JWT + Token 失效机制 |
| 授权 | 角色校验 (is_admin) |
| 注入防护 | SQLAlchemy ORM 参数化查询 |
| XSS | React 自动转义 + CSP Header |
| CORS | 白名单域名配置 |
| 限流 | Nginx rate limiting |
| 数据 | 敏感字段加密存储 |
| 日志 | 操作日志 + 审计追踪 |
