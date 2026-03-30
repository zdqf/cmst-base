import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Typography, Button, InputNumber, Empty, Spin, Space, Divider, Popconfirm, Row, Col, Tag } from 'antd'
import { ShoppingCartOutlined, DeleteOutlined, ShopOutlined, ArrowRightOutlined } from '@ant-design/icons'
import { motion, AnimatePresence } from 'framer-motion'
import { useCart } from '../contexts/CartContext'
import { mockCartItems } from '../mock/data'
import { formatPrice } from '../utils/format'

const { Title, Text } = Typography

export default function Cart() {
  const { items: cartItems, totalCount, totalPrice, fetchCart, updateQuantity, removeItem } = useCart()
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  // Use mock data if cart is empty after fetch
  const items = cartItems.length > 0 ? cartItems : (loading ? [] : mockCartItems)
  const count = cartItems.length > 0 ? totalCount : items.reduce((s, i) => s + i.quantity, 0)
  const price = cartItems.length > 0 ? totalPrice : items.reduce((s, i) => s + Number(i.product_price) * i.quantity, 0)

  useEffect(() => {
    fetchCart().catch(() => {}).finally(() => setLoading(false))
  }, [fetchCart])

  if (loading) return <div style={{ textAlign: 'center', padding: 120 }}><Spin size="large" /></div>

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '24px 24px 120px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ShoppingCartOutlined style={{ fontSize: 24, color: '#2c6b4f' }} />
            <Title level={3} style={{ margin: 0 }}>购物车</Title>
            <Tag color="green">{count} 件</Tag>
          </div>
        </div>

        {items.length === 0 ? (
          <Card style={{ borderRadius: 16, border: 'none', textAlign: 'center', padding: 48 }}>
            <Empty
              description="购物车是空的"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button type="primary" icon={<ShopOutlined />} onClick={() => navigate('/products')} style={{ borderRadius: 10 }}>
                去逛逛
              </Button>
            </Empty>
          </Card>
        ) : (
          <>
            <AnimatePresence>
              {items.map((item, i) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Card style={{ borderRadius: 12, border: 'none', marginBottom: 12 }} styles={{ body: { padding: '16px 20px' } }}>
                    <Row align="middle" gutter={16}>
                      <Col flex="60px">
                        <div style={{
                          width: 56, height: 56, borderRadius: 10,
                          background: 'linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28,
                        }}>
                          🏷️
                        </div>
                      </Col>
                      <Col flex="auto">
                        <Text strong style={{ display: 'block', marginBottom: 4 }}>{item.product_name}</Text>
                        <Text style={{ color: '#e53e3e', fontWeight: 600 }}>¥{formatPrice(item.product_price)}</Text>
                      </Col>
                      <Col>
                        <Space direction="vertical" align="end" size={8}>
                          <InputNumber
                            min={1} value={item.quantity} size="small"
                            onChange={(v) => v && updateQuantity(item.id, v)}
                            style={{ width: 90 }}
                          />
                          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              小计：<Text style={{ color: '#e53e3e' }}>¥{formatPrice(Number(item.product_price) * item.quantity)}</Text>
                            </Text>
                            <Popconfirm title="确定删除？" onConfirm={() => removeItem(item.id)} okText="确定" cancelText="取消">
                              <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                            </Popconfirm>
                          </div>
                        </Space>
                      </Col>
                    </Row>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Bottom Bar */}
            <div style={{
              position: 'fixed', bottom: 0, left: 0, right: 0,
              background: '#fff', borderTop: '1px solid #f0f0f0',
              padding: '12px 24px', zIndex: 99,
              boxShadow: '0 -4px 12px rgba(0,0,0,0.06)',
            }}>
              <div style={{ maxWidth: 900, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <Text type="secondary">共 {count} 件，合计</Text>
                  <Text style={{ color: '#e53e3e', fontSize: 24, fontWeight: 700, marginLeft: 8 }}>¥{formatPrice(price)}</Text>
                </div>
                <Button type="primary" size="large" icon={<ArrowRightOutlined />}
                  onClick={() => navigate('/order/confirm')}
                  style={{ height: 48, paddingInline: 40, borderRadius: 12, fontWeight: 600 }}>
                  去结算
                </Button>
              </div>
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
