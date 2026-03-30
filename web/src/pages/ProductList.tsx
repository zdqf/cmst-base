import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Tag, Typography, Pagination, Empty, Spin, Space } from 'antd'
import { ShopOutlined, FireOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getProductList } from '../api/products'
import { mockProducts } from '../mock/data'
import { HerbBagIcon, TeaCupIcon, GiftBoxIcon, BottleIcon } from '../assets/icons'
import { formatPrice, formatPriceInt, formatPriceDec } from '../utils/format'
import type { Product } from '../types'

const { Title, Text } = Typography

const PAGE_SIZE = 20

const CATEGORIES = [
  { label: '全部', value: '', color: 'default' },
  { label: '原药材', value: '原药材', color: 'green' },
  { label: '简加工产品', value: '简加工产品', color: 'blue' },
  { label: '调理组合包', value: '调理组合包', color: 'orange' },
]

const productIllustrations = [
  <HerbBagIcon style={{ fontSize: 72 }} />,
  <BottleIcon style={{ fontSize: 72 }} />,
  <TeaCupIcon style={{ fontSize: 72 }} />,
  <GiftBoxIcon style={{ fontSize: 72 }} />,
  <HerbBagIcon style={{ fontSize: 72 }} />,
  <TeaCupIcon style={{ fontSize: 72 }} />,
  <GiftBoxIcon style={{ fontSize: 72 }} />,
  <BottleIcon style={{ fontSize: 72 }} />,
]

const productEmojis = ['🌿', '🍵', '🏷️', '💊', '🎁', '🧴', '📦', '🌸']

export default function ProductList() {
  const navigate = useNavigate()
  const [items, setItems] = useState<Product[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, unknown> = { page, page_size: PAGE_SIZE }
      if (category) params.category = category
      const data = await getProductList(params as Parameters<typeof getProductList>[0])
      setItems(data.items)
      setTotal(data.total)
    } catch {
      let filtered = mockProducts
      if (category) filtered = filtered.filter(p => p.category === category)
      setItems(filtered)
      setTotal(filtered.length)
    } finally {
      setLoading(false)
    }
  }, [page, category])

  useEffect(() => { fetchData() }, [fetchData])

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 24px 48px' }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{
          background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24,
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', right: 24, top: '50%', transform: 'translateY(-50%)', opacity: 0.15, fontSize: 100 }}>
            <ShopOutlined />
          </div>
          <Title level={2} style={{ margin: 0, color: '#e65100' }}>
            <ShopOutlined style={{ marginRight: 8 }} />药材商城
          </Title>
          <Text type="secondary" style={{ fontSize: 15 }}>精选道地药材，品质保障，产地直供</Text>
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
        <Empty description="暂无商品数据" style={{ padding: 80 }} />
      ) : (
        <>
          <Row gutter={[16, 16]}>
            {items.map((product, i) => (
              <Col xs={12} sm={8} md={6} key={product.id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Card
                    hoverable
                    onClick={() => navigate(`/products/${product.id}`)}
                    style={{ borderRadius: 12, border: 'none', overflow: 'hidden' }}
                    styles={{ body: { padding: 0 } }}
                  >
                    <div style={{
                      height: 160, background: 'linear-gradient(135deg, #fafbfa 0%, #f0f2f0 100%)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 48, position: 'relative',
                    }}>
                      {productIllustrations[i % productIllustrations.length]}
                      {product.stock <= 10 && product.stock > 0 && (
                        <Tag color="red" style={{ position: 'absolute', top: 8, right: 8, fontSize: 11 }}>
                          <FireOutlined /> 即将售罄
                        </Tag>
                      )}
                      {product.stock === 0 && (
                        <div style={{
                          position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                          <Tag color="default" style={{ fontSize: 14 }}>暂时缺货</Tag>
                        </div>
                      )}
                    </div>
                    <div style={{ padding: '12px 16px' }}>
                      <Text strong style={{ display: 'block', fontSize: 14, marginBottom: 4 }} ellipsis>
                        {product.name}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }} ellipsis>
                        {product.specification || product.category}
                      </Text>
                      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                        <div>
                          <Text style={{ color: '#e53e3e', fontSize: 20, fontWeight: 700 }}>¥{formatPriceInt(product.price)}</Text>
                          <Text type="secondary" style={{ fontSize: 11, marginLeft: 4 }}>.{formatPriceDec(product.price)}</Text>
                        </div>
                        <Tag color="green" style={{ fontSize: 11, margin: 0 }}>{product.category}</Tag>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>

          <div style={{ textAlign: 'center', marginTop: 32 }}>
            <Pagination
              current={page} total={total} pageSize={PAGE_SIZE}
              onChange={(p) => setPage(p)} showSizeChanger={false}
              showTotal={(t) => `共 ${t} 件商品`}
            />
          </div>
        </>
      )}
    </div>
  )
}
