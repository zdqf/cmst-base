import { useLocation, useNavigate, Link } from 'react-router-dom'
import { useEffect } from 'react'
import { Card, Typography, Button, Space, Result, QRCode } from 'antd'
import { HomeOutlined, WechatOutlined } from '@ant-design/icons'
import { motion } from 'framer-motion'
import type { ConsultationResponse } from '../types'

const { Title, Text } = Typography

export default function ConsultationSuccess() {
  const location = useLocation()
  const navigate = useNavigate()
  const result = (location.state as { result?: ConsultationResponse } | null)?.result

  useEffect(() => {
    if (!result) navigate('/consultation', { replace: true })
  }, [result, navigate])

  if (!result) return null

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: '48px 24px' }}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}>
        <Card style={{ borderRadius: 20, border: 'none', textAlign: 'center' }}>
          <Result
            status="success"
            title="咨询提交成功"
            subTitle="我们已收到您的咨询，请通过以下方式联系我们"
          />

          <Card style={{ borderRadius: 12, background: '#f0f7f4', marginBottom: 24 }}>
            <WechatOutlined style={{ fontSize: 32, color: '#07c160', marginBottom: 8 }} />
            <Title level={4} style={{ margin: '8px 0' }}>微信 / 企业微信</Title>
            <Text copyable style={{ fontSize: 18, fontWeight: 600 }}>{result.wechat_id}</Text>

            {result.qr_code_url && (
              <div style={{ marginTop: 16 }}>
                <img src={result.qr_code_url} alt="微信二维码" style={{ maxWidth: 200, borderRadius: 8 }} />
              </div>
            )}
          </Card>

          <Space>
            <Button type="primary" icon={<HomeOutlined />} onClick={() => navigate('/')} size="large" style={{ borderRadius: 10 }}>
              返回首页
            </Button>
          </Space>
        </Card>
      </motion.div>
    </div>
  )
}
