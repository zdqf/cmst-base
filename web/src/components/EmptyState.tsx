import { Link } from 'react-router-dom'
import { Empty, Button } from 'antd'

interface EmptyStateProps {
  message: string
  actionText?: string
  actionLink?: string
}

export default function EmptyState({ message, actionText, actionLink }: EmptyStateProps) {
  return (
    <Empty description={message} style={{ padding: 48 }}>
      {actionText && actionLink && (
        <Link to={actionLink}>
          <Button type="primary">{actionText}</Button>
        </Link>
      )}
    </Empty>
  )
}
