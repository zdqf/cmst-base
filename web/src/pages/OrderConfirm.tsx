import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../contexts/CartContext'
import { createOrder } from '../api/orders'
import styles from './OrderConfirm.module.css'

export default function OrderConfirm() {
  const { items, totalPrice, clearCart } = useCart()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (items.length === 0) {
      navigate('/cart', { replace: true })
    }
  }, [items, navigate])

  if (items.length === 0) return null

  const handleSubmit = async () => {
    setSubmitting(true)
    setError(null)
    try {
      await createOrder({
        items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
      })
      clearCart()
      navigate('/orders')
    } catch (err) {
      const msg = err instanceof Error ? err.message : '提交订单失败，请重试'
      if (/库存/.test(msg) || /stock/i.test(msg) || /insufficient/i.test(msg)) {
        setError(msg)
      } else {
        setError(msg)
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>订单确认</h1>

      <div className={styles.list}>
        {items.map((item) => (
          <div key={item.id} className={styles.item}>
            <div className={styles.itemInfo}>
              <span className={styles.itemName}>{item.product_name}</span>
              <span className={styles.itemMeta}>
                ¥{item.product_price.toFixed(2)} × {item.quantity}
              </span>
            </div>
            <span className={styles.itemSubtotal}>
              ¥{(item.product_price * item.quantity).toFixed(2)}
            </span>
          </div>
        ))}
      </div>

      <div className={styles.totalRow}>
        <span>应付总额</span>
        <span className={styles.totalPrice}>¥{totalPrice.toFixed(2)}</span>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <button
        className={styles.submitBtn}
        disabled={submitting}
        onClick={handleSubmit}
      >
        {submitting ? '提交中...' : '提交订单'}
      </button>
    </div>
  )
}
