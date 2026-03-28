import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProductList } from '../api/products'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import type { Product } from '../types'
import styles from './ProductList.module.css'

const PAGE_SIZE = 20

const CATEGORIES = [
  { label: '全部', value: '' },
  { label: '原药材', value: '原药材' },
  { label: '简加工产品', value: '简加工产品' },
  { label: '调理组合包', value: '调理组合包' },
]

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
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [page, category])

  useEffect(() => { fetchData() }, [fetchData])

  const handleCategoryChange = (value: string) => {
    setCategory(value)
    setPage(1)
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>药材商城</h1>

      {/* Category filter */}
      <div className={styles.categories}>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            className={category === cat.value ? styles.categoryBtnActive : styles.categoryBtn}
            onClick={() => handleCategoryChange(cat.value)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <Loading />
      ) : items.length === 0 ? (
        <EmptyState message="暂无商品数据" />
      ) : (
        <>
          <div className={styles.grid}>
            {items.map((product) => (
              <div
                key={product.id}
                className={styles.card}
                onClick={() => navigate(`/products/${product.id}`)}
              >
                <div className={styles.cardIcon}>🏷️</div>
                <div className={styles.cardInfo}>
                  <p className={styles.cardName}>{product.name}</p>
                  <p className={styles.cardCategory}>{product.category || '商品'}</p>
                  <p className={styles.cardPrice}>¥{product.price.toFixed(2)}</p>
                </div>
                <span className={styles.cardArrow}>›</span>
              </div>
            ))}
          </div>
          <Pagination
            current={page}
            total={total}
            pageSize={PAGE_SIZE}
            onChange={setPage}
          />
        </>
      )}
    </div>
  )
}
