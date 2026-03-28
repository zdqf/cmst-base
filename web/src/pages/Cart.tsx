import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../contexts/CartContext'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'
import styles from './Cart.module.css'

export default function Cart() {
  const { items, totalCount, totalPrice, fetchCart, updateQuantity, removeItem } = useCart()
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchCart().finally(() => setLoading(false))
  }, [fetchCart])

  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`确定要删除「${name}」吗？`)) {
      removeItem(id)
    }
  }

  if (loading) return <Loading />

  if (items.length === 0) {
    return (
      <div className={styles.page}>
        <h1 className={styles.title}>购物车</h1>
        <EmptyState message="购物车是空的" actionText="去逛逛" actionLink="/products" />
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>购物车</h1>

      {items.map((item) => (
        <div key={item.id} className={styles.item}>
          <div className={styles.itemInfo}>
            <p className={styles.itemName}>{item.product_name}</p>
            <p className={styles.itemPrice}>¥{item.product_price.toFixed(2)}</p>
            <p className={styles.itemSubtotal}>
              小计：¥{(item.product_price * item.quantity).toFixed(2)}
            </p>
            <div className={styles.quantityRow}>
              <button
                className={styles.qtyBtn}
                disabled={item.quantity <= 1}
                onClick={() => updateQuantity(item.id, item.quantity - 1)}
              >
                −
              </button>
              <span className={styles.qtyValue}>{item.quantity}</span>
              <button
                className={styles.qtyBtn}
                onClick={() => updateQuantity(item.id, item.quantity + 1)}
              >
                +
              </button>
            </div>
          </div>
          <button className={styles.deleteBtn} onClick={() => handleDelete(item.id, item.product_name)}>
            删除
          </button>
        </div>
      ))}

      <div className={styles.bottomBar}>
        <div className={styles.summary}>
          共 {totalCount} 件，合计{' '}
          <span className={styles.summaryPrice}>¥{totalPrice.toFixed(2)}</span>
        </div>
        <button className={styles.checkoutBtn} onClick={() => navigate('/order/confirm')}>
          去结算
        </button>
      </div>
    </div>
  )
}
