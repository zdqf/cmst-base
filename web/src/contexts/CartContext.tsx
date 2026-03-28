import { createContext, useContext, useReducer, useCallback, type ReactNode } from 'react'
import * as cartApi from '../api/cart'
import type { CartItem } from '../types'

// ===== State & Actions =====

interface CartState {
  items: CartItem[]
  totalCount: number
  totalPrice: number
}

type CartAction =
  | { type: 'SET_ITEMS'; items: CartItem[] }
  | { type: 'CLEAR' }

interface CartContextValue {
  items: CartItem[]
  totalCount: number
  totalPrice: number
  fetchCart: () => Promise<void>
  addItem: (productId: string, quantity: number) => Promise<void>
  updateQuantity: (cartItemId: string, quantity: number) => Promise<void>
  removeItem: (cartItemId: string) => Promise<void>
  clearCart: () => void
}

// ===== Helpers =====

function calcTotals(items: CartItem[]): { totalCount: number; totalPrice: number } {
  let totalCount = 0
  let totalPrice = 0
  for (const item of items) {
    totalCount += item.quantity
    totalPrice += item.product_price * item.quantity
  }
  return { totalCount, totalPrice }
}

// ===== Reducer =====

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'SET_ITEMS': {
      const { totalCount, totalPrice } = calcTotals(action.items)
      return { items: action.items, totalCount, totalPrice }
    }
    case 'CLEAR':
      return { items: [], totalCount: 0, totalPrice: 0 }
    default:
      return state
  }
}

// ===== Context =====

const CartContext = createContext<CartContextValue | null>(null)

const initialState: CartState = {
  items: [],
  totalCount: 0,
  totalPrice: 0,
}

// ===== Provider =====

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, initialState)

  const fetchCart = useCallback(async () => {
    const items = await cartApi.getCart()
    dispatch({ type: 'SET_ITEMS', items })
  }, [])

  const addItem = useCallback(async (productId: string, quantity: number) => {
    await cartApi.addToCart({ product_id: productId, quantity })
    await fetchCart()
  }, [fetchCart])

  const updateQuantity = useCallback(async (cartItemId: string, quantity: number) => {
    if (quantity < 1) return
    await cartApi.updateCartItem(cartItemId, quantity)
    await fetchCart()
  }, [fetchCart])

  const removeItem = useCallback(async (cartItemId: string) => {
    await cartApi.removeCartItem(cartItemId)
    await fetchCart()
  }, [fetchCart])

  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR' })
  }, [])

  return (
    <CartContext.Provider
      value={{
        items: state.items,
        totalCount: state.totalCount,
        totalPrice: state.totalPrice,
        fetchCart,
        addItem,
        updateQuantity,
        removeItem,
        clearCart,
      }}
    >
      {children}
    </CartContext.Provider>
  )
}

// ===== Hook =====

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext)
  if (!ctx) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return ctx
}
