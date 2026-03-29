# 草木沈塘 — 前端设计文档 (Web 端)

## 一、设计理念

- 中式美学 + 现代简约：品牌色取自草木绿，传递自然健康感
- 信任感优先：专业的内容排版、清晰的免责声明、品质感的视觉
- 转化导向：每个页面都有明确的 CTA（行动号召）
- 移动优先：响应式设计，900px 断点切换布局

## 二、色彩体系

| 用途 | 色值 | 说明 |
|------|------|------|
| 品牌主色 | #2c6b4f | 草木绿，传递自然健康 |
| 品牌深色 | #1a3c2e | 导航栏、Footer 背景 |
| 品牌浅色 | #edf7f0 | 选中态背景、卡片高亮 |
| 价格红 | #c62828 | 商品价格 |
| 警告橙 | #e65100 | 促销标签、限时提示 |
| 信息蓝 | #1565c0 | AI 问诊相关 |
| 高级紫 | #6a1b9a | 咨询、问诊历史 |
| 会员金 | #f9a825 | 会员等级、积分 |
| 背景色 | #f8faf8 | 页面背景，微绿色调 |
| 文字主色 | #1a202c | 正文 |
| 文字辅色 | #718096 | 次要信息 |

## 三、页面结构

### 3.1 导航栏（Desktop）
```
┌──────────────────────────────────────────────────────┐
│ 🌿 传承本草智慧 · 守护自然健康 | 客服热线 | 全国包邮  │ ← 顶部信息条
├──────────────────────────────────────────────────────┤
│ [Logo] 草木沈塘  首页 百科 商城 问诊 咨询 会员 关于 🛒👤│ ← 主导航
└──────────────────────────────────────────────────────┘
```

- 白色背景，品牌色选中态（圆角胶囊 + 底部指示条动画）
- 顶部深绿信息条传递品牌信息
- 购物车 Badge 实时显示数量

### 3.2 导航栏（Mobile）
```
┌──────────────────────────┐
│ [Logo] 草木沈塘    🛒 ☰  │ ← 顶部栏
└──────────────────────────┘
...页面内容...
┌──────────────────────────┐
│ 首页  百科  商城  购物车  我的│ ← 底部 TabBar
└──────────────────────────┘
```

### 3.3 页面清单

| 路由 | 页面 | 布局 |
|------|------|------|
| / | 首页 | Layout |
| /login | 登录 | 全屏 |
| /register | 注册 | 全屏 |
| /herbs | 本草百科列表 | Layout |
| /herbs/:id | 中药详情 | Layout |
| /products | 药材商城列表 | Layout |
| /products/:id | 商品详情 | Layout |
| /diagnosis | AI 问诊表单 | Layout |
| /diagnosis/result | 问诊结果 | Layout |
| /diagnosis/history | 问诊历史 | Layout |
| /pairing | 搭配建议 | Layout |
| /consultation | 在线咨询表单 | Layout |
| /consultation/success | 咨询成功 | Layout |
| /cart | 购物车 | Layout |
| /order/confirm | 订单确认 | Layout |
| /orders | 订单列表 | Layout |
| /profile | 个人中心 | Layout |
| /membership | 会员中心 | Layout |
| /about | 关于我们 | Layout |

## 四、组件体系

### 4.1 基础组件（Ant Design）
- Button, Card, Tag, Input, Select, Form, Table, Pagination
- Typography (Title, Text, Paragraph)
- Layout (Header, Content, Footer)
- Badge, Tooltip, Drawer, Divider, Space, Row, Col
- Carousel, Collapse, Steps, Timeline, Progress
- Alert, Empty, Spin, Result, message

### 4.2 自定义组件
| 组件 | 用途 |
|------|------|
| Layout | 全局布局（导航 + 内容 + Footer） |
| AuthGuard | 路由守卫，未登录跳转 |
| Loading | 加载状态 |
| EmptyState | 空状态 |
| ErrorMessage | 错误提示 |
| Disclaimer | 免责声明 |
| Pagination | 分页（封装 Ant Design） |

### 4.3 自定义 SVG 图标
| 图标 | 用途 |
|------|------|
| LogoIcon | 品牌 Logo |
| HerbLeafIcon | 中药叶子装饰 |
| WaveDecoration | 波浪分隔装饰 |
| HerbBagIcon | 药材袋产品插画 |
| TeaCupIcon | 茶杯产品插画 |
| GiftBoxIcon | 礼盒产品插画 |
| BottleIcon | 瓶装产品插画 |
| MountainHerbIcon | 山间草药场景 |
| VipCrownIcon | 会员皇冠 |

## 五、动画规范

使用 Framer Motion 实现：

| 场景 | 动画 | 参数 |
|------|------|------|
| 页面切换 | 淡入 + 上移 | opacity 0→1, y 10→0, 0.2s |
| 卡片入场 | 淡入 + 上移（交错） | delay i*0.08, 0.45s |
| 导航指示条 | 弹簧滑动 | spring, stiffness 500, damping 35 |
| 卡片 hover | 上浮 + 阴影 | translateY -3px, 0.3s |
| 登录卡片 | 缩放 + 淡入 | scale 0.95→1, 0.5s |

## 六、Mock 数据策略

所有页面在 API 请求失败时自动 fallback 到 mock 数据，确保：
- 开发阶段无需后端即可预览完整 UI
- 演示时页面不会空白
- Mock 数据位于 `src/mock/data.ts`

包含：20 味中药、8 款商品、3 个订单、2 条问诊历史、健康贴士、统计数据等。

## 七、前端待优化项

| 优化项 | 优先级 | 说明 |
|--------|--------|------|
| 路由懒加载 | P1 | React.lazy + Suspense 减少首屏包体积 |
| 图片懒加载 | P1 | 商品图片 IntersectionObserver |
| SEO 优化 | P1 | 中药百科页面考虑 SSR 或预渲染 |
| 骨架屏 | P2 | 列表页加载时显示骨架屏替代 Spin |
| PWA | P2 | Service Worker 离线缓存 |
| 暗色模式 | P3 | Ant Design 主题切换 |
| 无障碍 | P2 | aria 标签、键盘导航 |
