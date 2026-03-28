import styles from './Pagination.module.css'

interface PaginationProps {
  current: number
  total: number
  pageSize: number
  onChange: (page: number) => void
}

export default function Pagination({ current, total, pageSize, onChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className={styles.container}>
      <button
        className={styles.button}
        disabled={current <= 1}
        onClick={() => onChange(current - 1)}
      >
        上一页
      </button>
      <span className={styles.indicator}>
        {current} / {totalPages}
      </span>
      <button
        className={styles.button}
        disabled={current >= totalPages}
        onClick={() => onChange(current + 1)}
      >
        下一页
      </button>
    </div>
  )
}
