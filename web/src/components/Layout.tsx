import { Outlet, Link, useLocation } from 'react-router-dom'
import styles from './Layout.module.css'

const navItems = [
  { label: '首页', path: '/', icon: '🏠' },
  { label: '中药科普', path: '/herbs', icon: '📚' },
  { label: '药材商城', path: '/products', icon: '🛒' },
  { label: '购物车', path: '/cart', icon: '🛍️' },
  { label: '我的', path: '/profile', icon: '👤' },
]

export default function Layout() {
  const location = useLocation()

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <div className={styles.layout}>
      {/* Desktop top navigation */}
      <nav className={styles.topNav}>
        <Link to="/" className={styles.brand}>草木沈塘</Link>
        <ul className={styles.navLinks}>
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`${styles.navLink} ${isActive(item.path) ? styles.navLinkActive : ''}`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Main content */}
      <main className={styles.content}>
        <Outlet />
      </main>

      {/* Mobile bottom tab bar */}
      <nav className={styles.bottomTab}>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`${styles.tabItem} ${isActive(item.path) ? styles.tabItemActive : ''}`}
          >
            <span className={styles.tabIcon}>{item.icon}</span>
            <span className={styles.tabLabel}>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  )
}
