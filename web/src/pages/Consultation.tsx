import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Typography, Alert, Space, Tag } from 'antd'
import { MessageOutlined, UserOutlined, PhoneOutlined, FileTextOutlined, SendOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { submitConsultation } from '../api/consultation'
import type { ConsultationRequest } from '../types'

const { Title, Text } = Typography
const { TextArea } = Input

export default function Consultation() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (values: ConsultationRequest) => {
    setLoading(true); setError(null)
    try {
      const result = await submitConsultation(values)
      navigate('/consultation/success', { state: { result } })
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{
          background: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24, textAlign: 'center',
        }}>
          <MessageOutlined style={{ fontSize: 48, color: '#6a1b9a', marginBottom: 12 }} />
          <Title level={2} style={{ margin: 0, color: '#6a1b9a' }}>在线咨询</Title>
          <Text type="secondary" style={{ fontSize: 15 }}>专业中医师为您提供一对一咨询服务</Text>
        </div>

        {error && <Alert type="error" message={error} showIcon closable style={{ marginBottom: 16, borderRadius: 8 }} />}

        <Card style={{ borderRadius: 16, border: 'none' }}>
          <Form layout="vertical" onFinish={handleSubmit} size="large">
            <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请填写姓名' }, { max: 50, message: '不超过 50 字' }]}>
              <Input prefix={<UserOutlined style={{ color: '#999' }} />} placeholder="请输入姓名" style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item name="contact" label="联系方式" rules={[{ required: true, message: '请填写联系方式' }, { max: 50, message: '不超过 50 字' }]}>
              <Input prefix={<PhoneOutlined style={{ color: '#999' }} />} placeholder="请输入手机号或微信号" style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item name="subject" label="咨询主题" rules={[{ required: true, message: '请填写咨询主题' }, { max: 100, message: '不超过 100 字' }]}>
              <Input prefix={<FileTextOutlined style={{ color: '#999' }} />} placeholder="请输入咨询主题" style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item name="description" label="详细描述" rules={[{ required: true, message: '请填写详细描述' }, { max: 1000, message: '不超过 1000 字' }]}>
              <TextArea rows={5} placeholder="请详细描述您的咨询内容..." showCount maxLength={1000} style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading} icon={<SendOutlined />}
                style={{ height: 48, borderRadius: 12, fontSize: 16, fontWeight: 600 }}>
                {loading ? '提交中...' : '提交咨询'}
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <div style={{ marginTop: 24, display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Tag color="green" style={{ padding: '4px 12px' }}>🕐 工作日 9:00-18:00</Tag>
          <Tag color="blue" style={{ padding: '4px 12px' }}>💬 24小时内回复</Tag>
          <Tag color="purple" style={{ padding: '4px 12px' }}>🔒 信息保密</Tag>
        </div>
      </motion.div>
    </div>
  )
}
