import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Typography, Button, Alert, Divider, Space, Tag } from 'antd'
import { CheckCircleOutlined, ShoppingCartOutlined, SafetyCertificateOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { useCart } from '../contexts/CartContext'
import { createOrder } from '../api/orders'
import { formatPrice } from '../utils/format'

const { Title, Text } = Typography

export default function OrderConfirm() {
  const { items, totalPrice, clearCart } = useCart()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (items.length === 0) navigate('/cart', { replace: true })
  }, [items, navigate])

  if (items.length === 0) return null

  const handleSubmit = async () => {
    setSubmitting(true); setError(null)
    try {
      await createOrder({ items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity })) })
      clearCart()
      navigate('/orders')
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交订单失败')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Title level={3}><ShoppingCartOutlined /> 订单确认</Title>

        <Card style={{ borderRadius: 16, border: 'none', marginBottom: 16 }}>
          {items.map((item, i) => (
            <div key={item.id}>
              {i > 0 && <Divider style={{ margin: '12px 0' }} />}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <Text strong>{item.product_name}</Text>
                  <Text type="secondary" style={{ display: 'block', fontSize: 12 }}>
                    ¥{formatPrice(item.product_price)} × {item.quantity}
                  </Text>
                </div>
                <Text style={{ color: '#e53e3e', fontWeight: 600 }}>
                  ¥{formatPrice(Number(item.product_price) * item.quantity)}
                </Text>
              </div>
            </div>
          ))}

          <Divider />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text strong>应付总额</Text>
            <Text style={{ color: '#e53e3e', fontSize: 24, fontWeight: 700 }}>¥{formatPrice(totalPrice)}</Text>
          </div>
        </Card>

        {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16, borderRadius: 8 }} />}

        <Space direction="vertical" style={{ width: '100%' }} size={12}>
          <Button type="primary" size="large" block loading={submitting} icon={<CheckCircleOutlined />}
            onClick={handleSubmit} style={{ height: 48, borderRadius: 12, fontWeight: 600 }}>
            {submitting ? '提交中...' : '提交订单'}
          </Button>
          <div style={{ textAlign: 'center' }}>
            <Space>
              <Tag icon={<SafetyCertificateOutlined />} color="green">安全支付</Tag>
              <Tag color="blue">品质保障</Tag>
            </Space>
          </div>
        </Space>
      </motion.div>
    </div>
  )
}
