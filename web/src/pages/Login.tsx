import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useForm, validatePhone } from '../hooks/useForm'
import styles from './Login.module.css'

interface LoginForm {
  phone: string
  code: string
}

const phoneRules = {
  phone: (value: string) => {
    if (!value || !value.trim()) return '请输入手机号'
    if (!validatePhone(value)) return '手机号须为 11 位数字'
    return undefined
  },
  code: (value: string) => {
    if (!value || !value.trim()) return '请输入验证码'
    return undefined
  },
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { values, errors, touched, handleChange, handleBlur, validate } =
    useForm<LoginForm>({ phone: '', code: '' }, phoneRules)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setError(null)
    try {
      await login(values.phone, values.code)
      const from = (location.state as { from?: string })?.from || '/'
      navigate(from, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>
          <div className={styles.brandName}>草木沈塘</div>
          <div className={styles.brandSub}>传统中药知识科普与调理参考</div>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.field}>
            <label className={styles.label}>手机号</label>
            <input
              className={`${styles.input} ${touched.phone && errors.phone ? styles.inputError : ''}`}
              type="tel"
              placeholder="请输入 11 位手机号"
              maxLength={11}
              value={values.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              onBlur={() => handleBlur('phone')}
            />
            {touched.phone && errors.phone && (
              <div className={styles.fieldError}>{errors.phone}</div>
            )}
          </div>

          <div className={styles.field}>
            <label className={styles.label}>验证码</label>
            <input
              className={`${styles.input} ${touched.code && errors.code ? styles.inputError : ''}`}
              type="text"
              placeholder="请输入验证码"
              value={values.code}
              onChange={(e) => handleChange('code', e.target.value)}
              onBlur={() => handleBlur('code')}
            />
            {touched.code && errors.code && (
              <div className={styles.fieldError}>{errors.code}</div>
            )}
          </div>

          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading}
          >
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        <div className={styles.footer}>
          还没有账号？<Link to="/register">立即注册</Link>
        </div>
      </div>
    </div>
  )
}
