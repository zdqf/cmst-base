import { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react'
import * as authApi from '../api/auth'

// ===== State & Actions =====

interface AuthState {
  token: string | null
  isLoggedIn: boolean
}

type AuthAction =
  | { type: 'SET_TOKEN'; token: string }
  | { type: 'LOGOUT' }

interface AuthContextValue {
  state: AuthState
  login: (phone: string, code: string) => Promise<void>
  register: (phone: string, code: string) => Promise<void>
  logout: () => void
}

// ===== Reducer =====

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_TOKEN':
      return { token: action.token, isLoggedIn: true }
    case 'LOGOUT':
      return { token: null, isLoggedIn: false }
    default:
      return state
  }
}

// ===== Context =====

const AuthContext = createContext<AuthContextValue | null>(null)

function getInitialState(): AuthState {
  const token = localStorage.getItem('token')
  return {
    token,
    isLoggedIn: !!token,
  }
}

// ===== Provider =====

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, undefined, getInitialState)

  // Sync with localStorage on mount (handles external changes)
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token && !state.isLoggedIn) {
      dispatch({ type: 'SET_TOKEN', token })
    } else if (!token && state.isLoggedIn) {
      dispatch({ type: 'LOGOUT' })
    }
  }, [])

  const login = async (phone: string, code: string) => {
    const res = await authApi.login(phone, code)
    localStorage.setItem('token', res.access_token)
    dispatch({ type: 'SET_TOKEN', token: res.access_token })
  }

  const register = async (phone: string, code: string) => {
    const res = await authApi.register(phone, code)
    localStorage.setItem('token', res.access_token)
    dispatch({ type: 'SET_TOKEN', token: res.access_token })
  }

  const logout = () => {
    localStorage.removeItem('token')
    dispatch({ type: 'LOGOUT' })
  }

  return (
    <AuthContext.Provider value={{ state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// ===== Hook =====

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
