import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import AdminLayout from '@/components/AdminLayout';
import AuthGuard from '@/components/AuthGuard';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Users from '@/pages/Users';
import Herbs from '@/pages/Herbs';
import Products from '@/pages/Products';
import Orders from '@/pages/Orders';
import Consultations from '@/pages/Consultations';
import DiagnosisLogs from '@/pages/DiagnosisLogs';
import Prompts from '@/pages/Prompts';
import Compliance from '@/pages/Compliance';

const App: React.FC = () => (
  <ConfigProvider locale={zhCN} theme={{ token: { colorPrimary: '#4e6b45', borderRadius: 6 } }}>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<AuthGuard><AdminLayout /></AuthGuard>}>
          <Route index element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="herbs" element={<Herbs />} />
          <Route path="products" element={<Products />} />
          <Route path="orders" element={<Orders />} />
          <Route path="consultations" element={<Consultations />} />
          <Route path="diagnosis-logs" element={<DiagnosisLogs />} />
          <Route path="prompts" element={<Prompts />} />
          <Route path="compliance" element={<Compliance />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </ConfigProvider>
);

export default App;
