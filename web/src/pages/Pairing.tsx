import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, Typography, Tag, Button, Spin, Alert, Space, Row, Col, Badge, Divider, Empty } from 'antd'
import { ExperimentOutlined, CheckCircleOutlined, ReloadOutlined, WarningOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getHerbList } from '../api/herbs'
import { submitPairing } from '../api/ai'
import { mockHerbs } from '../mock/data'
import { HerbLeafIcon } from '../assets/icons'
import type { HerbListItem, PairingResult } from '../types'

const { Title, Text, Paragraph } = Typography

export default function Pairing() {
  const [herbs, setHerbs] = useState<HerbListItem[]>([])
  const [herbsLoading, setHerbsLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PairingResult | null>(null)

  useEffect(() => {
    getHerbList({ page: 1, page_size: 100 })
      .then(data => setHerbs(data.items))
      .catch(() => setHerbs(mockHerbs))
      .finally(() => setHerbsLoading(false))
  }, [])

  const toggleHerb = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  const handleSubmit = async () => {
    if (selectedIds.size === 0) return
    setLoading(true); setError(null)
    try {
      setResult(await submitPairing(Array.from(selectedIds)))
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取搭配建议失败')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => { setResult(null); setSelectedIds(new Set()); setError(null) }

  if (herbsLoading) return <div style={{ textAlign: 'center', padding: 120 }}><Spin size="large" /></div>

  if (result) {
    return (
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px 24px 48px' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{
            background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
            borderRadius: 16, padding: '32px 24px', marginBottom: 24, textAlign: 'center',
          }}>
            <CheckCircleOutlined style={{ fontSize: 48, color: '#2c6b4f', marginBottom: 12 }} />
            <Title level={3} style={{ margin: 0, color: '#2c6b4f' }}>搭配建议结果</Title>
          </div>

          <Alert type="warning" showIcon icon={<WarningOutlined />} message="免责声明"
            description="以下内容仅为中药搭配方向参考，不构成医疗建议。" style={{ marginBottom: 24, borderRadius: 12 }} />

          <Card style={{ borderRadius: 16, border: 'none', marginBottom: 16 }}>
            <Title level={5}><ExperimentOutlined /> 搭配思路</Title>
            <Paragraph style={{ lineHeight: 2, background: '#f9fafb', padding: 16, borderRadius: 8 }}>
              {result.suggestion}
            </Paragraph>
          </Card>

          <Title level={5} style={{ marginBottom: 12 }}>中药详情</Title>
          <Row gutter={[12, 12]}>
            {result.herbs.map(herb => (
              <Col xs={24} md={12} key={herb.id}>
                <Card size="small" style={{ borderRadius: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <HerbLeafIcon style={{ fontSize: 20, color: '#2c6b4f' }} />
                    <Link to={`/herbs/${herb.id}`}><Text strong style={{ color: '#2c6b4f' }}>{herb.name}</Text></Link>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>不适合人群：{herb.unsuitable_groups}</Text>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>注意事项：{herb.precautions}</Text>
                </Card>
              </Col>
            ))}
          </Row>

          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Button icon={<ReloadOutlined />} onClick={handleReset} size="large" style={{ borderRadius: 10 }}>重新选择</Button>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{
          background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24, textAlign: 'center',
        }}>
          <ExperimentOutlined style={{ fontSize: 48, color: '#e65100', marginBottom: 12 }} />
          <Title level={2} style={{ margin: 0, color: '#e65100' }}>中药搭配建议</Title>
          <Text type="secondary" style={{ fontSize: 15 }}>选择一味或多味中药，获取 AI 搭配思路建议</Text>
        </div>

        {error && <Alert type="error" message={error} showIcon closable style={{ marginBottom: 16, borderRadius: 8 }} />}

        <Card style={{ borderRadius: 16, border: 'none', marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <Text strong>选择中药</Text>
            <Badge count={selectedIds.size} style={{ backgroundColor: '#2c6b4f' }}>
              <Tag color="green">已选择</Tag>
            </Badge>
          </div>

          {herbs.length === 0 ? (
            <Empty description="暂无可选中药" />
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {herbs.map(herb => (
                <Tag
                  key={herb.id}
                  color={selectedIds.has(herb.id) ? 'green' : undefined}
                  style={{
                    cursor: 'pointer', padding: '6px 16px', borderRadius: 20, fontSize: 13,
                    border: selectedIds.has(herb.id) ? undefined : '1px solid #d9d9d9',
                    transition: 'all 0.2s',
                  }}
                  onClick={() => toggleHerb(herb.id)}
                >
                  {selectedIds.has(herb.id) && <CheckCircleOutlined style={{ marginRight: 4 }} />}
                  {herb.name}
                </Tag>
              ))}
            </div>
          )}
        </Card>

        <Button
          type="primary" size="large" block
          icon={<ExperimentOutlined />}
          disabled={loading || selectedIds.size === 0}
          loading={loading}
          onClick={handleSubmit}
          style={{ height: 48, borderRadius: 12, fontWeight: 600 }}
        >
          {loading ? '分析中...' : '获取搭配建议'}
        </Button>
      </motion.div>
    </div>
  )
}
