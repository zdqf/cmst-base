import React, { useEffect, useState } from 'react';
import { Table, Button, Tag, Input, Select, Space, Modal, Form, message, Popconfirm, Typography, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, SearchOutlined, RobotOutlined } from '@ant-design/icons';
import { getHerbs, createHerb, updateHerb, updateHerbStatus, generateHerbContent } from '@/api/herbs';
import type { HerbDetail, PaginatedData } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const HERB_CATEGORIES = ['补气类', '补血类', '清热类', '解表类', '理气类', '活血类', '化痰类', '其他'];

const Herbs: React.FC = () => {
  const [data, setData] = useState<PaginatedData<HerbDetail>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [keyword, setKeyword] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>();
  const [filterStatus, setFilterStatus] = useState<string>();
  const [page, setPage] = useState(1);
  const [generating, setGenerating] = useState<string | null>(null);
  const [form] = Form.useForm();

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await getHerbs({ page: p, page_size: 10, category: filterCategory, keyword: keyword || undefined, status: filterStatus });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, [filterCategory, filterStatus]);

  const openCreate = () => { setEditingId(null); form.resetFields(); setModalOpen(true); };
  const openEdit = (record: HerbDetail) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    const res = editingId ? await updateHerb(editingId, values) : await createHerb(values);
    if (res.data.code === 0) {
      message.success(editingId ? '更新成功' : '创建成功');
      setModalOpen(false);
      load();
    } else {
      message.error(res.data.message);
    }
  };

  const handleToggleStatus = async (record: HerbDetail) => {
    const newStatus = record.status === 'active' ? 'inactive' : 'active';
    const res = await updateHerbStatus(record.id, newStatus);
    if (res.data.code === 0) { message.success(res.data.message); load(); }
    else message.error(res.data.message);
  };

  const handleGenerate = async (id: string) => {
    setGenerating(id);
    try {
      const res = await generateHerbContent(id);
      if (res.data.code === 0) {
        Modal.info({ title: 'AI 生成内容', content: <pre style={{ whiteSpace: 'pre-wrap', maxHeight: 400, overflow: 'auto' }}>{res.data.data?.content}</pre>, width: 640 });
      } else {
        message.error(res.data.message);
      }
    } finally {
      setGenerating(null);
    }
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name', width: 120 },
    { title: '分类', dataIndex: 'category', key: 'category', width: 100, render: (v: string | null) => v || '-' },
    { title: '性味归经', dataIndex: 'flavor_meridian', key: 'flavor_meridian', ellipsis: true, width: 200 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 80, render: (s: string) => <Tag color={s === 'active' ? 'green' : 'default'}>{s === 'active' ? '上架' : '下架'}</Tag> },
    { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 260, render: (_: any, record: HerbDetail) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title={`确定${record.status === 'active' ? '下架' : '上架'}？`} onConfirm={() => handleToggleStatus(record)}>
            <Button type="link" size="small">{record.status === 'active' ? '下架' : '上架'}</Button>
          </Popconfirm>
          <Tooltip title="AI 生成内容">
            <Button type="link" size="small" icon={<RobotOutlined />} loading={generating === record.id} onClick={() => handleGenerate(record.id)}>AI生成</Button>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>中药管理</Title>
        <Space>
          <Input placeholder="搜索名称" prefix={<SearchOutlined />} value={keyword} onChange={(e) => setKeyword(e.target.value)} onPressEnter={() => { setPage(1); load(1); }} style={{ width: 160 }} allowClear />
          <Select placeholder="分类" allowClear style={{ width: 120 }} value={filterCategory} onChange={(v) => { setFilterCategory(v); setPage(1); }} options={HERB_CATEGORIES.map((c) => ({ label: c, value: c }))} />
          <Select placeholder="状态" allowClear style={{ width: 100 }} value={filterStatus} onChange={(v) => { setFilterStatus(v); setPage(1); }} options={[{ label: '上架', value: 'active' }, { label: '下架', value: 'inactive' }]} />
          <Button onClick={() => { setPage(1); load(1); }}>搜索</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新增中药</Button>
        </Space>
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading} scroll={{ x: 900 }}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />
      <Modal title={editingId ? '编辑中药' : '新增中药'} open={modalOpen} onOk={handleSave} onCancel={() => setModalOpen(false)} width={640} okText="保存" cancelText="取消" destroyOnClose>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入中药名称' }]}>
            <Input placeholder="如：黄芪" />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Select placeholder="选择分类" allowClear options={HERB_CATEGORIES.map((c) => ({ label: c, value: c }))} />
          </Form.Item>
          <Form.Item name="origin_and_form" label="来源与形态">
            <TextArea rows={2} placeholder="产地、外观形态描述" />
          </Form.Item>
          <Form.Item name="flavor_meridian" label="性味归经">
            <TextArea rows={2} placeholder="性味归经白话解释" />
          </Form.Item>
          <Form.Item name="common_pairings" label="常见搭配方向">
            <TextArea rows={2} placeholder="常见搭配方向" />
          </Form.Item>
          <Form.Item name="unsuitable_groups" label="不适合人群">
            <TextArea rows={2} placeholder="不适合人群" />
          </Form.Item>
          <Form.Item name="precautions" label="注意事项">
            <TextArea rows={2} placeholder="注意事项" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Herbs;
