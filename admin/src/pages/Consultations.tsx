import React, { useEffect, useState } from 'react';
import { Table, Tag, Select, Space, Button, Modal, Form, Input, message, Typography, Descriptions } from 'antd';
import { getConsultations, updateConsultationStatus, updateConsultationNotes } from '@/api/consultations';
import type { AdminConsultationItem, PaginatedData } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  pending: { color: 'orange', label: '待处理' },
  processing: { color: 'blue', label: '处理中' },
  completed: { color: 'green', label: '已完成' },
};

const Consultations: React.FC = () => {
  const [data, setData] = useState<PaginatedData<AdminConsultationItem>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>();
  const [page, setPage] = useState(1);
  const [detailOpen, setDetailOpen] = useState(false);
  const [current, setCurrent] = useState<AdminConsultationItem | null>(null);
  const [notesForm] = Form.useForm();

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await getConsultations({ page: p, page_size: 10, status: filterStatus });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, [filterStatus]);

  const handleStatusChange = async (record: AdminConsultationItem, newStatus: string) => {
    const res = await updateConsultationStatus(record.id, newStatus);
    if (res.data.code === 0) { message.success('状态已更新'); load(); }
    else message.error(res.data.message);
  };

  const openDetail = (record: AdminConsultationItem) => {
    setCurrent(record);
    notesForm.setFieldsValue({ admin_notes: record.admin_notes || '' });
    setDetailOpen(true);
  };

  const handleSaveNotes = async () => {
    if (!current) return;
    const values = await notesForm.validateFields();
    const res = await updateConsultationNotes(current.id, values.admin_notes);
    if (res.data.code === 0) {
      message.success('备注已保存');
      setDetailOpen(false);
      load();
    } else {
      message.error(res.data.message);
    }
  };

  const columns = [
    { title: '姓名', dataIndex: 'name', key: 'name', width: 100 },
    { title: '联系方式', dataIndex: 'contact', key: 'contact', width: 140 },
    { title: '主题', dataIndex: 'subject', key: 'subject', ellipsis: true, width: 200 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: (s: string) => <Tag color={STATUS_MAP[s]?.color}>{STATUS_MAP[s]?.label || s}</Tag> },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 260, render: (_: any, record: AdminConsultationItem) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => openDetail(record)}>详情/备注</Button>
          {record.status === 'pending' && <Button type="link" size="small" onClick={() => handleStatusChange(record, 'processing')}>开始处理</Button>}
          {record.status === 'processing' && <Button type="link" size="small" onClick={() => handleStatusChange(record, 'completed')}>标记完成</Button>}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>咨询管理</Title>
        <Select placeholder="状态筛选" allowClear style={{ width: 120 }} value={filterStatus} onChange={(v) => { setFilterStatus(v); setPage(1); }} options={[{ label: '待处理', value: 'pending' }, { label: '处理中', value: 'processing' }, { label: '已完成', value: 'completed' }]} />
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading} scroll={{ x: 900 }}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />
      <Modal title="咨询详情" open={detailOpen} onCancel={() => setDetailOpen(false)} width={640} footer={[
        <Button key="cancel" onClick={() => setDetailOpen(false)}>关闭</Button>,
        <Button key="save" type="primary" onClick={handleSaveNotes}>保存备注</Button>,
      ]}>
        {current && (
          <>
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="姓名">{current.name}</Descriptions.Item>
              <Descriptions.Item label="联系方式">{current.contact}</Descriptions.Item>
              <Descriptions.Item label="主题" span={2}>{current.subject}</Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>{current.description}</Descriptions.Item>
              <Descriptions.Item label="状态"><Tag color={STATUS_MAP[current.status]?.color}>{STATUS_MAP[current.status]?.label}</Tag></Descriptions.Item>
              <Descriptions.Item label="提交时间">{new Date(current.created_at).toLocaleString('zh-CN')}</Descriptions.Item>
              {current.handled_at && <Descriptions.Item label="处理时间">{new Date(current.handled_at).toLocaleString('zh-CN')}</Descriptions.Item>}
            </Descriptions>
            <Form form={notesForm} layout="vertical">
              <Form.Item name="admin_notes" label="管理员备注">
                <TextArea rows={4} placeholder="添加处理备注..." />
              </Form.Item>
            </Form>
          </>
        )}
      </Modal>
    </div>
  );
};

export default Consultations;
