import { Alert } from 'antd'
import { WarningOutlined } from '@ant-design/icons'

interface DisclaimerProps {
  type?: 'full' | 'short'
}

const FULL_TEXT = '以下内容仅为传统中药知识科普与调理方向参考，不构成医疗诊断或治疗建议，如有健康问题请咨询专业医师'
const SHORT_TEXT = '本内容仅供科普参考，不构成医疗建议'

export default function Disclaimer({ type = 'full' }: DisclaimerProps) {
  return (
    <Alert
      type="warning"
      showIcon
      icon={<WarningOutlined />}
      message={type === 'full' ? '免责声明' : '提示'}
      description={type === 'full' ? FULL_TEXT : SHORT_TEXT}
      style={{ borderRadius: 8, marginBottom: 16 }}
    />
  )
}
