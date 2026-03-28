import { useState, useEffect, useCallback } from 'react'
import { Card, Typography, Collapse, Tag, Empty, Spin, Pagination, Space } from 'antd'
import { HistoryOutlined, UserOutlined, MedicineBoxOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getDiagnosisHistory } from '../api/ai'
import { mockDiagnosisHistory } from '../mock/data'
import type { DiagnosisHistoryItem } from '../types'

const { Title, Text, Paragraph } = Typography

export default function DiagnosisHistory() {
  const [items, setItems] = useState<DiagnosisHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize] = useState(20)

  const fetchData = useCallback(async (p: number) => {
    setLoading(true)
    try {
      const res = await getDiagnosisHistory(p)
      setItems(res.items)
      setTotal(res.total)
    } catch {
      setItems(mockDiagnosisHistory)
      setTotal(mockDiagnosisHistory.length)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData(page) }, [page, fetchData])

  const formatTime = (iso: string) => new Date(iso).toLocaleString('zh-CN')

  if (loading) return <div style={{ textAlign: 'center', padding: 120 }}><Spin size="large" /></div>

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{
          background: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24,
        }}>
          <HistoryOutlined style={{ fontSize: 36, color: '#6a1b9a', marginBottom: 8 }} />
          <Title level={2} style={{ margin: 0, color: '#6a1b9a' }}>问诊历史</Title>
          <Text type="secondary">查看您的历次问诊记录与 AI 分析结果</Text>
        </div>

        {items.length === 0 ? (
          <Empty description="暂无问诊记录" style={{ padding: 80 }} />
        ) : (
          <>
            <Collapse
              accordion
              style={{ background: 'transparent', border: 'none' }}
              items={items.map((item, i) => ({
                key: item.id,
                label: (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <div>
                      <Text strong style={{ display: 'block' }}>{item.input_data.symptoms.slice(0, 40)}...</Text>
                      <Space size={8} style={{ marginTop: 4 }}>
                        <Tag icon={<ClockCircleOutlined />} color="default">{formatTime(item.created_at)}</Tag>
                        <Tag color="blue">{item.input_data.gender} · {item.input_data.age}岁</Tag>
                      </Space>
                    </div>
                  </div>
                ),
                children: (
                  <div>
                    <Card size="small" style={{ marginBottom: 12, borderRadius: 8, background: '#f9fafb' }}>
                      <Space direction="vertical" size={4}>
                        <Text type="secondary"><UserOutlined /> 基本信息：{item.input_data.gender}，{item.input_data.age}岁</Text>
                        <Text type="secondary"><MedicineBoxOutlined /> 主要不适：{item.input_data.symptoms}</Text>
                        {item.input_data.allergies && <Text type="secondary">过敏史：{item.input_data.allergies}</Text>}
                        {item.input_data.medications && <Text type="secondary">当前用药：{item.input_data.medications}</Text>}
                      </Space>
                    </Card>
                    <div style={{ background: '#f0f7f4', borderRadius: 8, padding: 16 }}>
                      <Text strong style={{ display: 'block', marginBottom: 8, color: '#2c6b4f' }}>
                        <MedicineBoxOutlined /> AI 分析结果
                      </Text>
                      <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8, color: '#333' }}>
                        {item.ai_output}
                      </div>
                    </div>
                  </div>
                ),
                style: { marginBottom: 12, borderRadius: 12, border: '1px solid #f0f0f0', overflow: 'hidden' },
              }))}
            />

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Pagination current={page} total={total} pageSize={pageSize} onChange={setPage} showSizeChanger={false} />
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
