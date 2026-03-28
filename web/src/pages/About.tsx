import { Card, Typography, Row, Col, Timeline, Divider, Space, Tag } from 'antd'
import {
  HeartOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
  TrophyOutlined,
  EnvironmentOutlined,
  PhoneOutlined,
  MailOutlined,
  ClockCircleOutlined,
  StarOutlined,
  RocketOutlined,
  BulbOutlined,
  GlobalOutlined,
} from '@ant-design/icons'
import { motion } from 'framer-motion'
import { LogoIcon, MountainHerbIcon } from '../assets/icons'

const { Title, Text, Paragraph } = Typography

const values = [
  { icon: <SafetyCertificateOutlined style={{ fontSize: 32, color: '#2c6b4f' }} />, title: '品质为本', desc: '严选道地药材产区，从源头把控品质，每一味药材都经过专业检测。' },
  { icon: <HeartOutlined style={{ fontSize: 32, color: '#e91e63' }} />, title: '用心服务', desc: '专业中医师团队审核所有科普内容，确保信息准确可靠。' },
  { icon: <BulbOutlined style={{ fontSize: 32, color: '#ff6d00' }} />, title: '科技赋能', desc: '运用 AI 技术辅助中医调理方向分析，让传统智慧触手可及。' },
  { icon: <GlobalOutlined style={{ fontSize: 32, color: '#1565c0' }} />, title: '传承创新', desc: '在传承千年本草智慧的基础上，以现代方式让更多人了解中药文化。' },
]

const milestones = [
  { time: '2023 年初', title: '品牌创立', desc: '草木沈塘品牌正式成立，致力于中药知识科普与优质药材甄选。' },
  { time: '2023 年中', title: '平台上线', desc: '线上平台正式上线，提供中药百科、药材商城等核心功能。' },
  { time: '2024 年初', title: 'AI 问诊上线', desc: '引入 AI 技术，推出智能问诊功能，为用户提供调理方向参考。' },
  { time: '2024 年中', title: '会员体系', desc: '推出会员积分体系，为忠实用户提供更多专属权益。' },
  { time: '2025 年', title: '持续发展', desc: '药材品类持续扩充，服务覆盖更多用户，成为值得信赖的中药科普平台。' },
]

const teamMembers = [
  { name: '首席中医顾问', role: '主任中医师，30年临床经验', avatar: '👨‍⚕️' },
  { name: '药材品控专家', role: '中药鉴定高级工程师', avatar: '🔬' },
  { name: '产品研发团队', role: '传统配方与现代工艺结合', avatar: '⚗️' },
  { name: '客户服务团队', role: '7×12小时在线服务', avatar: '💬' },
]

export default function About() {
  return (
    <div style={{ overflow: 'hidden' }}>
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #1a3c2e 0%, #2c6b4f 50%, #3d8b6a 100%)',
        padding: '64px 24px 80px',
        textAlign: 'center',
        position: 'relative',
      }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <LogoIcon style={{ fontSize: 72, color: 'rgba(255,255,255,0.8)', marginBottom: 16 }} />
          <Title style={{ color: '#fff', fontSize: 36, margin: '0 0 8px', fontWeight: 800 }}>关于草木沈塘</Title>
          <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 16 }}>传承本草智慧 · 守护自然健康</Text>
        </motion.div>
      </div>

      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '48px 24px' }}>
        {/* Brand Story */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <Card style={{ borderRadius: 16, border: 'none', marginBottom: 48 }}>
            <Row gutter={32} align="middle">
              <Col xs={24} md={10}>
                <div style={{
                  background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
                  borderRadius: 16, padding: 40, textAlign: 'center',
                }}>
                  <MountainHerbIcon style={{ fontSize: 160 }} />
                </div>
              </Col>
              <Col xs={24} md={14}>
                <Tag color="green" style={{ marginBottom: 12 }}>品牌故事</Tag>
                <Title level={3}>源于热爱，始于传承</Title>
                <Paragraph style={{ lineHeight: 2, color: '#555' }}>
                  草木沈塘，取意"草木有情，沈于塘中"。我们相信每一味中药都蕴含着大自然的智慧与力量。
                </Paragraph>
                <Paragraph style={{ lineHeight: 2, color: '#555' }}>
                  团队由资深中医师、药材鉴定专家和互联网技术人才组成，致力于将传统中药知识以现代化、数字化的方式呈现给每一位用户。我们不仅提供专业的中药科普内容，更精选全国各地道地药材，让品质药材走进千家万户。
                </Paragraph>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* Values */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <Title level={3}>我们的理念</Title>
            <Text type="secondary">四大核心价值，贯穿每一个服务环节</Text>
          </div>
          <Row gutter={[20, 20]} style={{ marginBottom: 48 }}>
            {values.map((v, i) => (
              <Col xs={12} md={6} key={i}>
                <Card style={{ borderRadius: 16, border: 'none', textAlign: 'center', height: '100%' }}
                  styles={{ body: { padding: '28px 16px' } }}>
                  <div style={{ marginBottom: 12 }}>{v.icon}</div>
                  <Title level={5} style={{ marginBottom: 8 }}>{v.title}</Title>
                  <Text type="secondary" style={{ fontSize: 12, lineHeight: 1.6 }}>{v.desc}</Text>
                </Card>
              </Col>
            ))}
          </Row>
        </motion.div>

        {/* Timeline */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <Title level={3}>发展历程</Title>
          </div>
          <Card style={{ borderRadius: 16, border: 'none', marginBottom: 48 }}>
            <Timeline
              mode="left"
              items={milestones.map(m => ({
                color: '#2c6b4f',
                children: (
                  <div style={{ paddingBottom: 16 }}>
                    <Tag color="green">{m.time}</Tag>
                    <Title level={5} style={{ margin: '8px 0 4px' }}>{m.title}</Title>
                    <Text type="secondary" style={{ fontSize: 13 }}>{m.desc}</Text>
                  </div>
                ),
              }))}
            />
          </Card>
        </motion.div>

        {/* Team */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <Title level={3}>专业团队</Title>
          </div>
          <Row gutter={[16, 16]} style={{ marginBottom: 48 }}>
            {teamMembers.map((m, i) => (
              <Col xs={12} md={6} key={i}>
                <Card style={{ borderRadius: 16, border: 'none', textAlign: 'center' }}
                  styles={{ body: { padding: '24px 16px' } }}>
                  <div style={{ fontSize: 48, marginBottom: 12 }}>{m.avatar}</div>
                  <Text strong style={{ display: 'block' }}>{m.name}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>{m.role}</Text>
                </Card>
              </Col>
            ))}
          </Row>
        </motion.div>

        {/* Contact */}
        <Card style={{
          borderRadius: 16, border: 'none',
          background: 'linear-gradient(135deg, #f0f7f4 0%, #e8f5e9 100%)',
        }}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <Title level={3} style={{ color: '#2c6b4f' }}>联系我们</Title>
          </div>
          <Row gutter={[32, 24]} justify="center">
            {[
              { icon: <PhoneOutlined style={{ fontSize: 24, color: '#2c6b4f' }} />, label: '客服热线', value: '400-XXX-XXXX' },
              { icon: <MailOutlined style={{ fontSize: 24, color: '#2c6b4f' }} />, label: '电子邮箱', value: 'hello@caomushentang.com' },
              { icon: <ClockCircleOutlined style={{ fontSize: 24, color: '#2c6b4f' }} />, label: '服务时间', value: '周一至周六 9:00-18:00' },
              { icon: <EnvironmentOutlined style={{ fontSize: 24, color: '#2c6b4f' }} />, label: '公司地址', value: '中国 · 北京' },
            ].map((c, i) => (
              <Col xs={12} md={6} key={i} style={{ textAlign: 'center' }}>
                {c.icon}
                <Text type="secondary" style={{ display: 'block', fontSize: 12, marginTop: 8 }}>{c.label}</Text>
                <Text strong style={{ fontSize: 13 }}>{c.value}</Text>
              </Col>
            ))}
          </Row>
        </Card>
      </div>
    </div>
  )
}
