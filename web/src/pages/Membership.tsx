import { useNavigate } from 'react-router-dom'
import { Card, Typography, Button, Row, Col, Tag, Space, Divider, List, Progress } from 'antd'
import {
  CrownOutlined,
  GiftOutlined,
  ThunderboltOutlined,
  StarOutlined,
  CheckCircleOutlined,
  RightOutlined,
  FireOutlined,
  HeartOutlined,
  SafetyCertificateOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import { motion } from 'framer-motion'
import { VipCrownIcon } from '../assets/icons'

const { Title, Text, Paragraph } = Typography

const memberLevels = [
  {
    name: '草木新友',
    level: 1,
    color: '#8d6e63',
    bg: 'linear-gradient(135deg, #efebe9 0%, #d7ccc8 100%)',
    icon: '🌱',
    threshold: 0,
    discount: '9.8折',
    benefits: ['新人专享优惠券', '免费问诊 1 次/月', '积分兑换'],
  },
  {
    name: '本草知己',
    level: 2,
    color: '#78909c',
    bg: 'linear-gradient(135deg, #eceff1 0%, #cfd8dc 100%)',
    icon: '🌿',
    threshold: 500,
    discount: '9.5折',
    benefits: ['每月专属优惠', '免费问诊 3 次/月', '优先客服', '生日礼包'],
  },
  {
    name: '沈塘贵宾',
    level: 3,
    color: '#f9a825',
    bg: 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)',
    icon: '👑',
    threshold: 2000,
    discount: '9折',
    benefits: ['无限免费问诊', '专属中医师顾问', '新品优先体验', '年度健康报告', '定制调理方案'],
  },
]

const pointsActivities = [
  { action: '每日签到', points: '+5', icon: <StarOutlined style={{ color: '#f9a825' }} /> },
  { action: '完成问诊', points: '+20', icon: <HeartOutlined style={{ color: '#e91e63' }} /> },
  { action: '购买商品', points: '消费1元=1积分', icon: <GiftOutlined style={{ color: '#2c6b4f' }} /> },
  { action: '分享好友', points: '+50', icon: <ThunderboltOutlined style={{ color: '#ff6d00' }} /> },
  { action: '评价商品', points: '+10', icon: <CheckCircleOutlined style={{ color: '#1565c0' }} /> },
]

export default function Membership() {
  const navigate = useNavigate()

  return (
    <div style={{ overflow: 'hidden' }}>
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #1a3c2e 0%, #2c6b4f 40%, #3d8b6a 100%)',
        padding: '48px 24px 72px',
        textAlign: 'center',
        position: 'relative',
      }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <VipCrownIcon style={{ fontSize: 80, marginBottom: 16 }} />
          <Title level={2} style={{ color: '#fff', margin: 0 }}>会员中心</Title>
          <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 15 }}>加入草木沈塘会员，享受专属健康权益</Text>

          {/* Current status card */}
          <Card style={{
            maxWidth: 400, margin: '24px auto 0', borderRadius: 16, border: 'none',
            background: 'rgba(255,255,255,0.12)', backdropFilter: 'blur(10px)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ fontSize: 36 }}>🌱</div>
              <div style={{ textAlign: 'left', flex: 1 }}>
                <Text style={{ color: '#fff', fontWeight: 600, display: 'block' }}>草木新友</Text>
                <Text style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>当前积分：128</Text>
              </div>
              <Tag style={{ background: 'rgba(255,255,255,0.2)', color: '#fff', border: 'none' }}>Lv.1</Tag>
            </div>
            <div style={{ marginTop: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text style={{ color: 'rgba(255,255,255,0.6)', fontSize: 11 }}>距离下一等级还需 372 积分</Text>
                <Text style={{ color: 'rgba(255,255,255,0.6)', fontSize: 11 }}>128/500</Text>
              </div>
              <Progress percent={25.6} showInfo={false} strokeColor="#ffd54f" trailColor="rgba(255,255,255,0.1)" size="small" />
            </div>
          </Card>
        </motion.div>
      </div>

      <div style={{ maxWidth: 1100, margin: '-32px auto 0', padding: '0 24px 48px', position: 'relative', zIndex: 1 }}>
        {/* Member Levels */}
        <Row gutter={[20, 20]} style={{ marginBottom: 48 }}>
          {memberLevels.map((level, i) => (
            <Col xs={24} md={8} key={i}>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                <Card
                  style={{
                    borderRadius: 16, border: level.level === 3 ? '2px solid #ffd54f' : 'none',
                    overflow: 'hidden', height: '100%',
                    boxShadow: level.level === 3 ? '0 8px 32px rgba(249,168,37,0.15)' : '0 4px 16px rgba(0,0,0,0.06)',
                  }}
                  styles={{ body: { padding: 0 } }}
                >
                  <div style={{ background: level.bg, padding: '24px 20px', textAlign: 'center' }}>
                    <div style={{ fontSize: 40, marginBottom: 8 }}>{level.icon}</div>
                    <Title level={4} style={{ margin: 0, color: level.color }}>{level.name}</Title>
                    <Tag color={level.level === 3 ? 'gold' : 'default'} style={{ marginTop: 8 }}>
                      {level.threshold === 0 ? '注册即享' : `${level.threshold} 积分升级`}
                    </Tag>
                  </div>
                  <div style={{ padding: '20px' }}>
                    <div style={{ textAlign: 'center', marginBottom: 16 }}>
                      <Text style={{ fontSize: 28, fontWeight: 700, color: level.color }}>{level.discount}</Text>
                      <Text type="secondary" style={{ display: 'block', fontSize: 12 }}>全场商品折扣</Text>
                    </div>
                    <Divider style={{ margin: '12px 0' }} />
                    {level.benefits.map((b, j) => (
                      <div key={j} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                        <CheckCircleOutlined style={{ color: '#2c6b4f', fontSize: 13 }} />
                        <Text style={{ fontSize: 13 }}>{b}</Text>
                      </div>
                    ))}
                  </div>
                </Card>
              </motion.div>
            </Col>
          ))}
        </Row>

        {/* Points Activities */}
        <Title level={4} style={{ marginBottom: 20 }}>
          <FireOutlined style={{ color: '#ff6d00', marginRight: 8 }} />积分获取方式
        </Title>
        <Card style={{ borderRadius: 16, border: 'none', marginBottom: 48 }}>
          <Row gutter={[16, 16]}>
            {pointsActivities.map((act, i) => (
              <Col xs={12} md={4} key={i}>
                <div style={{ textAlign: 'center', padding: '16px 8px' }}>
                  <div style={{ fontSize: 24, marginBottom: 8 }}>{act.icon}</div>
                  <Text strong style={{ display: 'block', fontSize: 13 }}>{act.action}</Text>
                  <Tag color="green" style={{ marginTop: 6 }}>{act.points}</Tag>
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* CTA */}
        <Card style={{
          borderRadius: 16, border: 'none', textAlign: 'center',
          background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
        }}>
          <TrophyOutlined style={{ fontSize: 40, color: '#2c6b4f', marginBottom: 12 }} />
          <Title level={4} style={{ color: '#2c6b4f' }}>立即开始赚取积分</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 20 }}>完成问诊、购买商品、每日签到都能获得积分</Text>
          <Space>
            <Button type="primary" size="large" onClick={() => navigate('/diagnosis')} style={{ borderRadius: 10 }}>
              去问诊
            </Button>
            <Button size="large" onClick={() => navigate('/products')} style={{ borderRadius: 10 }}>
              去购物
            </Button>
          </Space>
        </Card>
      </div>
    </div>
  )
}
