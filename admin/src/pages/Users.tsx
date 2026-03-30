import React, { useEffect, useState } from 'react';
import { Table, Input, Tag, Button, message, Popconfirm, Typography, Space } from 'antd';
import { SearchOutlined, StopOutlined } from '@ant-design/icons';
import { getUsers, disableUser } from '@/api/users';
import type { AdminUserItem, PaginatedData } from '@/types';

const { Title } = Typography;

const Users: React.FC = () => {
  const [data, setData] = useState<PaginatedData<AdminUserItem>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [phone, setPhone] = useState('');
  const [page, setPage] = useState(1);

  const load = async (p = page, search = phone) => {
    setLoading(true);
    try {
      const res = await getUsers({ page: p, page_size: 10, phone: search || undefined });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, []);

  const handleDisable = async (id: string) => {
    const res = await disableUser(id);
    if (res.data.code === 0) {
      message.success('用户已禁用');
      load();
    } else {
      message.error(res.data.message);
    }
  };

  const columns = [
    { title: '手机号', dataIndex: 'phone', key: 'phone' },
    { title: '昵称', dataIndex: 'nickname', key: 'nickname', render: (v: string | null) => v || '-' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s: string) => <Tag color={s === 'active' ? 'green' : 'red'}>{s === 'active' ? '正常' : '已禁用'}</Tag> },
    { title: '管理员', dataIndex: 'is_admin', key: 'is_admin', render: (v: boolean) => v ? <Tag color="blue">是</Tag> : '否' },
    { title: '最后登录', dataIndex: 'last_login_at', key: 'last_login_at', render: (v: string | null) => v ? new Date(v).toLocaleString('zh-CN') : '-' },
    { title: '注册时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', render: (_: any, record: AdminUserItem) => (
        record.status === 'active' && !record.is_admin ? (
          <Popconfirm title="确定禁用该用户？" onConfirm={() => handleDisable(record.id)} okText="确定" cancelText="取消">
            <Button type="link" danger icon={<StopOutlined />} size="small">禁用</Button>
          </Popconfirm>
        ) : null
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>用户管理</Title>
        <Space>
          <Input placeholder="搜索手机号" prefix={<SearchOutlined />} value={phone} onChange={(e) => setPhone(e.target.value)} onPressEnter={() => { setPage(1); load(1, phone); }} style={{ width: 200 }} allowClear />
          <Button type="primary" onClick={() => { setPage(1); load(1, phone); }}>搜索</Button>
        </Space>
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />
    </div>
  );
};

export default Users;
