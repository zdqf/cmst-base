import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Typography, Space, Button } from 'antd';
import {
  UserOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  MessageOutlined,
  MedicineBoxOutlined,
  HistoryOutlined,
  ArrowUpOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getUsers } from '@/api/users';
import { getOrders } from '@/api/orders';
import { getConsultations } from '@/api/consultations';
import { getDiagnosisLogs } from '@/api/diagnosisLogs';
import { getProducts } from '@/api/products';
import { getHerbs } from '@/api/herbs';
import type { AdminOrderItem, AdminConsultationItem } from '@/types';

const { Title, Text } = Typography;

const ORDER_STATUS_MAP: Record<string, { color: string; label: string }> = {
  pending: { color: 'orange', label: '待处理' },
  paid: { color: 'blue', label: '已支付' },
  shipped: { color: 'cyan', label: '已发货' },
  completed: { color: 'green', label: '已完成' },
  cancelled: { color: 'red', label: '已取消' },
};

const CONSULT_STATUS_MAP: Record<string, { color: string; label: string }> = {
  pending: { color: 'orange', label: '待处理' },
  processing: { color: 'blue', label: '处理中' },
  completed: { color: 'green', label: '已完成' },
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ users: 0, orders: 0, pendingOrders: 0, consultations: 0, pendingConsultations: 0, products: 0, herbs: 0, diagnosisLogs: 0 });
  const [recentOrders, setRecentOrders] = useState<AdminOrderItem[]>([]);
  const [recentConsultations, setRecentConsultations] = useState<AdminConsultationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [usersRes, ordersRes, pendingOrdersRes, consultsRes, pendingConsultsRes, productsRes, herbsRes, diagRes] = await Promise.all([
        getUsers({ page: 1, page_size: 1 }),
        getOrders({ page: 1, page_size: 5 }),
        getOrders({ page: 1, page_size: 1, status: 'pending' }),
        getConsultations({ page: 1, page_size: 5 }),
        getConsultations({ page: 1, page_size: 1, status: 'pending' }),
        getProducts({ page: 1, page_size: 1 }),
        getHerbs({ page: 1, page_size: 1 }),
        getDiagnosisLogs({ page: 1, page_size: 1 }),
      ]);

      setStats({
        users: usersRes.data.data?.total || 0,
        orders: ordersRes.data.data?.total || 0,
        pendingOrders: pendingOrdersRes.data.data?.total || 0,
        consultations: consultsRes.data.data?.total || 0,
        pendingConsultations: pendingConsultsRes.data.data?.total || 0,
        products: productsRes.data.data?.total || 0,
        herbs: herbsRes.data.data?.total || 0,
        diagnosisLogs: diagRes.data.data?.total || 0,
      });
      setRecentOrders(ordersRes.data.data?.items || []);
      setRecentConsultations(consultsRes.data.data?.items || []);
    } catch {
      // silently fail, stats show 0
    } finally {
      setLoading(false);
    }
  };

  const orderColumns = [
    { title: '订单号', dataIndex: 'order_no', key: 'order_no', width: 200 },
    { title: '金额', dataIndex: 'total_amount', key: 'total_amount', render: (v: number) => `¥${Number(v).toFixed(2)}` },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s: string) => <Tag color={ORDER_STATUS_MAP[s]?.color}>{ORDER_STATUS_MAP[s]?.label || s}</Tag> },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => new Date(v).toLocaleString('zh-CN') },
  ];

  const consultColumns = [
    { title: '姓名', dataIndex: 'name', key: 'name' },
    { title: '主题', dataIndex: 'subject', key: 'subject', ellipsis: true },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s: string) => <Tag color={CONSULT_STATUS_MAP[s]?.color}>{CONSULT_STATUS_MAP[s]?.label || s}</Tag> },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => new Date(v).toLocaleString('zh-CN') },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>仪表盘</Title>

      {/* 核心指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/users')}>
            <Statistic title="注册用户" value={stats.users} prefix={<UserOutlined style={{ color: '#1890ff' }} />} loading={loading} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/orders')}>
            <Statistic title="总订单" value={stats.orders} prefix={<ShoppingCartOutlined style={{ color: '#52c41a' }} />} loading={loading} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/products')}>
            <Statistic title="在售商品" value={stats.products} prefix={<DollarOutlined style={{ color: '#faad14' }} />} loading={loading} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/herbs')}>
            <Statistic title="中药词条" value={stats.herbs} prefix={<MedicineBoxOutlined style={{ color: '#722ed1' }} />} loading={loading} />
          </Card>
        </Col>
      </Row>

      {/* 待处理事项 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="待处理订单" value={stats.pendingOrders} prefix={<ClockCircleOutlined style={{ color: '#fa8c16' }} />} valueStyle={stats.pendingOrders > 0 ? { color: '#fa8c16' } : undefined} loading={loading} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="待回复咨询" value={stats.pendingConsultations} prefix={<MessageOutlined style={{ color: '#eb2f96' }} />} valueStyle={stats.pendingConsultations > 0 ? { color: '#eb2f96' } : undefined} loading={loading} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/consultations')}>
            <Statistic title="总咨询" value={stats.consultations} prefix={<MessageOutlined style={{ color: '#13c2c2' }} />} loading={loading} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card hoverable onClick={() => navigate('/diagnosis-logs')}>
            <Statistic title="AI 问诊次数" value={stats.diagnosisLogs} prefix={<HistoryOutlined style={{ color: '#2f54eb' }} />} loading={loading} />
          </Card>
        </Col>
      </Row>

      {/* 快捷入口 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="快捷操作" size="small">
            <Space wrap>
              <Button type="primary" onClick={() => navigate('/herbs')}>管理中药</Button>
              <Button type="primary" onClick={() => navigate('/products')}>管理商品</Button>
              <Button onClick={() => navigate('/orders')}>处理订单</Button>
              <Button onClick={() => navigate('/consultations')}>处理咨询</Button>
              <Button onClick={() => navigate('/prompts')}>Prompt 模板</Button>
              <Button onClick={() => navigate('/compliance')}>合规配置</Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 最近数据 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="最近订单" size="small" extra={<a onClick={() => navigate('/orders')}>查看全部</a>}>
            <Table columns={orderColumns} dataSource={recentOrders} rowKey="id" pagination={false} size="small" loading={loading} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="最近咨询" size="small" extra={<a onClick={() => navigate('/consultations')}>查看全部</a>}>
            <Table columns={consultColumns} dataSource={recentConsultations} rowKey="id" pagination={false} size="small" loading={loading} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
