import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { CartProvider } from './contexts/CartContext'
import Layout from './components/Layout'
import AuthGuard from './components/AuthGuard'
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import HerbList from './pages/HerbList'
import HerbDetail from './pages/HerbDetail'
import Diagnosis from './pages/Diagnosis'
import DiagnosisResult from './pages/DiagnosisResult'
import DiagnosisHistory from './pages/DiagnosisHistory'
import Pairing from './pages/Pairing'
import Consultation from './pages/Consultation'
import ConsultationSuccess from './pages/ConsultationSuccess'
import ProductList from './pages/ProductList'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import OrderConfirm from './pages/OrderConfirm'
import OrderList from './pages/OrderList'
import Profile from './pages/Profile'
import Membership from './pages/Membership'
import About from './pages/About'

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
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
      </CartProvider>
    </AuthProvider>
  )
}
