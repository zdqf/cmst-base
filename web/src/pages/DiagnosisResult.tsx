import { useLocation, Navigate, useNavigate } from 'react-router-dom'
import { Card, Typography, Alert, Button, Space, Divider, Tag } from 'antd'
import { CheckCircleOutlined, HistoryOutlined, HomeOutlined, WarningOutlined, MedicineBoxOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import type { DiagnosisResult as DiagnosisResultType } from '../types'

const { Title, Text, Paragraph } = Typography

export default function DiagnosisResult() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = (location.state as { result?: DiagnosisResultType } | null)?.result

  if (!result) return <Navigate to="/diagnosis" replace />

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px 24px 48px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Success Header */}
        <div style={{
          background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
          borderRadius: 16, padding: '32px 24px', marginBottom: 24, textAlign: 'center',
        }}>
          <CheckCircleOutlined style={{ fontSize: 48, color: '#2c6b4f', marginBottom: 12 }} />
          <Title level={3} style={{ margin: 0, color: '#2c6b4f' }}>问诊分析完成</Title>
          <Text type="secondary">以下为 AI 基于中医理论的调理方向参考</Text>
        </div>

        <Alert
          type="warning" showIcon icon={<WarningOutlined />}
          message="免责声明"
          description="以下内容仅为传统中药知识科普与调理方向参考，不构成医疗诊断或治疗建议，如有健康问题请咨询专业医师。"
          style={{ marginBottom: 24, borderRadius: 12 }}
        />

        <Card style={{ borderRadius: 16, border: 'none' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <MedicineBoxOutlined style={{ fontSize: 20, color: '#2c6b4f' }} />
            <Title level={4} style={{ margin: 0 }}>分析结果</Title>
          </div>
          <div style={{
            background: '#f9fafb', borderRadius: 12, padding: 24,
            whiteSpace: 'pre-wrap', lineHeight: 2, fontSize: 14, color: '#333',
          }}>
            {result.ai_output}
          </div>
        </Card>

        <div style={{ display: 'flex', gap: 12, marginTop: 24, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button icon={<MedicineBoxOutlined />} onClick={() => navigate('/diagnosis')}>再次问诊</Button>
          <Button icon={<HistoryOutlined />} onClick={() => navigate('/diagnosis/history')}>问诊历史</Button>
          <Button type="primary" icon={<HomeOutlined />} onClick={() => navigate('/')}>返回首页</Button>
        </div>
      </motion.div>
    </div>
  )
}
