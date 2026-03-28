import { useLocation, Navigate } from 'react-router-dom'
import Disclaimer from '../components/Disclaimer'
import type { DiagnosisResult as DiagnosisResultType } from '../types'
import styles from './DiagnosisResult.module.css'

export default function DiagnosisResult() {
  const location = useLocation()
  const result = (location.state as { result?: DiagnosisResultType } | null)?.result

  if (!result) {
    return <Navigate to="/diagnosis" replace />
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>问诊结果</h1>
      <Disclaimer type="full" />
      <div className={styles.content}>
        <pre className={styles.output}>{result.ai_output}</pre>
      </div>
    </div>
  )
}
