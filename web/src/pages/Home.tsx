import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDailyHerb } from '../api/herbs'
import Loading from '../components/Loading'
import type { HerbDetail } from '../types'
import styles from './Home.module.css'

const quickEntries = [
  { label: '中药科普', path: '/herbs', icon: '🌿' },
  { label: 'AI 问诊', path: '/diagnosis', icon: '🩺' },
  { label: '在线咨询', path: '/consultation', icon: '💬' },
  { label: '药材商城', path: '/products', icon: '🏪' },
]

export default function Home() {
  const navigate = useNavigate()
  const [dailyHerb, setDailyHerb] = useState<HerbDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    getDailyHerb()
      .then(setDailyHerb)
      .catch(() => setFailed(true))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className={styles.page}>
      {/* Brand introduction */}
      <section className={styles.brand}>
        <h1 className={styles.brandName}>草木沈塘</h1>
        <p className={styles.tagline}>传承本草智慧，守护自然健康</p>
        <p className={styles.description}>
          专注传统中药知识科普与优质药材甄选，为您提供专业的中药调理方向参考与品质药材服务。
        </p>
      </section>

      {/* Daily herb recommendation */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>今日草本推荐</h2>
        {loading ? (
          <Loading />
        ) : failed || !dailyHerb ? (
          <div className={styles.fallback}>暂无推荐</div>
        ) : (
          <div
            className={styles.herbCard}
            onClick={() => navigate(`/herbs/${dailyHerb.id}`)}
          >
            <div className={styles.herbIcon}>🌱</div>
            <div className={styles.herbInfo}>
              <p className={styles.herbName}>{dailyHerb.name}</p>
              <p className={styles.herbCategory}>
                {dailyHerb.category || '中药'}
              </p>
            </div>
            <span className={styles.herbArrow}>›</span>
          </div>
        )}
      </section>

      {/* Quick entries */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>快捷入口</h2>
        <div className={styles.entries}>
          {quickEntries.map((entry) => (
            <div
              key={entry.path}
              className={styles.entry}
              onClick={() => navigate(entry.path)}
            >
              <div className={styles.entryIcon}>{entry.icon}</div>
              <span className={styles.entryLabel}>{entry.label}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
