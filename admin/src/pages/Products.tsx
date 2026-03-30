import React, { useEffect, useState } from 'react';
import { Table, Button, Tag, Select, Space, Modal, Form, Input, InputNumber, message, Popconfirm, Typography } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { getProducts, createProduct, updateProduct, updateProductStatus, updateProductStock } from '@/api/products';
import type { ProductDetail, PaginatedData } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

const PRODUCT_CATEGORIES = ['原药材', '简加工产品', '调理组合包'];

const Products: React.FC = () => {
  const [data, setData] = useState<PaginatedData<ProductDetail>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [stockModalOpen, setStockModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [stockTarget, setStockTarget] = useState<ProductDetail | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>();
  const [filterStatus, setFilterStatus] = useState<string>();
  const [page, setPage] = useState(1);
  const [form] = Form.useForm();
  const [stockForm] = Form.useForm();

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await getProducts({ page: p, page_size: 10, category: filterCategory, status: filterStatus });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, [filterCategory, filterStatus]);

  const openCreate = () => { setEditingId(null); form.resetFields(); setModalOpen(true); };
  const openEdit = (record: ProductDetail) => {
    setEditingId(record.id);
    form.setFieldsValue({ ...record, price: Number(record.price) });
    setModalOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    const res = editingId ? await updateProduct(editingId, values) : await createProduct(values);
    if (res.data.code === 0) {
      message.success(editingId ? '更新成功' : '创建成功');
      setModalOpen(false);
      load();
    } else {
      message.error(res.data.message);
    }
  };

  const handleToggleStatus = async (record: ProductDetail) => {
    const newStatus = record.status === 'active' ? 'inactive' : 'active';
    const res = await updateProductStatus(record.id, newStatus);
    if (res.data.code === 0) { message.success(res.data.message); load(); }
    else message.error(res.data.message);
  };

  const openStockModal = (record: ProductDetail) => {
    setStockTarget(record);
    stockForm.resetFields();
    setStockModalOpen(true);
  };

  const handleStockUpdate = async () => {
    if (!stockTarget) return;
    const values = await stockForm.validateFields();
    const res = await updateProductStock(stockTarget.id, values);
    if (res.data.code === 0) {
      message.success('库存已更新');
      setStockModalOpen(false);
      load();
    } else {
      message.error(res.data.message);
    }
  };

  const columns = [
    { title: '商品名称', dataIndex: 'name', key: 'name', width: 160 },
    { title: '分类', dataIndex: 'category', key: 'category', width: 120, render: (v: string | null) => v || '-' },
    { title: '价格', dataIndex: 'price', key: 'price', width: 100, render: (v: number) => `¥${Number(v).toFixed(2)}` },
    { title: '库存', dataIndex: 'stock', key: 'stock', width: 80, render: (v: number) => <span style={{ color: v <= 10 ? '#ff4d4f' : undefined, fontWeight: v <= 10 ? 600 : undefined }}>{v}</span> },
    { title: '状态', dataIndex: 'status', key: 'status', width: 80, render: (s: string) => <Tag color={s === 'active' ? 'green' : 'default'}>{s === 'active' ? '上架' : '下架'}</Tag> },
    { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 280, render: (_: any, record: ProductDetail) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Button type="link" size="small" onClick={() => openStockModal(record)}>调库存</Button>
          <Popconfirm title={`确定${record.status === 'active' ? '下架' : '上架'}？`} onConfirm={() => handleToggleStatus(record)}>
            <Button type="link" size="small">{record.status === 'active' ? '下架' : '上架'}</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>商品管理</Title>
        <Space>
          <Select placeholder="分类" allowClear style={{ width: 140 }} value={filterCategory} onChange={(v) => { setFilterCategory(v); setPage(1); }} options={PRODUCT_CATEGORIES.map((c) => ({ label: c, value: c }))} />
          <Select placeholder="状态" allowClear style={{ width: 100 }} value={filterStatus} onChange={(v) => { setFilterStatus(v); setPage(1); }} options={[{ label: '上架', value: 'active' }, { label: '下架', value: 'inactive' }]} />
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新增商品</Button>
        </Space>
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading} scroll={{ x: 1000 }}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />

      {/* 新增/编辑商品 */}
      <Modal title={editingId ? '编辑商品' : '新增商品'} open={modalOpen} onOk={handleSave} onCancel={() => setModalOpen(false)} width={560} okText="保存" cancelText="取消" destroyOnClose>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="商品名称" rules={[{ required: true, message: '请输入商品名称' }]}>
            <Input placeholder="商品名称" />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Select placeholder="选择分类" allowClear options={PRODUCT_CATEGORIES.map((c) => ({ label: c, value: c }))} />
          </Form.Item>
          <Form.Item name="price" label="价格" rules={[{ required: true, message: '请输入价格' }]}>
            <InputNumber min={0.01} step={0.01} precision={2} prefix="¥" style={{ width: '100%' }} placeholder="0.00" />
          </Form.Item>
          <Form.Item name="specification" label="规格">
            <Input placeholder="如：500g/袋" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="商品描述" />
          </Form.Item>
          <Form.Item name="image_url" label="图片 URL">
            <Input placeholder="https://..." />
          </Form.Item>
          {!editingId && (
            <Form.Item name="stock" label="初始库存">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="0" />
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* 库存调整 */}
      <Modal title={`调整库存 — ${stockTarget?.name || ''} (当前: ${stockTarget?.stock || 0})`} open={stockModalOpen} onOk={handleStockUpdate} onCancel={() => setStockModalOpen(false)} okText="确认" cancelText="取消" destroyOnClose>
        <Form form={stockForm} layout="vertical">
          <Form.Item name="change_amount" label="变更数量" rules={[{ required: true, message: '请输入变更数量' }]} extra="正数为入库，负数为出库">
            <InputNumber style={{ width: '100%' }} placeholder="如：50 或 -10" />
          </Form.Item>
          <Form.Item name="reason" label="变更原因" rules={[{ required: true, message: '请输入变更原因' }]}>
            <Input placeholder="如：采购入库、盘点调整" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Products;
