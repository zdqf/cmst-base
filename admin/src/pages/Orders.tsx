import React, { useEffect, useState } from 'react';
import { Table, Tag, Select, DatePicker, Space, Button, Modal, message, Typography } from 'antd';
import { getOrders, updateOrderStatus } from '@/api/orders';
import type { AdminOrderItem, PaginatedData } from '@/types';
import dayjs from 'dayjs';

const { Title } = Typography;
const { RangePicker } = DatePicker;

const STATUS_OPTIONS = [
  { label: '待处理', value: 'pending' },
  { label: '已支付', value: 'paid' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' },
];

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  pending: { color: 'orange', label: '待处理' },
  paid: { color: 'blue', label: '已支付' },
  shipped: { color: 'cyan', label: '已发货' },
  completed: { color: 'green', label: '已完成' },
  cancelled: { color: 'red', label: '已取消' },
};

// 状态流转规则
const NEXT_STATUS: Record<string, string[]> = {
  pending: ['paid', 'cancelled'],
  paid: ['shipped', 'cancelled'],
  shipped: ['completed'],
  completed: [],
  cancelled: [],
};

const Orders: React.FC = () => {
  const [data, setData] = useState<PaginatedData<AdminOrderItem>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>();
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [page, setPage] = useState(1);

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await getOrders({
        page: p, page_size: 10, status: filterStatus,
        start_date: dateRange?.[0], end_date: dateRange?.[1],
      });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, [filterStatus, dateRange]);

  const handleStatusChange = (record: AdminOrderItem, newStatus: string) => {
    Modal.confirm({
      title: '确认更新订单状态',
      content: `将订单 ${record.order_no} 状态从「${STATUS_MAP[record.status]?.label}」更新为「${STATUS_MAP[newStatus]?.label}」？`,
      onOk: async () => {
        const res = await updateOrderStatus(record.id, newStatus);
        if (res.data.code === 0) { message.success('状态已更新'); load(); }
        else message.error(res.data.message);
      },
    });
  };

  const columns = [
    { title: '订单号', dataIndex: 'order_no', key: 'order_no', width: 200 },
    { title: '用户 ID', dataIndex: 'user_id', key: 'user_id', width: 120, ellipsis: true, render: (v: string) => v.slice(0, 8) + '...' },
    { title: '金额', dataIndex: 'total_amount', key: 'total_amount', width: 100, render: (v: number) => `¥${Number(v).toFixed(2)}` },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: (s: string) => <Tag color={STATUS_MAP[s]?.color}>{STATUS_MAP[s]?.label || s}</Tag> },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 200, render: (_: any, record: AdminOrderItem) => {
        const nextStatuses = NEXT_STATUS[record.status] || [];
        if (nextStatuses.length === 0) return <span style={{ color: '#999' }}>无可用操作</span>;
        return (
          <Space size="small">
            {nextStatuses.map((s) => (
              <Button key={s} type="link" size="small" onClick={() => handleStatusChange(record, s)}>
                {STATUS_MAP[s]?.label}
              </Button>
            ))}
          </Space>
        );
      },
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>订单管理</Title>
        <Space>
          <Select placeholder="状态筛选" allowClear style={{ width: 120 }} value={filterStatus} onChange={(v) => { setFilterStatus(v); setPage(1); }} options={STATUS_OPTIONS} />
          <RangePicker onChange={(_, dateStrings) => { setDateRange(dateStrings[0] ? [dateStrings[0], dateStrings[1]] : null); setPage(1); }} />
        </Space>
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading} scroll={{ x: 1100 }}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />
    </div>
  );
};

export default Orders;
