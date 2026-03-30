import React, { useEffect, useState } from 'react';
import { Card, Tabs, Button, Form, Input, Table, Tag, Modal, message, Typography, Space, Spin } from 'antd';
import { EditOutlined, HistoryOutlined, ExperimentOutlined } from '@ant-design/icons';
import { getActivePrompt, updatePrompt, getPromptHistory, testPrompt } from '@/api/prompts';
import type { PromptTemplate, PaginatedData } from '@/types';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const PROMPT_TYPES = [
  { key: 'health_advisor', label: '健康顾问' },
  { key: 'pairing_assistant', label: '科普助手' },
  { key: 'content_generator', label: '科普内容生成' },
];

const Prompts: React.FC = () => {
  const [activeType, setActiveType] = useState('health_advisor');
  const [activeTemplate, setActiveTemplate] = useState<PromptTemplate | null>(null);
  const [loading, setLoading] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [testOpen, setTestOpen] = useState(false);
  const [history, setHistory] = useState<PaginatedData<PromptTemplate>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [historyPage, setHistoryPage] = useState(1);
  const [testResult, setTestResult] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [editForm] = Form.useForm();
  const [testForm] = Form.useForm();

  const loadActive = async (type = activeType) => {
    setLoading(true);
    try {
      const res = await getActivePrompt(type);
      if (res.data.code === 0) setActiveTemplate(res.data.data);
      else setActiveTemplate(null);
    } catch {
      setActiveTemplate(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadActive(activeType); }, [activeType]);

  const openEdit = () => {
    editForm.setFieldsValue({
      content: activeTemplate?.content || '',
      role_name: activeTemplate?.role_name || '',
    });
    setEditOpen(true);
  };

  const handleSave = async () => {
    const values = await editForm.validateFields();
    const res = await updatePrompt(activeType, values);
    if (res.data.code === 0) {
      message.success('模板已更新（新版本）');
      setEditOpen(false);
      loadActive();
    } else {
      message.error(res.data.message);
    }
  };

  const openHistory = async () => {
    setHistoryOpen(true);
    loadHistory(1);
  };

  const loadHistory = async (p: number) => {
    const res = await getPromptHistory(activeType, { page: p, page_size: 10 });
    if (res.data.code === 0) setHistory(res.data.data);
    setHistoryPage(p);
  };

  const openTest = () => {
    testForm.resetFields();
    setTestResult('');
    setTestOpen(true);
  };

  const handleTest = async () => {
    const values = await testForm.validateFields();
    setTestLoading(true);
    try {
      const res = await testPrompt({ type: activeType, test_input: values.test_input });
      if (res.data.code === 0) {
        setTestResult(res.data.data?.ai_output || '');
      } else {
        message.error(res.data.message);
      }
    } finally {
      setTestLoading(false);
    }
  };

  const historyColumns = [
    { title: '版本', dataIndex: 'version', key: 'version', width: 80, render: (v: number) => `v${v}` },
    { title: '角色名', dataIndex: 'role_name', key: 'role_name', width: 120 },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 80, render: (v: boolean) => v ? <Tag color="green">当前</Tag> : <Tag>历史</Tag> },
    { title: '内容摘要', dataIndex: 'content', key: 'content', ellipsis: true, render: (v: string) => v?.slice(0, 80) + '...' },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 80, render: (_: any, record: PromptTemplate) => (
        <Button type="link" size="small" onClick={() => Modal.info({ title: `v${record.version} 完整内容`, content: <pre style={{ whiteSpace: 'pre-wrap', maxHeight: 500, overflow: 'auto' }}>{record.content}</pre>, width: 640 })}>查看</Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>Prompt 模板管理</Title>
      <Tabs activeKey={activeType} onChange={(k) => setActiveType(k)} items={PROMPT_TYPES.map((t) => ({ key: t.key, label: t.label }))} />

      <Spin spinning={loading}>
        {activeTemplate ? (
          <Card
            title={<Space><span>{activeTemplate.role_name}</span><Tag color="green">v{activeTemplate.version} · 当前活跃</Tag></Space>}
            extra={
              <Space>
                <Button icon={<EditOutlined />} onClick={openEdit}>编辑</Button>
                <Button icon={<HistoryOutlined />} onClick={openHistory}>版本历史</Button>
                <Button icon={<ExperimentOutlined />} type="primary" onClick={openTest}>测试</Button>
              </Space>
            }
          >
            <div style={{ background: '#fafafa', padding: 16, borderRadius: 8, maxHeight: 400, overflow: 'auto' }}>
              <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{activeTemplate.content}</Paragraph>
            </div>
            <div style={{ marginTop: 12, color: '#999', fontSize: 12 }}>
              更新时间：{new Date(activeTemplate.updated_at).toLocaleString('zh-CN')}
            </div>
          </Card>
        ) : (
          <Card>
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              暂无该类型的活跃模板
              <br />
              <Button type="primary" style={{ marginTop: 16 }} onClick={openEdit}>创建模板</Button>
            </div>
          </Card>
        )}
      </Spin>

      {/* 编辑模板 */}
      <Modal title="编辑 Prompt 模板" open={editOpen} onOk={handleSave} onCancel={() => setEditOpen(false)} width={700} okText="保存（创建新版本）" cancelText="取消" destroyOnClose>
        <Form form={editForm} layout="vertical">
          <Form.Item name="role_name" label="角色名称">
            <Input placeholder="如：健康顾问" />
          </Form.Item>
          <Form.Item name="content" label="模板内容" rules={[{ required: true, message: '请输入模板内容' }]}>
            <TextArea rows={12} placeholder="输入 Prompt 模板内容..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* 版本历史 */}
      <Modal title="版本历史" open={historyOpen} onCancel={() => setHistoryOpen(false)} width={800} footer={<Button onClick={() => setHistoryOpen(false)}>关闭</Button>}>
        <Table
          columns={historyColumns} dataSource={history.items} rowKey="id" size="small"
          pagination={{ current: historyPage, pageSize: 10, total: history.total, onChange: loadHistory }}
        />
      </Modal>

      {/* 测试 */}
      <Modal title="测试 Prompt" open={testOpen} onCancel={() => setTestOpen(false)} width={700} footer={[
        <Button key="cancel" onClick={() => setTestOpen(false)}>关闭</Button>,
        <Button key="test" type="primary" loading={testLoading} onClick={handleTest}>发送测试</Button>,
      ]}>
        <Form form={testForm} layout="vertical">
          <Form.Item name="test_input" label="测试输入" rules={[{ required: true, message: '请输入测试内容' }]}>
            <TextArea rows={4} placeholder="输入测试数据..." />
          </Form.Item>
        </Form>
        {testResult && (
          <>
            <Title level={5}>AI 输出</Title>
            <div style={{ background: '#f0f5ff', padding: 16, borderRadius: 8, maxHeight: 300, overflow: 'auto' }}>
              <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{testResult}</Paragraph>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
};

export default Prompts;
