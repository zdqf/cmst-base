import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getProductDetail } from '../api/products'
import { useCart } from '../contexts/CartContext'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import type { Product } from '../types'
import styles from './ProductDetail.module.css'

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const { addItem } = useCart()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [showToast, setShowToast] = useState(false)

  const fetchProduct = async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const data = await getProductDetail(id)
      setProduct(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载商品详情失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchProduct() }, [id])

  const handleAddToCart = async () => {
    if (!product || adding) return
    setAdding(true)
    try {
      await addItem(product.id, 1)
      setShowToast(true)
      setTimeout(() => setShowToast(false), 2000)
    } catch {
      setError('加入购物车失败，请重试')
    } finally {
      setAdding(false)
    }
  }

  if (loading) return <div className={styles.page}><Loading /></div>
  if (error) return <div className={styles.page}><ErrorMessage message={error} onRetry={fetchProduct} /></div>
  if (!product) return null

  return (
    <div className={styles.page}>
      {product.image_url && (
        <img className={styles.image} src={product.image_url} alt={product.name} />
      )}
      <h1 className={styles.name}>{product.name}</h1>
      <p className={styles.price}>¥{product.price.toFixed(2)}</p>

      {product.stock > 0 ? (
        <p className={styles.stockIn}>有货 · 库存 {product.stock}</p>
      ) : (
        <p className={styles.stockOut}>暂时缺货</p>
      )}

      {product.specification && (
        <div className={styles.section}>
          <p className={styles.label}>规格</p>
          <p className={styles.value}>{product.specification}</p>
        </div>
      )}

      {product.description && (
        <div className={styles.section}>
          <p className={styles.label}>商品描述</p>
          <p className={styles.value}>{product.description}</p>
        </div>
      )}

      {product.stock > 0 ? (
        <button className={styles.addBtn} onClick={handleAddToCart} disabled={adding}>
          {adding ? '添加中...' : '加入购物车'}
        </button>
      ) : (
        <button className={styles.addBtn} disabled>暂时缺货</button>
      )}

      {showToast && <div className={styles.toast}>已加入购物车</div>}
    </div>
  )
}
