import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Card, Form, Input, Button, Typography, Space, message, Divider } from 'antd'
import { MobileOutlined, SafetyOutlined, LoginOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { LogoIcon, WaveDecoration, HerbLeafIcon } from '../assets/icons'

const { Title, Text, Paragraph } = Typography

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (values: { phone: string; code: string }) => {
    setLoading(true)
    try {
      await login(values.phone, values.code)
      const from = (location.state as { from?: string })?.from || '/'
      navigate(from, { replace: true })
    } catch (err) {
      message.error(err instanceof Error ? err.message : '登录失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e4d38 0%, #2c6b4f 40%, #3d8b6a 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Decorative */}
      <div style={{ position: 'absolute', top: '10%', left: '5%', opacity: 0.06, fontSize: 300 }}>
        <HerbLeafIcon />
      </div>
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, color: '#fff' }}>
        <WaveDecoration style={{ width: '100%', height: 120 }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5 }}
        style={{ width: '100%', maxWidth: 420, position: 'relative', zIndex: 1 }}
      >
        <Card
          style={{
            borderRadius: 20,
            boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
            border: 'none',
          }}
          styles={{ body: { padding: '40px 32px' } }}
        >
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <LogoIcon style={{ fontSize: 56, color: '#2c6b4f', marginBottom: 12 }} />
            <Title level={3} style={{ margin: 0, color: '#2c6b4f' }}>草木沈塘</Title>
            <Text type="secondary">传承本草智慧，守护自然健康</Text>
          </div>

          <Form layout="vertical" onFinish={handleSubmit} size="large">
            <Form.Item
              name="phone"
              rules={[
                { required: true, message: '请输入手机号' },
                { pattern: /^\d{11}$/, message: '手机号须为 11 位数字' },
              ]}
            >
              <Input
                prefix={<MobileOutlined style={{ color: '#2c6b4f' }} />}
                placeholder="请输入 11 位手机号"
                maxLength={11}
                style={{ borderRadius: 10, height: 48 }}
              />
            </Form.Item>

            <Form.Item
              name="code"
              rules={[{ required: true, message: '请输入验证码' }]}
            >
              <Input
                prefix={<SafetyOutlined style={{ color: '#2c6b4f' }} />}
                placeholder="请输入验证码"
                style={{ borderRadius: 10, height: 48 }}
                suffix={
                  <Button type="link" size="small" style={{ padding: 0, fontSize: 13 }}>
                    获取验证码
                  </Button>
                }
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                icon={<LoginOutlined />}
                style={{
                  height: 48,
                  borderRadius: 10,
                  fontSize: 16,
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #2c6b4f 0%, #3d8b6a 100%)',
                }}
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          <Divider style={{ margin: '16px 0' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>或</Text>
          </Divider>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary">还没有账号？</Text>
            <Link to="/register" style={{ fontWeight: 600, marginLeft: 4 }}>立即注册</Link>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
