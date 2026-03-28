import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { Layout as AntLayout, Badge, Drawer, Button, Typography, Tooltip, Divider, Space } from 'antd'
import {
  HomeOutlined,
  ReadOutlined,
  ShoppingCartOutlined,
  ShopOutlined,
  UserOutlined,
  MenuOutlined,
  MedicineBoxOutlined,
  MessageOutlined,
  ExperimentOutlined,
  HistoryOutlined,
  GiftOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  WechatOutlined,
  RightOutlined,
  CrownOutlined,
  BookOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import { motion, AnimatePresence } from 'framer-motion'
import { useCart } from '../contexts/CartContext'
import { LogoIcon } from '../assets/icons'

const { Header, Content, Footer } = AntLayout
const { Text, Title } = Typography

interface NavItem {
  key: string
  label: string
  icon: React.ReactNode
}

const mainNavItems: NavItem[] = [
  { key: '/', label: '首页', icon: <HomeOutlined /> },
  { key: '/herbs', label: '本草百科', icon: <ReadOutlined /> },
  { key: '/products', label: '药材商城', icon: <ShopOutlined /> },
  { key: '/diagnosis', label: 'AI 问诊', icon: <MedicineBoxOutlined /> },
  { key: '/consultation', label: '在线咨询', icon: <MessageOutlined /> },
  { key: '/membership', label: '会员', icon: <CrownOutlined /> },
  { key: '/about', label: '关于', icon: <InfoCircleOutlined /> },
]

const mobileNavItems: NavItem[] = [
  { key: '/', label: '首页', icon: <HomeOutlined /> },
  { key: '/herbs', label: '百科', icon: <ReadOutlined /> },
  { key: '/products', label: '商城', icon: <ShopOutlined /> },
  { key: '/cart', label: '购物车', icon: <ShoppingCartOutlined /> },
  { key: '/profile', label: '我的', icon: <UserOutlined /> },
]

const drawerMenuGroups = [
  {
    title: '核心服务',
    items: [
      { key: '/diagnosis', label: 'AI 智能问诊', icon: <MedicineBoxOutlined style={{ color: '#1565c0' }} /> },
      { key: '/pairing', label: '中药搭配建议', icon: <ExperimentOutlined style={{ color: '#e65100' }} /> },
      { key: '/consultation', label: '专家在线咨询', icon: <MessageOutlined style={{ color: '#6a1b9a' }} /> },
    ],
  },
  {
    title: '我的',
    items: [
      { key: '/orders', label: '我的订单', icon: <ShoppingCartOutlined style={{ color: '#2c6b4f' }} /> },
      { key: '/diagnosis/history', label: '问诊历史', icon: <HistoryOutlined style={{ color: '#00695c' }} /> },
      { key: '/membership', label: '会员中心', icon: <CrownOutlined style={{ color: '#f9a825' }} /> },
      { key: '/profile', label: '个人中心', icon: <UserOutlined style={{ color: '#546e7a' }} /> },
    ],
  },
  {
    title: '更多',
    items: [
      { key: '/about', label: '关于草木沈塘', icon: <InfoCircleOutlined style={{ color: '#78909c' }} /> },
    ],
  },
]

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { totalCount } = useCart()
  const [drawerOpen, setDrawerOpen] = useState(false)

  const getSelectedKey = () => {
    const path = location.pathname
    if (path === '/') return '/'
    const match = mainNavItems.find(item => item.key !== '/' && path.startsWith(item.key))
    return match?.key || ''
  }

  const getMobileSelectedKey = () => {
    const path = location.pathname
    if (path === '/') return '/'
    const match = mobileNavItems.find(item => item.key !== '/' && path.startsWith(item.key))
    return match?.key || ''
  }

  const selectedKey = getSelectedKey()

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* ===== Desktop Header ===== */}
      <Header className="desktop-header" style={{
        background: '#fff',
        padding: 0,
        height: 'auto',
        lineHeight: 'normal',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 1px 8px rgba(0,0,0,0.06)',
        borderBottom: '1px solid #f0f0f0',
      }}>
        {/* Top bar */}
        <div style={{
          background: 'linear-gradient(90deg, #1a3c2e 0%, #2c6b4f 50%, #1a3c2e 100%)',
          height: 36,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 32,
          fontSize: 12,
          color: 'rgba(255,255,255,0.7)',
        }}>
          <span>🌿 传承本草智慧 · 守护自然健康</span>
          <span style={{ opacity: 0.4 }}>|</span>
          <span><PhoneOutlined /> 客服热线：400-XXX-XXXX</span>
          <span style={{ opacity: 0.4 }}>|</span>
          <span><EnvironmentOutlined /> 全国包邮 · 道地药材</span>
        </div>

        {/* Main nav */}
        <div style={{
          maxWidth: 1280,
          margin: '0 auto',
          padding: '0 32px',
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          {/* Logo */}
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
            <LogoIcon style={{ fontSize: 38, color: '#2c6b4f' }} />
            <div>
              <div style={{
                fontSize: 20,
                fontWeight: 800,
                color: '#1a3c2e',
                letterSpacing: 3,
                lineHeight: 1.2,
                fontFamily: "'KaiTi', 'STKaiti', serif",
              }}>
                草木沈塘
              </div>
              <div style={{ fontSize: 10, color: '#8fae9b', letterSpacing: 1, marginTop: -1 }}>
                CAOMUSHENTANG
              </div>
            </div>
          </Link>

          {/* Nav items */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: 4, height: 64 }}>
            {mainNavItems.map(item => {
              const isActive = selectedKey === item.key
              return (
                <div
                  key={item.key}
                  onClick={() => navigate(item.key)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 5,
                    padding: '6px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    fontSize: 14,
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? '#2c6b4f' : '#555',
                    background: isActive ? '#edf7f0' : 'transparent',
                    transition: 'all 0.25s ease',
                    position: 'relative',
                    whiteSpace: 'nowrap',
                  }}
                  onMouseEnter={e => {
                    if (!isActive) {
                      e.currentTarget.style.color = '#2c6b4f'
                      e.currentTarget.style.background = '#f5faf7'
                    }
                  }}
                  onMouseLeave={e => {
                    if (!isActive) {
                      e.currentTarget.style.color = '#555'
                      e.currentTarget.style.background = 'transparent'
                    }
                  }}
                >
                  <span style={{ fontSize: 15 }}>{item.icon}</span>
                  {item.label}
                  {isActive && (
                    <motion.div
                      layoutId="nav-indicator"
                      style={{
                        position: 'absolute',
                        bottom: -1,
                        left: '20%',
                        right: '20%',
                        height: 2,
                        background: '#2c6b4f',
                        borderRadius: 1,
                      }}
                      transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                    />
                  )}
                </div>
              )
            })}
          </nav>

          {/* Right actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
            <Tooltip title="购物车">
              <Badge count={totalCount} size="small" offset={[-4, 4]}>
                <Button
                  type="text"
                  icon={<ShoppingCartOutlined style={{ fontSize: 18 }} />}
                  onClick={() => navigate('/cart')}
                  style={{ color: '#555', width: 40, height: 40, borderRadius: 10 }}
                />
              </Badge>
            </Tooltip>
            <Tooltip title="个人中心">
              <Button
                type="text"
                icon={<UserOutlined style={{ fontSize: 16 }} />}
                onClick={() => navigate('/profile')}
                style={{ color: '#555', width: 40, height: 40, borderRadius: 10 }}
              />
            </Tooltip>
          </div>
        </div>
      </Header>

      {/* ===== Mobile Header ===== */}
      <Header className="mobile-header" style={{
        background: '#fff',
        padding: '0 16px',
        display: 'none',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: 52,
        boxShadow: '0 1px 6px rgba(0,0,0,0.06)',
        borderBottom: '1px solid #f0f0f0',
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <LogoIcon style={{ fontSize: 28, color: '#2c6b4f' }} />
          <span style={{ color: '#1a3c2e', fontSize: 17, fontWeight: 700, letterSpacing: 2 }}>草木沈塘</span>
        </Link>
        <div style={{ display: 'flex', gap: 4 }}>
          <Badge count={totalCount} size="small" offset={[-4, 4]}>
            <Button type="text" icon={<ShoppingCartOutlined style={{ fontSize: 18, color: '#555' }} />} onClick={() => navigate('/cart')} style={{ width: 36, height: 36 }} />
          </Badge>
          <Button type="text" icon={<MenuOutlined style={{ fontSize: 18, color: '#555' }} />} onClick={() => setDrawerOpen(true)} style={{ width: 36, height: 36 }} />
        </div>
      </Header>

      {/* ===== Mobile Drawer ===== */}
      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <LogoIcon style={{ fontSize: 28, color: '#2c6b4f' }} />
            <div>
              <div style={{ fontWeight: 700, color: '#1a3c2e', fontSize: 15 }}>草木沈塘</div>
              <div style={{ fontSize: 10, color: '#8fae9b' }}>传承本草智慧</div>
            </div>
          </div>
        }
        placement="right"
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
        width={300}
        styles={{ body: { padding: '8px 16px' } }}
      >
        {drawerMenuGroups.map((group, gi) => (
          <div key={gi} style={{ marginBottom: 16 }}>
            <Text type="secondary" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, display: 'block', marginBottom: 8, paddingLeft: 4 }}>
              {group.title}
            </Text>
            {group.items.map(item => {
              const isActive = location.pathname === item.key
              return (
                <div
                  key={item.key}
                  onClick={() => { navigate(item.key); setDrawerOpen(false) }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '12px 12px',
                    borderRadius: 10,
                    cursor: 'pointer',
                    background: isActive ? '#edf7f0' : 'transparent',
                    marginBottom: 2,
                    transition: 'background 0.2s',
                  }}
                >
                  <span style={{ fontSize: 18 }}>{item.icon}</span>
                  <span style={{ flex: 1, fontWeight: isActive ? 600 : 400, color: isActive ? '#2c6b4f' : '#333' }}>{item.label}</span>
                  <RightOutlined style={{ fontSize: 10, color: '#ccc' }} />
                </div>
              )
            })}
            {gi < drawerMenuGroups.length - 1 && <Divider style={{ margin: '8px 0' }} />}
          </div>
        ))}
      </Drawer>

      {/* ===== Content ===== */}
      <Content style={{ padding: 0, minHeight: 'calc(100vh - 164px)' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </Content>

      {/* ===== Desktop Footer ===== */}
      <Footer className="desktop-footer" style={{ background: '#1a3c2e', padding: 0 }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '48px 32px 24px' }}>
          <div style={{ display: 'flex', gap: 64, flexWrap: 'wrap', marginBottom: 40 }}>
            {/* Brand */}
            <div style={{ flex: '1 1 280px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <LogoIcon style={{ fontSize: 36, color: '#8fae9b' }} />
                <div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: '#fff', letterSpacing: 2 }}>草木沈塘</div>
                  <div style={{ fontSize: 10, color: '#5a8a6e', letterSpacing: 1 }}>CAOMUSHENTANG</div>
                </div>
              </div>
              <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 13, lineHeight: 1.8, display: 'block' }}>
                专注传统中药知识科普与优质药材甄选，为您提供专业的中药调理方向参考与品质药材服务。所有内容仅供科普参考，不构成医疗建议。
              </Text>
            </div>

            {/* Links */}
            {[
              { title: '产品服务', links: [
                { label: '本草百科', path: '/herbs' },
                { label: '药材商城', path: '/products' },
                { label: 'AI 问诊', path: '/diagnosis' },
                { label: '在线咨询', path: '/consultation' },
              ]},
              { title: '用户中心', links: [
                { label: '我的订单', path: '/orders' },
                { label: '问诊历史', path: '/diagnosis/history' },
                { label: '会员中心', path: '/membership' },
                { label: '个人中心', path: '/profile' },
              ]},
              { title: '关于我们', links: [
                { label: '品牌故事', path: '/about' },
                { label: '联系我们', path: '/about' },
                { label: '加入我们', path: '/about' },
              ]},
            ].map((col, i) => (
              <div key={i} style={{ flex: '0 0 140px' }}>
                <Text style={{ color: '#fff', fontWeight: 600, fontSize: 14, display: 'block', marginBottom: 16 }}>{col.title}</Text>
                {col.links.map((link, j) => (
                  <Link key={j} to={link.path} style={{ display: 'block', color: 'rgba(255,255,255,0.45)', fontSize: 13, marginBottom: 10, transition: 'color 0.2s' }}
                    onMouseEnter={e => (e.currentTarget.style.color = '#8fae9b')}
                    onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.45)')}>
                    {link.label}
                  </Link>
                ))}
              </div>
            ))}
          </div>

          <Divider style={{ borderColor: 'rgba(255,255,255,0.08)', margin: '0 0 20px' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <Text style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12 }}>
              © 2024 草木沈塘 CAOMUSHENTANG · 本平台内容仅供科普参考，不构成医疗建议
            </Text>
            <Space size={16}>
              <WechatOutlined style={{ color: 'rgba(255,255,255,0.3)', fontSize: 18 }} />
              <PhoneOutlined style={{ color: 'rgba(255,255,255,0.3)', fontSize: 18 }} />
            </Space>
          </div>
        </div>
      </Footer>

      {/* ===== Mobile Bottom Tab ===== */}
      <div className="mobile-tab-bar" style={{
        position: 'fixed', bottom: 0, left: 0, right: 0,
        height: 56, background: '#fff',
        borderTop: '1px solid #eee',
        display: 'none',
        justifyContent: 'space-around',
        alignItems: 'center',
        zIndex: 100,
        boxShadow: '0 -1px 8px rgba(0,0,0,0.04)',
      }}>
        {mobileNavItems.map(item => {
          const isActive = getMobileSelectedKey() === item.key
          return (
            <div
              key={item.key}
              onClick={() => navigate(item.key)}
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                gap: 1, cursor: 'pointer', flex: 1, paddingTop: 6,
                color: isActive ? '#2c6b4f' : '#aaa',
                transition: 'color 0.2s',
              }}
            >
              <div style={{ position: 'relative', fontSize: 20, lineHeight: 1 }}>
                {item.key === '/cart' ? (
                  <Badge count={totalCount} size="small" offset={[6, -4]}>{item.icon}</Badge>
                ) : item.icon}
                {isActive && (
                  <motion.div layoutId="mobile-tab-dot" style={{
                    position: 'absolute', bottom: -4, left: '50%', transform: 'translateX(-50%)',
                    width: 4, height: 4, borderRadius: 2, background: '#2c6b4f',
                  }} />
                )}
              </div>
              <span style={{ fontSize: 10, fontWeight: isActive ? 600 : 400, marginTop: 2 }}>{item.label}</span>
            </div>
          )
        })}
      </div>

      {/* ===== Responsive CSS ===== */}
      <style>{`
        .desktop-header { display: block !important; }
        .mobile-header { display: none !important; }
        .desktop-footer { display: block !important; }
        .mobile-tab-bar { display: none !important; }
        @media (max-width: 900px) {
          .desktop-header { display: none !important; }
          .mobile-header { display: flex !important; }
          .desktop-footer { display: none !important; }
          .mobile-tab-bar { display: flex !important; }
          .ant-layout-content { padding-bottom: 64px !important; }
        }
      `}</style>
    </AntLayout>
  )
}
