import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Spin } from 'antd'
import { AuthProvider } from './contexts/AuthContext'
import { CartProvider } from './contexts/CartContext'
import Layout from './components/Layout'
import AuthGuard from './components/AuthGuard'

// Lazy load all pages for better code splitting
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Home = lazy(() => import('./pages/Home'))
const HerbList = lazy(() => import('./pages/HerbList'))
const HerbDetail = lazy(() => import('./pages/HerbDetail'))
const Diagnosis = lazy(() => import('./pages/Diagnosis'))
const DiagnosisResult = lazy(() => import('./pages/DiagnosisResult'))
const DiagnosisHistory = lazy(() => import('./pages/DiagnosisHistory'))
const Pairing = lazy(() => import('./pages/Pairing'))
const Consultation = lazy(() => import('./pages/Consultation'))
const ConsultationSuccess = lazy(() => import('./pages/ConsultationSuccess'))
const ProductList = lazy(() => import('./pages/ProductList'))
const ProductDetail = lazy(() => import('./pages/ProductDetail'))
const Cart = lazy(() => import('./pages/Cart'))
const OrderConfirm = lazy(() => import('./pages/OrderConfirm'))
const OrderList = lazy(() => import('./pages/OrderList'))
const Profile = lazy(() => import('./pages/Profile'))
const Membership = lazy(() => import('./pages/Membership'))
const About = lazy(() => import('./pages/About'))

const PageLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
    <Spin size="large" />
  </div>
)

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public routes without layout */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Layout-wrapped routes */}
            <Route element={<Layout />}>
              {/* Public pages */}
              <Route path="/" element={<Home />} />
              <Route path="/herbs" element={<HerbList />} />
              <Route path="/herbs/:id" element={<HerbDetail />} />
              <Route path="/products" element={<ProductList />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/membership" element={<Membership />} />
              <Route path="/about" element={<About />} />

              {/* Auth-required pages */}
              <Route element={<AuthGuard />}>
                <Route path="/diagnosis" element={<Diagnosis />} />
                <Route path="/diagnosis/result" element={<DiagnosisResult />} />
                <Route path="/diagnosis/history" element={<DiagnosisHistory />} />
                <Route path="/pairing" element={<Pairing />} />
                <Route path="/consultation" element={<Consultation />} />
                <Route path="/consultation/success" element={<ConsultationSuccess />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/order/confirm" element={<OrderConfirm />} />
                <Route path="/orders" element={<OrderList />} />
                <Route path="/profile" element={<Profile />} />
              </Route>
            </Route>
          </Routes>
        </Suspense>
      </CartProvider>
    </AuthProvider>
  )
}
