import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, message, Popconfirm, Typography, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { getComplianceWords, createComplianceWord, updateComplianceWord, deleteComplianceWord } from '@/api/compliance';
import type { ComplianceWord, PaginatedData } from '@/types';

const { Title } = Typography;

const Compliance: React.FC = () => {
  const [data, setData] = useState<PaginatedData<ComplianceWord>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [form] = Form.useForm();

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await getComplianceWords({ page: p, page_size: 10 });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, []);

  const openCreate = () => { setEditingId(null); form.resetFields(); setModalOpen(true); };
  const openEdit = (record: ComplianceWord) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    const res = editingId ? await updateComplianceWord(editingId, values) : await createComplianceWord(values);
    if (res.data.code === 0) {
      message.success(editingId ? '更新成功' : '添加成功');
      setModalOpen(false);
      load();
    } else {
      message.error(res.data.message);
    }
  };

  const handleDelete = async (id: string) => {
    const res = await deleteComplianceWord(id);
    if (res.data.code === 0) { message.success('已删除'); load(); }
    else message.error(res.data.message);
  };

  const columns = [
    { title: '违规词', dataIndex: 'forbidden_word', key: 'forbidden_word', render: (v: string) => <Tag color="red">{v}</Tag> },
    { title: '替换词', dataIndex: 'replacement', key: 'replacement', render: (v: string | null) => v ? <Tag color="green">{v}</Tag> : <span style={{ color: '#999' }}>（直接过滤）</span> },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 160, render: (_: any, record: ComplianceWord) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除该违规词？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>合规配置</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>添加违规词</Button>
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />
      <Modal title={editingId ? '编辑违规词' : '添加违规词'} open={modalOpen} onOk={handleSave} onCancel={() => setModalOpen(false)} okText="保存" cancelText="取消" destroyOnClose>
        <Form form={form} layout="vertical">
          <Form.Item name="forbidden_word" label="违规词" rules={[{ required: true, message: '请输入违规词' }]}>
            <Input placeholder="如：包治百病" />
          </Form.Item>
          <Form.Item name="replacement" label="替换词" extra="留空则直接过滤该词">
            <Input placeholder="如：辅助调理（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Compliance;
