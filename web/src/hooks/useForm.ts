import { useState, useCallback } from 'react'
import type { DiagnosisRequest, ConsultationRequest } from '../types'

// --- Types ---

type ValidationRule<T> = {
  [K in keyof T]?: (value: T[K], values: T) => string | undefined
}

interface UseFormReturn<T> {
  values: T
  errors: Partial<Record<keyof T, string>>
  touched: Partial<Record<keyof T, boolean>>
  handleChange: (field: keyof T, value: T[keyof T]) => void
  handleBlur: (field: keyof T) => void
  validate: () => boolean
  resetForm: () => void
}

// --- Phone validation ---

export function validatePhone(phone: string): boolean {
  return /^\d{11}$/.test(phone)
}

// --- Diagnosis form validation rules ---

export const diagnosisValidationRules: ValidationRule<DiagnosisRequest> = {
  age: (value) => {
    if (value === undefined || value === null || value === ('' as unknown as number)) {
      return '请输入年龄'
    }
    const num = Number(value)
    if (!Number.isInteger(num) || num < 1 || num > 150) {
      return '年龄须为 1-150 的正整数'
    }
    return undefined
  },
  gender: (value) => {
    if (!value || !value.trim()) return '请选择性别'
    return undefined
  },
  symptoms: (value) => {
    if (!value || !value.trim()) return '请填写主要不适描述'
    if (value.length > 500) return '主要不适描述不超过 500 字'
    return undefined
  },
}

// --- Consultation form validation rules ---

export const consultationValidationRules: ValidationRule<ConsultationRequest> = {
  name: (value) => {
    if (!value || !value.trim()) return '请填写姓名'
    if (value.length > 50) return '姓名不超过 50 字'
    return undefined
  },
  contact: (value) => {
    if (!value || !value.trim()) return '请填写联系方式'
    if (value.length > 50) return '联系方式不超过 50 字'
    return undefined
  },
  subject: (value) => {
    if (!value || !value.trim()) return '请填写咨询主题'
    if (value.length > 100) return '咨询主题不超过 100 字'
    return undefined
  },
  description: (value) => {
    if (!value || !value.trim()) return '请填写详细描述'
    if (value.length > 1000) return '详细描述不超过 1000 字'
    return undefined
  },
}

// --- Generic useForm hook ---

export function useForm<T extends Record<string, any>>(
  initialValues: T,
  rules?: ValidationRule<T>
): UseFormReturn<T> {
  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({})

  const handleChange = useCallback((field: keyof T, value: T[keyof T]) => {
    setValues((prev) => ({ ...prev, [field]: value }))
    // Clear error on change
    setErrors((prev) => {
      if (!prev[field]) return prev
      const next = { ...prev }
      delete next[field]
      return next
    })
  }, [])

  const handleBlur = useCallback(
    (field: keyof T) => {
      setTouched((prev) => ({ ...prev, [field]: true }))
      // Validate single field on blur
      if (rules && rules[field]) {
        const error = rules[field]!(values[field] as T[keyof T], values)
        setErrors((prev) => {
          if (error) return { ...prev, [field]: error }
          const next = { ...prev }
          delete next[field]
          return next
        })
      }
    },
    [rules, values]
  )

  const validate = useCallback((): boolean => {
    if (!rules) return true
    const newErrors: Partial<Record<keyof T, string>> = {}
    const allTouched: Partial<Record<keyof T, boolean>> = {}
    let valid = true

    for (const key of Object.keys(rules) as Array<keyof T>) {
      allTouched[key] = true
      const rule = rules[key]
      if (rule) {
        const error = rule(values[key] as T[keyof T], values)
        if (error) {
          newErrors[key] = error
          valid = false
        }
      }
    }

    setTouched((prev) => ({ ...prev, ...allTouched }))
    setErrors(newErrors)
    return valid
  }, [rules, values])

  const resetForm = useCallback(() => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
  }, [initialValues])

  return { values, errors, touched, handleChange, handleBlur, validate, resetForm }
}
