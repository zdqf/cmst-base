import { useState, useEffect, useCallback } from 'react'
import { getOrderList } from '../api/orders'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import type { Order } from '../types'
import styles from './OrderList.module.css'

const statusMap: Record<string, string> = {
  pending: '待处理',
  confirmed: '已确认',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消',
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('zh-CN')
}

function formatPrice(amount: number) {
  return `¥${amount.toFixed(2)}`
}

export default function OrderList() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize, setPageSize] = useState(20)

  const fetchData = useCallback(async (p: number) => {
    setLoading(true)
    try {
      const res = await getOrderList(p)
      setOrders(res.items)
      setTotal(res.total)
      setPageSize(res.page_size)
    } catch {
      // empty list shown on error
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData(page)
  }, [page, fetchData])

  if (loading) return <Loading />

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>我的订单</h1>

      {orders.length === 0 ? (
        <EmptyState message="暂无订单" />
      ) : (
        <>
          <div className={styles.list}>
            {orders.map(order => (
              <div key={order.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <span className={styles.orderNo}>订单号：{order.order_no}</span>
                  <span className={styles.status}>{statusMap[order.status] || order.status}</span>
                </div>

                <div className={styles.items}>
                  {order.items.map((item, idx) => (
                    <div key={idx} className={styles.item}>
                      <span className={styles.itemName}>{item.product_name}</span>
                      <span className={styles.itemInfo}>
                        ×{item.quantity}　{formatPrice(item.unit_price)}
                      </span>
                    </div>
                  ))}
                </div>

                <div className={styles.cardFooter}>
                  <span className={styles.time}>{formatTime(order.created_at)}</span>
                  <span className={styles.total}>合计：{formatPrice(order.total_amount)}</span>
                </div>
              </div>
            ))}
          </div>

          <Pagination
            current={page}
            total={total}
            pageSize={pageSize}
            onChange={setPage}
          />
        </>
      )}
    </div>
  )
}
