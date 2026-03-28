import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getHerbList } from '../api/herbs'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import type { HerbListItem } from '../types'
import styles from './HerbList.module.css'

const PAGE_SIZE = 20

const CATEGORIES = [
  { label: '全部', value: '' },
  { label: '补益药', value: '补益药' },
  { label: '清热药', value: '清热药' },
  { label: '解表药', value: '解表药' },
  { label: '理气药', value: '理气药' },
  { label: '活血药', value: '活血药' },
]

export default function HerbList() {
  const navigate = useNavigate()
  const [items, setItems] = useState<HerbListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [keyword, setKeyword] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, unknown> = { page, page_size: PAGE_SIZE }
      if (category) params.category = category
      if (keyword) params.keyword = keyword
      const data = await getHerbList(params as Parameters<typeof getHerbList>[0])
      setItems(data.items)
      setTotal(data.total)
    } catch {
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [page, category, keyword])

  useEffect(() => { fetchData() }, [fetchData])

  const handleSearch = () => {
    setKeyword(searchInput.trim())
    setPage(1)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  const handleCategoryChange = (value: string) => {
    setCategory(value)
    setPage(1)
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>中药科普</h1>

      {/* Search */}
      <div className={styles.searchBar}>
        <input
          className={styles.searchInput}
          type="text"
          placeholder="搜索中药名称..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>

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
        <EmptyState message="暂无中药数据" />
      ) : (
        <>
          <div className={styles.grid}>
            {items.map((herb) => (
              <div
                key={herb.id}
                className={styles.card}
                onClick={() => navigate(`/herbs/${herb.id}`)}
              >
                <div className={styles.cardIcon}>🌿</div>
                <div className={styles.cardInfo}>
                  <p className={styles.cardName}>{herb.name}</p>
                  <p className={styles.cardCategory}>{herb.category || '中药'}</p>
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
