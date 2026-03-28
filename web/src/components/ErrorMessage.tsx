import { Alert, Button } from 'antd'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <Alert
      type="error"
      message={message}
      showIcon
      style={{ borderRadius: 8 }}
      action={onRetry ? <Button size="small" onClick={onRetry}>重试</Button> : undefined}
    />
  )
}
