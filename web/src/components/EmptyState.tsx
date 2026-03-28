import { Link } from 'react-router-dom'
import styles from './EmptyState.module.css'

interface EmptyStateProps {
  message: string
  actionText?: string
  actionLink?: string
}

export default function EmptyState({ message, actionText, actionLink }: EmptyStateProps) {
  return (
    <div className={styles.container}>
      <p className={styles.message}>{message}</p>
      {actionText && actionLink && (
        <Link to={actionLink} className={styles.action}>
          {actionText}
        </Link>
      )}
    </div>
  )
}
