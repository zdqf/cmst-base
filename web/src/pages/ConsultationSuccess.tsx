import { useLocation, useNavigate, Link } from 'react-router-dom'
import { useEffect } from 'react'
import type { ConsultationResponse } from '../types'
import styles from './ConsultationSuccess.module.css'

export default function ConsultationSuccess() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = (location.state as { result?: ConsultationResponse } | null)?.result

  useEffect(() => {
    if (!result) {
      navigate('/consultation', { replace: true })
    }
  }, [result, navigate])

  if (!result) return null

  return (
    <div className={styles.page}>
      <div className={styles.successIcon}>✅</div>
      <h1 className={styles.title}>咨询提交成功</h1>
      <p className={styles.subtitle}>我们已收到您的咨询，请通过以下方式联系我们</p>

      <div className={styles.contactCard}>
        <div className={styles.contactLabel}>微信 / 企业微信</div>
        <div className={styles.contactValue}>{result.wechat_id}</div>

        {result.qr_code_url && (
          <img
            className={styles.qrCode}
            src={result.qr_code_url}
            alt="微信二维码"
          />
        )}
      </div>

      <Link to="/" className={styles.homeLink}>返回首页</Link>
    </div>
  )
}
