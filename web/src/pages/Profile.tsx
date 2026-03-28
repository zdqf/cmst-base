import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import styles from './Profile.module.css'

export default function Profile() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>用户中心</h1>

      <div className={styles.userCard}>
        <div className={styles.avatar}>我</div>
        <div className={styles.userInfo}>
          <span className={styles.statusText}>已登录</span>
          <span className={styles.statusHint}>欢迎使用草木沈塘</span>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>快捷入口</h2>
        <div className={styles.links}>
          <Link to="/orders" className={styles.linkItem}>
            我的订单
            <span className={styles.arrow}>›</span>
          </Link>
          <Link to="/diagnosis/history" className={styles.linkItem}>
            问诊历史
            <span className={styles.arrow}>›</span>
          </Link>
          <Link to="/cart" className={styles.linkItem}>
            购物车
            <span className={styles.arrow}>›</span>
          </Link>
        </div>
      </div>

      <button className={styles.logoutBtn} onClick={handleLogout}>
        退出登录
      </button>
    </div>
  )
}
