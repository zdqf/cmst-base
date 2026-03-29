# 草木沈塘 — API 接口文档

> Base URL: `https://api.caomushentang.com` 或 `http://localhost:8000`

## 一、通用说明

### 认证
需要认证的接口在 Header 中携带: `Authorization: Bearer <token>`

### 统一响应格式
```json
{ "code": 0, "message": "success", "data": { ... } }
```

### 错误码
| code | 含义 |
|------|------|
| 0 | 成功 |
| 400 | 参数错误 / 业务错误 |
| 401 | 未认证 / Token 过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 二、用户端 API

### 2.1 认证模块

#### POST /api/v1/auth/register
注册新用户

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | 是 | 11位手机号 |
| code | string | 是 | 短信验证码 |

**响应**: `{ "access_token": "eyJ..." }`

#### POST /api/v1/auth/login
用户登录

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | 是 | 11位手机号 |
| code | string | 是 | 短信验证码 |

**响应**: `{ "access_token": "eyJ..." }`

---

### 2.2 中药科普

#### GET /api/v1/herbs
中药列表（分页）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页条数，默认 10，最大 20 |
| category | string | 否 | 分类筛选 |
| keyword | string | 否 | 名称搜索 |

**响应**: 分页格式，items 为 `{ id, name, category, status }[]`

#### GET /api/v1/herbs/daily
今日草本推荐

**响应**: 完整中药详情对象

#### GET /api/v1/herbs/{herb_id}
中药详情

**响应**: `{ id, name, category, origin_and_form, flavor_meridian, common_pairings, unsuitable_groups, precautions, status }`

---

### 2.3 AI 问诊

#### POST /api/v1/ai/diagnosis 🔒
提交问诊

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| age | int | 是 | 年龄 1-150 |
| gender | string | 是 | 性别 |
| symptoms | string | 是 | 症状描述，≤500字 |
| allergies | string | 否 | 过敏史 |
| medications | string | 否 | 当前用药 |

**响应**: `{ id, result, created_at }`

#### GET /api/v1/ai/diagnosis/history 🔒
问诊历史（分页）

**响应**: 分页格式，items 为 `{ id, input_data, ai_output, created_at }[]`

#### POST /api/v1/ai/pairing 🔒
搭配建议

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| herb_ids | uuid[] | 是 | 选中的中药 ID 列表 |

**响应**: `{ result: "搭配建议文本..." }`

---

### 2.4 商品浏览

#### GET /api/v1/products
商品列表（分页）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页条数 |
| category | string | 否 | 分类筛选 |

#### GET /api/v1/products/{product_id}
商品详情

**响应**: `{ id, name, category, price, specification, description, image_url, stock, status }`

---

### 2.5 购物车 🔒

#### GET /api/v1/cart
获取购物车列表

#### POST /api/v1/cart
添加商品到购物车

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_id | uuid | 是 | 商品 ID |
| quantity | int | 是 | 数量 |

#### PUT /api/v1/cart/{item_id}
更新购物车商品数量

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| quantity | int | 是 | 新数量 |

#### DELETE /api/v1/cart/{item_id}
删除购物车商品

---

### 2.6 订单 🔒

#### POST /api/v1/orders
创建订单

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| items | array | 是 | `[{ product_id, quantity }]` |

#### GET /api/v1/orders
订单列表（分页，时间倒序）

---

### 2.7 咨询 🔒

#### POST /api/v1/consultations
提交咨询

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| contact | string | 是 | 联系方式 |
| subject | string | 是 | 咨询主题 |
| description | string | 是 | 详细描述 |

**响应**: `{ consultation: {...}, contact: { wechat_id, qr_code_url } }`

---

## 三、管理端 API（需 Admin 权限）

### 3.1 用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/users | 用户列表（支持 phone 搜索） |
| PUT | /api/v1/admin/users/{id}/disable | 禁用用户 |

### 3.2 中药管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/herbs | 中药列表（含下架） |
| POST | /api/v1/admin/herbs | 创建中药 |
| PUT | /api/v1/admin/herbs/{id} | 编辑中药 |
| PUT | /api/v1/admin/herbs/{id}/status | 上下架 |
| POST | /api/v1/admin/herbs/{id}/generate-content | AI 生成内容 |

### 3.3 商品管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/products | 商品列表 |
| POST | /api/v1/admin/products | 创建商品 |
| PUT | /api/v1/admin/products/{id} | 编辑商品 |
| PUT | /api/v1/admin/products/{id}/status | 上下架 |
| PUT | /api/v1/admin/products/{id}/stock | 库存调整 |

### 3.4 订单管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/orders | 订单列表（支持状态/日期筛选） |
| PUT | /api/v1/admin/orders/{id}/status | 更新订单状态 |

### 3.5 咨询管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/consultations | 咨询列表 |
| PUT | /api/v1/admin/consultations/{id}/status | 更新状态 |
| PUT | /api/v1/admin/consultations/{id}/notes | 添加备注 |

### 3.6 问诊记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/diagnosis-logs | 问诊记录列表 |
| GET | /api/v1/admin/diagnosis-logs/{id} | 问诊详情 |

### 3.7 Prompt 模板

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/prompts | 模板列表 |
| GET | /api/v1/admin/prompts/{type}/active | 获取活跃模板 |
| PUT | /api/v1/admin/prompts/{type} | 更新模板（新版本） |
| GET | /api/v1/admin/prompts/{type}/history | 版本历史 |
| POST | /api/v1/admin/prompts/test | 测试 Prompt |

### 3.8 合规配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/compliance | 违规词列表 |
| POST | /api/v1/admin/compliance | 添加违规词 |
| PUT | /api/v1/admin/compliance/{id} | 编辑违规词 |
| DELETE | /api/v1/admin/compliance/{id} | 删除违规词 |

---

## 四、待开发 API

### 4.1 收货地址

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/addresses | 地址列表 |
| POST | /api/v1/addresses | 新增地址 |
| PUT | /api/v1/addresses/{id} | 编辑地址 |
| DELETE | /api/v1/addresses/{id} | 删除地址 |
| PUT | /api/v1/addresses/{id}/default | 设为默认 |

### 4.2 会员积分

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/member/info | 会员信息（等级、积分） |
| GET | /api/v1/member/points-log | 积分流水 |
| POST | /api/v1/member/sign-in | 每日签到 |

### 4.3 优惠券

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/coupons/available | 可领取优惠券 |
| POST | /api/v1/coupons/{id}/claim | 领取优惠券 |
| GET | /api/v1/coupons/mine | 我的优惠券 |

### 4.4 支付

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/payments/create | 创建支付 |
| POST | /api/v1/payments/callback/wechat | 微信支付回调 |
| POST | /api/v1/payments/callback/alipay | 支付宝回调 |

### 4.5 商品评价

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/products/{id}/reviews | 商品评价列表 |
| POST | /api/v1/products/{id}/reviews | 提交评价 |
