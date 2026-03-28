import { useState, useEffect, useCallback } from 'react'
import { getDiagnosisHistory } from '../api/ai'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import type { DiagnosisHistoryItem } from '../types'
import styles from './DiagnosisHistory.module.css'

export default function DiagnosisHistory() {
  const [items, setItems] = useState<DiagnosisHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize, setPageSize] = useState(20)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const fetchData = useCallback(async (p: number) => {
    setLoading(true)
    try {
      const res = await getDiagnosisHistory(p)
      setItems(res.items)
      setTotal(res.total)
      setPageSize(res.page_size)
    } catch {
      // error handled silently, empty list shown
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData(page)
  }, [page, fetchData])

  const handlePageChange = (p: number) => {
    setPage(p)
    setExpandedId(null)
  }

  const toggleExpand = (id: string) => {
    setExpandedId(prev => (prev === id ? null : id))
  }

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN')
  }

  if (loading) return <Loading />

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>问诊历史</h1>

      {items.length === 0 ? (
        <EmptyState message="暂无问诊记录" />
      ) : (
        <>
          <div className={styles.list}>
            {items.map(item => (
              <div key={item.id} className={styles.record}>
                <div className={styles.recordHeader} onClick={() => toggleExpand(item.id)}>
                  <div className={styles.recordSummary}>
                    <p className={styles.recordTime}>{formatTime(item.created_at)}</p>
                    <p className={styles.recordSymptoms}>{item.input_data.symptoms}</p>
                  </div>
                  <span className={expandedId === item.id ? styles.arrowExpanded : styles.arrow}>
                    ›
                  </span>
                </div>

                {expandedId === item.id && (
                  <div className={styles.recordDetail}>
                    <div className={styles.detailSection}>
                      <p className={styles.detailLabel}>基本信息</p>
                      <p className={styles.detailValue}>
                        年龄：{item.input_data.age}　性别：{item.input_data.gender}
                      </p>
                    </div>
                    <div className={styles.detailSection}>
                      <p className={styles.detailLabel}>主要不适</p>
                      <p className={styles.detailValue}>{item.input_data.symptoms}</p>
                    </div>
                    {item.input_data.allergies && (
                      <div className={styles.detailSection}>
                        <p className={styles.detailLabel}>过敏史</p>
                        <p className={styles.detailValue}>{item.input_data.allergies}</p>
                      </div>
                    )}
                    {item.input_data.medications && (
                      <div className={styles.detailSection}>
                        <p className={styles.detailLabel}>当前用药</p>
                        <p className={styles.detailValue}>{item.input_data.medications}</p>
                      </div>
                    )}
                    <div className={styles.detailSection}>
                      <p className={styles.detailLabel}>AI 建议</p>
                      <p className={styles.detailValue}>{item.ai_output}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <Pagination
            current={page}
            total={total}
            pageSize={pageSize}
            onChange={handlePageChange}
          />
        </>
      )}
    </div>
  )
}
