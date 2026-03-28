import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Select, Button, Typography, Alert, Steps, Space, Tag } from 'antd'
import { MedicineBoxOutlined, UserOutlined, FileTextOutlined, SendOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { submitDiagnosis } from '../api/ai'
import type { DiagnosisRequest } from '../types'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

export default function Diagnosis() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form] = Form.useForm()

  const handleSubmit = async (values: DiagnosisRequest) => {
    setLoading(true)
    setError(null)
    try {
      const result = await submitDiagnosis({ ...values, age: Number(values.age) })
      navigate('/diagnosis/result', { state: { result } })
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24,
          textAlign: 'center',
        }}>
          <MedicineBoxOutlined style={{ fontSize: 48, color: '#1565c0', marginBottom: 12 }} />
          <Title level={2} style={{ margin: 0, color: '#1565c0' }}>AI 智能问诊</Title>
          <Text type="secondary" style={{ fontSize: 15 }}>基于传统中医理论，为您提供调理方向参考</Text>
        </div>

        {/* Steps */}
        <Steps
          current={0}
          size="small"
          style={{ marginBottom: 32 }}
          items={[
            { title: '填写信息', icon: <UserOutlined /> },
            { title: 'AI 分析', icon: <MedicineBoxOutlined /> },
            { title: '查看结果', icon: <FileTextOutlined /> },
          ]}
        />

        {error && <Alert type="error" message={error} showIcon closable style={{ marginBottom: 16, borderRadius: 8 }} />}

        <Card style={{ borderRadius: 16, border: 'none' }}>
          <Form form={form} layout="vertical" onFinish={handleSubmit} size="large">
            <Form.Item name="age" label="年龄" rules={[
              { required: true, message: '请输入年龄' },
              { type: 'number', min: 1, max: 150, message: '年龄须为 1-150', transform: Number },
            ]}>
              <Input type="number" placeholder="请输入年龄（1-150）" prefix={<UserOutlined style={{ color: '#999' }} />} style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item name="gender" label="性别" rules={[{ required: true, message: '请选择性别' }]}>
              <Select placeholder="请选择性别" style={{ borderRadius: 10 }}
                options={[{ value: '男', label: '男' }, { value: '女', label: '女' }]} />
            </Form.Item>

            <Form.Item name="symptoms" label="主要不适描述" rules={[
              { required: true, message: '请填写主要不适描述' },
              { max: 500, message: '不超过 500 字' },
            ]}>
              <TextArea rows={4} placeholder="请描述您的主要不适症状，如：近期感觉疲劳乏力，面色偏黄..." showCount maxLength={500} style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item name="allergies" label={<Space>既往过敏史 <Tag>选填</Tag></Space>}>
              <TextArea rows={2} placeholder="如有过敏史请填写" style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item name="medications" label={<Space>当前用药情况 <Tag>选填</Tag></Space>}>
              <TextArea rows={2} placeholder="如有正在服用的药物请填写" style={{ borderRadius: 10 }} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading} icon={<SendOutlined />}
                style={{ height: 48, borderRadius: 12, fontSize: 16, fontWeight: 600 }}>
                {loading ? '分析中...' : '提交问诊'}
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Alert
          style={{ marginTop: 24, borderRadius: 12 }}
          type="info" showIcon
          message="温馨提示"
          description="本功能基于传统中医理论提供调理方向参考，不构成医疗诊断或治疗建议。如有健康问题，请及时就医。"
        />
      </motion.div>
    </div>
  )
}
