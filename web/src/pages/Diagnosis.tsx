import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, diagnosisValidationRules } from '../hooks/useForm'
import { submitDiagnosis } from '../api/ai'
import ErrorMessage from '../components/ErrorMessage'
import type { DiagnosisRequest } from '../types'
import styles from './Diagnosis.module.css'

const initialValues: DiagnosisRequest = {
  age: '' as unknown as number,
  gender: '',
  symptoms: '',
  allergies: '',
  medications: '',
}

export default function Diagnosis() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { values, errors, touched, handleChange, handleBlur, validate } =
    useForm<DiagnosisRequest>(initialValues, diagnosisValidationRules)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setError(null)
    try {
      const result = await submitDiagnosis({
        ...values,
        age: Number(values.age),
      })
      navigate('/diagnosis/result', { state: { result } })
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>AI 问诊</h1>

      <form onSubmit={handleSubmit}>
        {error && (
          <div className={styles.errorWrap}>
            <ErrorMessage message={error} onRetry={handleSubmit as unknown as () => void} />
          </div>
        )}

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>年龄</label>
          <input
            className={`${styles.input} ${touched.age && errors.age ? styles.inputError : ''}`}
            type="number"
            placeholder="请输入年龄（1-150）"
            min={1}
            max={150}
            value={values.age}
            onChange={(e) => handleChange('age', e.target.value as unknown as number)}
            onBlur={() => handleBlur('age')}
          />
          {touched.age && errors.age && (
            <div className={styles.fieldError}>{errors.age}</div>
          )}
        </div>

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>性别</label>
          <select
            className={`${styles.select} ${touched.gender && errors.gender ? styles.inputError : ''}`}
            value={values.gender}
            onChange={(e) => handleChange('gender', e.target.value)}
            onBlur={() => handleBlur('gender')}
          >
            <option value="">请选择性别</option>
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
          {touched.gender && errors.gender && (
            <div className={styles.fieldError}>{errors.gender}</div>
          )}
        </div>

        <div className={styles.field}>
          <label className={`${styles.label} ${styles.required}`}>主要不适描述</label>
          <textarea
            className={`${styles.textarea} ${touched.symptoms && errors.symptoms ? styles.inputError : ''}`}
            placeholder="请描述您的主要不适症状"
            maxLength={500}
            value={values.symptoms}
            onChange={(e) => handleChange('symptoms', e.target.value)}
            onBlur={() => handleBlur('symptoms')}
          />
          <div className={styles.charCount}>{values.symptoms.length}/500</div>
          {touched.symptoms && errors.symptoms && (
            <div className={styles.fieldError}>{errors.symptoms}</div>
          )}
        </div>

        <div className={styles.field}>
          <label className={styles.label}>既往过敏史</label>
          <textarea
            className={styles.textarea}
            placeholder="如有过敏史请填写（选填）"
            value={values.allergies ?? ''}
            onChange={(e) => handleChange('allergies', e.target.value)}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>当前用药情况</label>
          <textarea
            className={styles.textarea}
            placeholder="如有正在服用的药物请填写（选填）"
            value={values.medications ?? ''}
            onChange={(e) => handleChange('medications', e.target.value)}
          />
        </div>

        <button
          type="submit"
          className={styles.submitBtn}
          disabled={loading}
        >
          {loading ? '提交中...' : '提交问诊'}
        </button>
      </form>
    </div>
  )
}
