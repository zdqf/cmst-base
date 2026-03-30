import { useState, useEffect, useCallback } from 'react'
import { Card, Typography, Tag, Empty, Spin, Pagination, Space, Timeline, Divider } from 'antd'
import { ShoppingOutlined, ClockCircleOutlined, CheckCircleOutlined, CarOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getOrderList } from '../api/orders'
import { mockOrders } from '../mock/data'
import { formatPrice } from '../utils/format'
import type { Order } from '../types'

const { Title, Text } = Typography

const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  pending: { color: 'orange', icon: <ClockCircleOutlined />, label: '待处理' },
  confirmed: { color: 'blue', icon: <CheckCircleOutlined />, label: '已确认' },
  shipped: { color: 'cyan', icon: <CarOutlined />, label: '已发货' },
  completed: { color: 'green', icon: <CheckCircleOutlined />, label: '已完成' },
  cancelled: { color: 'default', icon: <CloseCircleOutlined />, label: '已取消' },
}

export default function OrderList() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize] = useState(20)

  const fetchData = useCallback(async (p: number) => {
    setLoading(true)
    try {
      const res = await getOrderList(p)
      setOrders(res.items)
      setTotal(res.total)
    } catch {
      setOrders(mockOrders)
      setTotal(mockOrders.length)
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
          background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24,
        }}>
          <ShoppingOutlined style={{ fontSize: 36, color: '#1565c0', marginBottom: 8 }} />
          <Title level={2} style={{ margin: 0, color: '#1565c0' }}>我的订单</Title>
          <Text type="secondary">查看和管理您的所有订单</Text>
        </div>

        {orders.length === 0 ? (
          <Empty description="暂无订单" style={{ padding: 80 }} />
        ) : (
          <>
            {orders.map((order, i) => {
              const status = statusConfig[order.status] || statusConfig.pending
              return (
                <motion.div key={order.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                  <Card style={{ borderRadius: 12, border: 'none', marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <Space>
                        <Text type="secondary" style={{ fontSize: 12 }}>订单号：{order.order_no}</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}><ClockCircleOutlined /> {formatTime(order.created_at)}</Text>
                      </Space>
                      <Tag icon={status.icon} color={status.color}>{status.label}</Tag>
                    </div>

                    {order.items.map((item, idx) => (
                      <div key={idx} style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '8px 0', borderBottom: idx < order.items.length - 1 ? '1px solid #f5f5f5' : 'none',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{
                            width: 36, height: 36, borderRadius: 8, background: '#f5f5f5',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
                          }}>🏷️</div>
                          <Text>{item.product_name}</Text>
                        </div>
                        <Text type="secondary">×{item.quantity}　¥{formatPrice(item.unit_price)}</Text>
                      </div>
                    ))}

                    <Divider style={{ margin: '12px 0' }} />
                    <div style={{ textAlign: 'right' }}>
                      <Text type="secondary">合计：</Text>
                      <Text style={{ color: '#e53e3e', fontSize: 18, fontWeight: 700 }}>¥{formatPrice(order.total_amount)}</Text>
                    </div>
                  </Card>
                </motion.div>
              )
            })}

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Pagination current={page} total={total} pageSize={pageSize} onChange={setPage} showSizeChanger={false} />
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
