import { Spin } from 'antd'

interface LoadingProps {
  fullscreen?: boolean
}

export default function Loading({ fullscreen = false }: LoadingProps) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: fullscreen ? 0 : 48,
      minHeight: fullscreen ? '100vh' : 'auto',
    }}>
      <Spin size="large" />
    </div>
  )
}
