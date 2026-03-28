import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Typography, Tag, Spin, Button, Space, Divider, Alert, Row, Col, Descriptions } from 'antd'
import { ArrowLeftOutlined, ExperimentOutlined, WarningOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getHerbDetail } from '../api/herbs'
import { mockHerbDetails } from '../mock/data'
import { HerbLeafIcon } from '../assets/icons'
import type { HerbDetail as HerbDetailType } from '../types'

const { Title, Text, Paragraph } = Typography

const FIELDS: { key: keyof HerbDetailType; label: string; icon: React.ReactNode; color: string }[] = [
  { key: 'origin_and_form', label: '来源与形态', icon: '🌱', color: '#e8f5e9' },
  { key: 'flavor_meridian', label: '性味归经', icon: '🎯', color: '#e3f2fd' },
  { key: 'common_pairings', label: '常见搭配方向', icon: '🤝', color: '#fff3e0' },
  { key: 'unsuitable_groups', label: '不适合人群', icon: '⚠️', color: '#ffebee' },
  { key: 'precautions', label: '注意事项', icon: '📋', color: '#f3e5f5' },
]

export default function HerbDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [herb, setHerb] = useState<HerbDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    setError(null)
    getHerbDetail(id)
      .then(setHerb)
      .catch(() => {
        // Fallback to mock
        const mock = mockHerbDetails[id]
        if (mock) setHerb(mock)
        else setError('加载失败，请重试')
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div style={{ textAlign: 'center', padding: 120 }}><Spin size="large" /></div>
  if (error) return (
    <div style={{ maxWidth: 800, margin: '48px auto', padding: '0 24px' }}>
      <Alert type="error" message={error} showIcon action={<Button onClick={() => window.location.reload()}>重试</Button>} />
    </div>
  )
  if (!herb) return null

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
          返回
        </Button>

        {/* Hero Card */}
        <Card style={{
          borderRadius: 20, border: 'none', overflow: 'hidden', marginBottom: 24,
          boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        }} styles={{ body: { padding: 0 } }}>
          <div style={{
            background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
            padding: '48px 32px', textAlign: 'center',
          }}>
            <HerbLeafIcon style={{ fontSize: 80, color: '#2c6b4f', marginBottom: 16 }} />
            <Title level={2} style={{ color: '#2c6b4f', margin: 0 }}>{herb.name}</Title>
            <Space style={{ marginTop: 12 }}>
              {herb.category && <Tag color="green" style={{ fontSize: 14, padding: '4px 16px' }}>{herb.category}</Tag>}
              <Tag color="blue" style={{ fontSize: 14, padding: '4px 16px' }}>
                <ExperimentOutlined /> 查看搭配
              </Tag>
            </Space>
          </div>
        </Card>

        {/* Detail Sections */}
        <Row gutter={[16, 16]}>
          {FIELDS.map(({ key, label, icon, color }) => (
            <Col xs={24} md={key === 'origin_and_form' ? 24 : 12} key={key}>
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <Card
                  style={{ borderRadius: 12, border: 'none', height: '100%' }}
                  styles={{ body: { padding: '20px 24px' } }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <div style={{
                      width: 36, height: 36, borderRadius: 10, background: color,
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
                    }}>
                      {icon}
                    </div>
                    <Text strong style={{ fontSize: 15 }}>{label}</Text>
                  </div>
                  <Paragraph style={{ margin: 0, color: '#555', lineHeight: 1.8 }}>
                    {(herb[key] as string) || '暂无信息'}
                  </Paragraph>
                </Card>
              </motion.div>
            </Col>
          ))}
        </Row>

        {/* Disclaimer */}
        <Alert
          style={{ marginTop: 24, borderRadius: 12 }}
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          message="免责声明"
          description="以上内容仅为传统中药知识科普与调理方向参考，不构成医疗诊断或治疗建议，如有健康问题请咨询专业医师。"
        />
      </motion.div>
    </div>
  )
}
