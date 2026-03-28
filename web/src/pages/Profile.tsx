import { useNavigate } from 'react-router-dom'
import { Card, Typography, Button, Space, Avatar, Divider, Row, Col, Tag } from 'antd'
import {
  UserOutlined, ShoppingOutlined, HistoryOutlined, ShoppingCartOutlined,
  LogoutOutlined, MedicineBoxOutlined, ExperimentOutlined, MessageOutlined,
  RightOutlined, SettingOutlined, HeartOutlined, CrownOutlined,
} from '@ant-design/icons'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { LogoIcon } from '../assets/icons'

const { Title, Text } = Typography

const menuItems = [
  { label: '我的订单', path: '/orders', icon: <ShoppingOutlined style={{ color: '#1565c0' }} />, bg: '#e3f2fd' },
  { label: '问诊历史', path: '/diagnosis/history', icon: <HistoryOutlined style={{ color: '#6a1b9a' }} />, bg: '#f3e5f5' },
  { label: '购物车', path: '/cart', icon: <ShoppingCartOutlined style={{ color: '#e65100' }} />, bg: '#fff3e0' },
  { label: 'AI 问诊', path: '/diagnosis', icon: <MedicineBoxOutlined style={{ color: '#2c6b4f' }} />, bg: '#e8f5e9' },
  { label: '搭配建议', path: '/pairing', icon: <ExperimentOutlined style={{ color: '#c62828' }} />, bg: '#ffebee' },
  { label: '会员中心', path: '/membership', icon: <CrownOutlined style={{ color: '#f9a825' }} />, bg: '#fef9e7' },
]

export default function Profile() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '0 0 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Profile Header */}
        <div style={{
          background: 'linear-gradient(135deg, #1e4d38 0%, #2c6b4f 50%, #3d8b6a 100%)',
          padding: '48px 24px 64px', textAlign: 'center',
          position: 'relative',
        }}>
          <Avatar size={80} style={{ background: 'rgba(255,255,255,0.2)', border: '3px solid rgba(255,255,255,0.3)' }}
            icon={<UserOutlined style={{ fontSize: 36 }} />} />
          <Title level={4} style={{ color: '#fff', marginTop: 12, marginBottom: 4 }}>欢迎回来</Title>
          <Text style={{ color: 'rgba(255,255,255,0.7)' }}>草木沈塘会员</Text>
          <div style={{ marginTop: 12 }}>
            <Tag color="rgba(255,255,255,0.15)" style={{ color: '#fff', border: '1px solid rgba(255,255,255,0.2)' }}>
              <HeartOutlined /> 已登录
            </Tag>
          </div>
        </div>

        <div style={{ padding: '0 24px', marginTop: -32 }}>
          {/* Quick Stats */}
          <Card style={{ borderRadius: 16, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', marginBottom: 24 }}>
            <Row gutter={16} justify="space-around">
              {[
                { label: '订单', value: '3', path: '/orders' },
                { label: '问诊', value: '2', path: '/diagnosis/history' },
                { label: '购物车', value: '2', path: '/cart' },
              ].map(item => (
                <Col key={item.label} style={{ textAlign: 'center', cursor: 'pointer' }} onClick={() => navigate(item.path)}>
                  <Text style={{ fontSize: 24, fontWeight: 700, color: '#2c6b4f', display: 'block' }}>{item.value}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>{item.label}</Text>
                </Col>
              ))}
            </Row>
          </Card>

          {/* Menu Grid */}
          <Row gutter={[12, 12]} style={{ marginBottom: 24 }}>
            {menuItems.map((item, i) => (
              <Col xs={8} key={item.path}>
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                  <Card
                    hoverable
                    onClick={() => navigate(item.path)}
                    style={{ borderRadius: 12, border: 'none', textAlign: 'center' }}
                    styles={{ body: { padding: '20px 8px' } }}
                  >
                    <div style={{
                      width: 44, height: 44, borderRadius: 12, background: item.bg,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      margin: '0 auto 8px', fontSize: 20,
                    }}>
                      {item.icon}
                    </div>
                    <Text style={{ fontSize: 12 }}>{item.label}</Text>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>

          {/* Logout */}
          <Button
            block danger type="default"
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            style={{ height: 48, borderRadius: 12, fontSize: 15 }}
          >
            退出登录
          </Button>
        </div>
      </motion.div>
    </div>
  )
}
