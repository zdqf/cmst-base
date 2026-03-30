import React, { useEffect, useState } from 'react';
import { Table, Space, Button, Modal, DatePicker, Input, Typography, Descriptions, Tag } from 'antd';
import { EyeOutlined, SearchOutlined } from '@ant-design/icons';
import { getDiagnosisLogs, getDiagnosisLogDetail } from '@/api/diagnosisLogs';
import type { AdminDiagnosisLogItem, PaginatedData } from '@/types';

const { Title, Paragraph } = Typography;
const { RangePicker } = DatePicker;

const GENDER_MAP: Record<string, string> = { male: '男', female: '女' };

const DiagnosisLogs: React.FC = () => {
  const [data, setData] = useState<PaginatedData<AdminDiagnosisLogItem>>({ items: [], total: 0, page: 1, page_size: 10, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [userId, setUserId] = useState('');
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detail, setDetail] = useState<AdminDiagnosisLogItem | null>(null);

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await getDiagnosisLogs({
        page: p, page_size: 10,
        user_id: userId || undefined,
        start_date: dateRange?.[0], end_date: dateRange?.[1],
      });
      if (res.data.code === 0) setData(res.data.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, [dateRange]);

  const openDetail = async (id: string) => {
    const res = await getDiagnosisLogDetail(id);
    if (res.data.code === 0) {
      setDetail(res.data.data);
      setDetailOpen(true);
    }
  };

  const columns = [
    { title: '用户 ID', dataIndex: 'user_id', key: 'user_id', width: 120, ellipsis: true, render: (v: string) => v.slice(0, 8) + '...' },
    {
      title: '症状摘要', key: 'symptoms', ellipsis: true, render: (_: any, record: AdminDiagnosisLogItem) => {
        const symptoms = record.input_data?.symptoms || record.input_data?.主要不适描述 || '-';
        return typeof symptoms === 'string' ? symptoms.slice(0, 50) : '-';
      },
    },
    {
      title: '性别/年龄', key: 'info', width: 100, render: (_: any, record: AdminDiagnosisLogItem) => {
        const gender = GENDER_MAP[record.input_data?.gender] || record.input_data?.gender || '';
        const age = record.input_data?.age || '';
        return `${gender} ${age}岁`;
      },
    },
    { title: 'AI 输出摘要', dataIndex: 'ai_output', key: 'ai_output', ellipsis: true, render: (v: string) => v?.slice(0, 60) + '...' },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 170, render: (v: string) => new Date(v).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'action', width: 80, render: (_: any, record: AdminDiagnosisLogItem) => (
        <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => openDetail(record.id)}>详情</Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>问诊记录</Title>
        <Space>
          <Input placeholder="用户 ID" prefix={<SearchOutlined />} value={userId} onChange={(e) => setUserId(e.target.value)} onPressEnter={() => { setPage(1); load(1); }} style={{ width: 200 }} allowClear />
          <RangePicker onChange={(_, dateStrings) => { setDateRange(dateStrings[0] ? [dateStrings[0], dateStrings[1]] : null); setPage(1); }} />
          <Button type="primary" onClick={() => { setPage(1); load(1); }}>搜索</Button>
        </Space>
      </div>
      <Table
        columns={columns} dataSource={data.items} rowKey="id" loading={loading} scroll={{ x: 900 }}
        pagination={{ current: data.page, pageSize: data.page_size, total: data.total, onChange: (p) => { setPage(p); load(p); }, showTotal: (t) => `共 ${t} 条` }}
      />
      <Modal title="问诊详情" open={detailOpen} onCancel={() => setDetailOpen(false)} width={700} footer={<Button onClick={() => setDetailOpen(false)}>关闭</Button>}>
        {detail && (
          <>
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="用户 ID" span={2}>{detail.user_id}</Descriptions.Item>
              <Descriptions.Item label="年龄">{detail.input_data?.age}</Descriptions.Item>
              <Descriptions.Item label="性别">{GENDER_MAP[detail.input_data?.gender] || detail.input_data?.gender}</Descriptions.Item>
              <Descriptions.Item label="症状描述" span={2}>{detail.input_data?.symptoms}</Descriptions.Item>
              {detail.input_data?.allergy_history && <Descriptions.Item label="过敏史" span={2}>{detail.input_data.allergy_history}</Descriptions.Item>}
              {detail.input_data?.current_medication && <Descriptions.Item label="当前用药" span={2}>{detail.input_data.current_medication}</Descriptions.Item>}
              {detail.prompt_version && <Descriptions.Item label="Prompt 版本">{detail.prompt_version}</Descriptions.Item>}
              <Descriptions.Item label="时间">{new Date(detail.created_at).toLocaleString('zh-CN')}</Descriptions.Item>
            </Descriptions>
            <Title level={5}>AI 输出</Title>
            <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8, maxHeight: 400, overflow: 'auto' }}>
              <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{detail.ai_output}</Paragraph>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
};

export default DiagnosisLogs;
