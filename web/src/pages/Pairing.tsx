import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHerbList } from '../api/herbs'
import { submitPairing } from '../api/ai'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import Disclaimer from '../components/Disclaimer'
import type { HerbListItem, PairingResult } from '../types'
import styles from './Pairing.module.css'

export default function Pairing() {
  const [herbs, setHerbs] = useState<HerbListItem[]>([])
  const [herbsLoading, setHerbsLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PairingResult | null>(null)

  useEffect(() => {
    const fetchHerbs = async () => {
      try {
        const data = await getHerbList({ page: 1, page_size: 100 })
        setHerbs(data.items)
      } catch {
        setHerbs([])
      } finally {
        setHerbsLoading(false)
      }
    }
    fetchHerbs()
  }, [])

  const toggleHerb = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleSubmit = async () => {
    if (selectedIds.size === 0) return
    setLoading(true)
    setError(null)
    try {
      const data = await submitPairing(Array.from(selectedIds))
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取搭配建议失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setSelectedIds(new Set())
    setError(null)
  }

  if (herbsLoading) return <Loading />

  // Result mode
  if (result) {
    return (
      <div className={styles.page}>
        <h1 className={styles.title}>搭配建议结果</h1>
        <Disclaimer type="full" />

        <div className={styles.suggestion}>
          <h2 className={styles.sectionTitle}>搭配思路</h2>
          <p className={styles.suggestionText}>{result.suggestion}</p>
        </div>

        <div className={styles.herbResults}>
          <h2 className={styles.sectionTitle}>中药详情</h2>
          {result.herbs.map((herb) => (
            <div key={herb.id} className={styles.herbCard}>
              <div className={styles.herbHeader}>
                <span className={styles.herbIcon}>🌿</span>
                <Link to={`/herbs/${herb.id}`} className={styles.herbLink}>
                  {herb.name}
                </Link>
              </div>
              <div className={styles.herbInfo}>
                <p><span className={styles.infoLabel}>不适合人群：</span>{herb.unsuitable_groups}</p>
                <p><span className={styles.infoLabel}>注意事项：</span>{herb.precautions}</p>
              </div>
            </div>
          ))}
        </div>

        <button className={styles.resetBtn} onClick={handleReset}>
          重新选择
        </button>
      </div>
    )
  }

  // Selection mode
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>中药搭配建议</h1>
      <p className={styles.subtitle}>选择一味或多味中药，获取 AI 搭配思路建议</p>

      {error && (
        <ErrorMessage message={error} onRetry={handleSubmit} />
      )}

      <div className={styles.chips}>
        {herbs.map((herb) => (
          <button
            key={herb.id}
            className={selectedIds.has(herb.id) ? styles.chipActive : styles.chip}
            onClick={() => toggleHerb(herb.id)}
          >
            {herb.name}
          </button>
        ))}
      </div>

      {herbs.length === 0 && (
        <p className={styles.emptyHint}>暂无可选中药</p>
      )}

      <div className={styles.selectedCount}>
        已选择 {selectedIds.size} 味中药
      </div>

      <button
        className={styles.submitBtn}
        disabled={loading || selectedIds.size === 0}
        onClick={handleSubmit}
      >
        {loading ? '分析中...' : '获取搭配建议'}
      </button>
    </div>
  )
}
