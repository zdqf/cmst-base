import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Input, Tag, Typography, Pagination, Empty, Spin, Space, Badge } from 'antd'
import { SearchOutlined, FireOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getHerbList } from '../api/herbs'
import { mockHerbs, hotSearches } from '../mock/data'
import { HerbLeafIcon } from '../assets/icons'
import type { HerbListItem } from '../types'

const { Title, Text } = Typography

const PAGE_SIZE = 20

const CATEGORIES = [
  { label: '全部', value: '', color: 'default' },
  { label: '补益药', value: '补益药', color: 'green' },
  { label: '清热药', value: '清热药', color: 'blue' },
  { label: '解表药', value: '解表药', color: 'orange' },
  { label: '理气药', value: '理气药', color: 'purple' },
  { label: '活血药', value: '活血药', color: 'red' },
]

const herbColors = ['#e8f5e9', '#e3f2fd', '#fff3e0', '#f3e5f5', '#ffebee', '#e0f2f1', '#fce4ec', '#f1f8e9']

export default function HerbList() {
  const navigate = useNavigate()
  const [items, setItems] = useState<HerbListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(true)
  const [useMock, setUseMock] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, unknown> = { page, page_size: PAGE_SIZE }
      if (category) params.category = category
      if (keyword) params.keyword = keyword
      const data = await getHerbList(params as Parameters<typeof getHerbList>[0])
      setItems(data.items)
      setTotal(data.total)
    } catch {
      // Fallback to mock data
      let filtered = mockHerbs
      if (category) filtered = filtered.filter(h => h.category === category)
      if (keyword) filtered = filtered.filter(h => h.name.includes(keyword))
      setItems(filtered)
      setTotal(filtered.length)
      setUseMock(true)
    } finally {
      setLoading(false)
    }
  }, [page, category, keyword])

  useEffect(() => { fetchData() }, [fetchData])

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 24px 48px' }}>
      {/* Page Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{
          background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24,
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', right: 24, top: '50%', transform: 'translateY(-50%)', opacity: 0.1, fontSize: 120 }}>
            <HerbLeafIcon />
          </div>
          <Title level={2} style={{ margin: 0, color: '#2c6b4f' }}>中药科普</Title>
          <Text type="secondary" style={{ fontSize: 15 }}>探索传统中药智慧，了解每一味本草的故事</Text>

          <div style={{ marginTop: 16 }}>
            <Input.Search
              placeholder="搜索中药名称..."
              allowClear
              enterButton={<><SearchOutlined /> 搜索</>}
              size="large"
              style={{ maxWidth: 480 }}
              onSearch={(v) => { setKeyword(v.trim()); setPage(1) }}
            />
          </div>

          <div style={{ marginTop: 12 }}>
            <Space size={4} wrap>
              <Text type="secondary" style={{ fontSize: 12, marginRight: 4 }}>
                <FireOutlined /> 热搜：
              </Text>
              {hotSearches.map(s => (
                <Tag key={s} style={{ cursor: 'pointer', borderRadius: 12 }}
                  onClick={() => { setKeyword(s); setPage(1) }}>
                  {s}
                </Tag>
              ))}
            </Space>
          </div>
        </div>
      </motion.div>

      {/* Category Filter */}
      <div style={{ marginBottom: 24 }}>
        <Space size={[8, 8]} wrap>
          {CATEGORIES.map(cat => (
            <Tag
              key={cat.value}
              color={category === cat.value ? cat.color || 'green' : undefined}
              style={{
                cursor: 'pointer', padding: '4px 16px', borderRadius: 20, fontSize: 13,
                fontWeight: category === cat.value ? 600 : 400,
                border: category === cat.value ? undefined : '1px solid #d9d9d9',
              }}
              onClick={() => { setCategory(cat.value); setPage(1) }}
            >
              {cat.label}
            </Tag>
          ))}
        </Space>
      </div>

      {/* Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
      ) : items.length === 0 ? (
        <Empty description="暂无中药数据" style={{ padding: 80 }} />
      ) : (
        <>
          <Row gutter={[16, 16]}>
            {items.map((herb, i) => (
              <Col xs={12} sm={8} md={6} key={herb.id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Card
                    hoverable
                    onClick={() => navigate(`/herbs/${herb.id}`)}
                    style={{ borderRadius: 12, border: 'none', overflow: 'hidden' }}
                    styles={{ body: { padding: 0 } }}
                  >
                    <div style={{
                      height: 120,
                      background: `linear-gradient(135deg, ${herbColors[i % herbColors.length]} 0%, ${herbColors[(i + 1) % herbColors.length]} 100%)`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <HerbLeafIcon style={{ fontSize: 48, color: '#2c6b4f', opacity: 0.6 }} />
                    </div>
                    <div style={{ padding: '12px 16px' }}>
                      <Text strong style={{ display: 'block', fontSize: 15, marginBottom: 4 }}>{herb.name}</Text>
                      <Tag color="green" style={{ fontSize: 11 }}>{herb.category || '中药'}</Tag>
                    </div>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>

          <div style={{ textAlign: 'center', marginTop: 32 }}>
            <Pagination
              current={page}
              total={total}
              pageSize={PAGE_SIZE}
              onChange={(p) => setPage(p)}
              showSizeChanger={false}
              showTotal={(t) => `共 ${t} 味中药`}
            />
          </div>
        </>
      )}
    </div>
  )
}
