import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Typography, Tag, Spin, Button, Space, Divider, Alert, Row, Col, InputNumber, message, Badge } from 'antd'
import { ArrowLeftOutlined, ShoppingCartOutlined, SafetyCertificateOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getProductDetail } from '../api/products'
import { useCart } from '../contexts/CartContext'
import { mockProducts } from '../mock/data'
import type { Product } from '../types'

const { Title, Text, Paragraph } = Typography

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { addItem } = useCart()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [quantity, setQuantity] = useState(1)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    getProductDetail(id)
      .then(setProduct)
      .catch(() => {
        const mock = mockProducts.find(p => p.id === id)
        if (mock) setProduct(mock)
        else setError('加载商品详情失败')
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleAddToCart = async () => {
    if (!product || adding) return
    setAdding(true)
    try {
      await addItem(product.id, quantity)
      message.success({ content: '已加入购物车', icon: <CheckCircleOutlined style={{ color: '#2c6b4f' }} /> })
    } catch {
      message.error('加入购物车失败，请重试')
    } finally {
      setAdding(false)
    }
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 120 }}><Spin size="large" /></div>
  if (error) return (
    <div style={{ maxWidth: 800, margin: '48px auto', padding: '0 24px' }}>
      <Alert type="error" message={error} showIcon action={<Button onClick={() => window.location.reload()}>重试</Button>} />
    </div>
  )
  if (!product) return null

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>返回</Button>

        <Card style={{ borderRadius: 20, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}
          styles={{ body: { padding: 0 } }}>
          <Row>
            <Col xs={24} md={10}>
              <div style={{
                height: 360, background: 'linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 80, borderRadius: '20px 0 0 20px',
              }}>
                🏷️
              </div>
            </Col>
            <Col xs={24} md={14}>
              <div style={{ padding: '32px 28px' }}>
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  <div>
                    {product.category && <Tag color="green" style={{ marginBottom: 8 }}>{product.category}</Tag>}
                    <Title level={3} style={{ margin: 0 }}>{product.name}</Title>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #fff5f5 0%, #ffebee 100%)',
                    borderRadius: 12, padding: '16px 20px',
                  }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>价格</Text>
                    <div>
                      <Text style={{ color: '#e53e3e', fontSize: 32, fontWeight: 700 }}>¥{product.price.toFixed(2)}</Text>
                      {product.specification && (
                        <Text type="secondary" style={{ marginLeft: 8 }}>/ {product.specification}</Text>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    {product.stock > 0 ? (
                      <Badge status="success" text={<Text style={{ color: '#38a169' }}>有货 · 库存 {product.stock}</Text>} />
                    ) : (
                      <Badge status="error" text={<Text type="danger">暂时缺货</Text>} />
                    )}
                  </div>

                  <Divider style={{ margin: '8px 0' }} />

                  {product.description && (
                    <div>
                      <Text type="secondary" style={{ fontSize: 12 }}>商品描述</Text>
                      <Paragraph style={{ marginTop: 4, lineHeight: 1.8 }}>{product.description}</Paragraph>
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 8 }}>
                    <Text>数量：</Text>
                    <InputNumber min={1} max={product.stock} value={quantity} onChange={(v) => setQuantity(v || 1)} style={{ width: 100 }} />
                  </div>

                  <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                    <Button
                      type="primary" size="large" icon={<ShoppingCartOutlined />}
                      onClick={handleAddToCart} loading={adding}
                      disabled={product.stock === 0}
                      style={{ flex: 1, height: 48, borderRadius: 12, fontWeight: 600 }}
                    >
                      {product.stock === 0 ? '暂时缺货' : '加入购物车'}
                    </Button>
                  </div>

                  <Space style={{ marginTop: 8 }}>
                    <Tag icon={<SafetyCertificateOutlined />} color="green">品质保障</Tag>
                    <Tag icon={<CheckCircleOutlined />} color="blue">道地药材</Tag>
                  </Space>
                </Space>
              </div>
            </Col>
          </Row>
        </Card>
      </motion.div>
    </div>
  )
}
