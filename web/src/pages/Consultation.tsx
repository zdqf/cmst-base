import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, consultationValidationRules } from '../hooks/useForm'
import { submitConsultation } from '../api/consultation'
import ErrorMessage from '../components/ErrorMessage'
import type { ConsultationRequest } from '../types'
import styles from './Consultation.module.css'

const initialValues: ConsultationRequest = {
  name: '',
  contact: '',
  subject: '',
  description: '',
}

export default function Consultation() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { values, errors, touched, handleChange, handleBlur, validate } =
    useForm<ConsultationRequest>(initialValues, consultationValidationRules)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setError(null)
    try {
      const result = await submitConsultation(values)
      navigate('/consultation/success', { state: { result } })
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>在线咨询</h1>

      <form onSubmit={handleSubmit}>
        {error && (
          <div className={styles.errorWrap}>
            <ErrorMessage message={error} />
          </div>
        )}

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>姓名</label>
          <input
            className={`${styles.input} ${touched.name && errors.name ? styles.inputError : ''}`}
            type="text"
            placeholder="请输入姓名"
            maxLength={50}
            value={values.name}
            onChange={(e) => handleChange('name', e.target.value)}
            onBlur={() => handleBlur('name')}
          />
          {touched.name && errors.name && (
            <div className={styles.fieldError}>{errors.name}</div>
          )}
        </div>

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>联系方式</label>
          <input
            className={`${styles.input} ${touched.contact && errors.contact ? styles.inputError : ''}`}
            type="text"
            placeholder="请输入联系方式"
            maxLength={50}
            value={values.contact}
            onChange={(e) => handleChange('contact', e.target.value)}
            onBlur={() => handleBlur('contact')}
          />
          {touched.contact && errors.contact && (
            <div className={styles.fieldError}>{errors.contact}</div>
          )}
        </div>

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>咨询主题</label>
          <input
            className={`${styles.input} ${touched.subject && errors.subject ? styles.inputError : ''}`}
            type="text"
            placeholder="请输入咨询主题"
            maxLength={100}
            value={values.subject}
            onChange={(e) => handleChange('subject', e.target.value)}
            onBlur={() => handleBlur('subject')}
          />
          {touched.subject && errors.subject && (
            <div className={styles.fieldError}>{errors.subject}</div>
          )}
        </div>

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>详细描述</label>
          <textarea
            className={`${styles.textarea} ${touched.description && errors.description ? styles.inputError : ''}`}
            placeholder="请详细描述您的咨询内容"
            maxLength={1000}
            value={values.description}
            onChange={(e) => handleChange('description', e.target.value)}
            onBlur={() => handleBlur('description')}
          />
          <div className={styles.charCount}>{values.description.length}/1000</div>
          {touched.description && errors.description && (
            <div className={styles.fieldError}>{errors.description}</div>
          )}
        </div>

        <button
          type="submit"
          className={styles.submitBtn}
          disabled={loading}
        >
          {loading ? '提交中...' : '提交咨询'}
        </button>
      </form>
    </div>
  )
}
