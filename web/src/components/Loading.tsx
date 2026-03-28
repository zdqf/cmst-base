import styles from './Loading.module.css'

interface LoadingProps {
  fullscreen?: boolean
}

export default function Loading({ fullscreen = false }: LoadingProps) {
  return (
    <div className={fullscreen ? styles.fullscreen : styles.inline}>
      <div className={styles.spinner} />
    </div>
  )
}
