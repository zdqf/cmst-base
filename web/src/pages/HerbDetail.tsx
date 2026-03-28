import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getHerbDetail } from '../api/herbs'
import Loading from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import Disclaimer from '../components/Disclaimer'
import type { HerbDetail as HerbDetailType } from '../types'
import styles from './HerbDetail.module.css'

const FIELDS: { key: keyof HerbDetailType; label: string }[] = [
  { key: 'origin_and_form', label: '来源与形态' },
  { key: 'flavor_meridian', label: '性味归经' },
  { key: 'common_pairings', label: '常见搭配方向' },
  { key: 'unsuitable_groups', label: '不适合人群' },
  { key: 'precautions', label: '注意事项' },
]

export default function HerbDetail() {
  const { id } = useParams<{ id: string }>()
  const [herb, setHerb] = useState<HerbDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const data = await getHerbDetail(id)
      setHerb(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [id])

  if (loading) return <Loading />
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />
  if (!herb) return null

  return (
    <div className={styles.page}>
      <h1 className={styles.name}>{herb.name}</h1>
      {herb.category && <span className={styles.category}>{herb.category}</span>}

      <div className={styles.sections}>
        {FIELDS.map(({ key, label }) => (
          <section key={key} className={styles.section}>
            <h2 className={styles.label}>{label}</h2>
            <p className={styles.content}>{herb[key] as string || '暂无信息'}</p>
          </section>
        ))}
      </div>

      <div className={styles.disclaimer}>
        <Disclaimer type="short" />
      </div>
    </div>
  )
}
