import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Typography, Button, Statistic, Tag, Carousel, Space } from 'antd'
import {
  ReadOutlined,
  MedicineBoxOutlined,
  MessageOutlined,
  ShopOutlined,
  ExperimentOutlined,
  ArrowRightOutlined,
  FireOutlined,
  HeartOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
  CrownOutlined,
  ThunderboltOutlined,
  StarOutlined,
} from '@ant-design/icons'
import { motion } from 'framer-motion'
import { getDailyHerb } from '../api/herbs'
import { mockHerbs, mockProducts, mockStats, healthTips, hotSearches } from '../mock/data'
import { WaveDecoration, HerbLeafIcon, HerbBagIcon, TeaCupIcon, GiftBoxIcon, BottleIcon } from '../assets/icons'
import type { HerbDetail } from '../types'

const { Title, Text, Paragraph } = Typography

const quickEntries = [
  { label: '本草百科', path: '/herbs', icon: <ReadOutlined style={{ fontSize: 26 }} />, color: '#2c6b4f', bg: '#edf7f0' },
  { label: 'AI 问诊', path: '/diagnosis', icon: <MedicineBoxOutlined style={{ fontSize: 26 }} />, color: '#1565c0', bg: '#e8f0fe' },
  { label: '搭配建议', path: '/pairing', icon: <ExperimentOutlined style={{ fontSize: 26 }} />, color: '#e65100', bg: '#fef0e6' },
  { label: '在线咨询', path: '/consultation', icon: <MessageOutlined style={{ fontSize: 26 }} />, color: '#6a1b9a', bg: '#f5eef8' },
  { label: '药材商城', path: '/products', icon: <ShopOutlined style={{ fontSize: 26 }} />, color: '#c62828', bg: '#fdecea' },
  { label: '会员中心', path: '/membership', icon: <CrownOutlined style={{ fontSize: 26 }} />, color: '#f9a825', bg: '#fef9e7' },
]

const productIcons = [
  <HerbBagIcon style={{ fontSize: 64 }} />,
  <BottleIcon style={{ fontSize: 64 }} />,
  <TeaCupIcon style={{ fontSize: 64 }} />,
  <GiftBoxIcon style={{ fontSize: 64 }} />,
]

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.45, ease: 'easeOut' as const },
  }),
}

const SectionHeader = ({ title, extra }: { title: string; extra?: React.ReactNode }) => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{ width: 3, height: 20, background: '#2c6b4f', borderRadius: 2 }} />
      <Title level={4} style={{ margin: 0, fontSize: 18 }}>{title}</Title>
    </div>
    {extra}
  </div>
)

export default function Home() {
  const navigate = useNavigate()
  const [dailyHerb, setDailyHerb] = useState<HerbDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDailyHerb()
      .then(setDailyHerb)
      .catch(() => {
        setDailyHerb({
          id: '1', name: '黄芪', category: '补益药', status: 'active',
          origin_and_form: '豆科植物蒙古黄芪的干燥根。主产于内蒙古、山西、甘肃等地。秋季采挖，除去须根和根头，晒干。',
          flavor_meridian: '甘，微温。归肺、脾经。',
          common_pairings: '常与人参、白术配伍',
          unsuitable_groups: '表实邪盛者慎用',
          precautions: '用量一般为9-30g',
          created_at: '', updated_at: '',
        })
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      {/* ===== Hero Banner ===== */}
      <div style={{
        background: 'linear-gradient(160deg, #1a3c2e 0%, #2c6b4f 45%, #3d8b6a 100%)',
        padding: '52px 24px 76px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', top: -20, right: '5%', opacity: 0.05, fontSize: 280, color: '#fff' }}>
          <HerbLeafIcon />
        </div>
        <div style={{ position: 'absolute', bottom: -2, left: 0, right: 0, color: '#f8faf8' }}>
          <WaveDecoration style={{ width: '100%', height: 70 }} />
        </div>

        <div style={{ maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <Row gutter={[48, 32]} align="middle">
            <Col xs={24} md={14}>
              <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}>
                <Tag style={{ background: 'rgba(255,255,255,0.12)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', marginBottom: 16, fontSize: 12, padding: '3px 12px', borderRadius: 20 }}>
                  <StarOutlined style={{ marginRight: 4 }} /> 传承千年本草智慧
                </Tag>
                <Title style={{ color: '#fff', fontSize: 40, marginBottom: 12, fontWeight: 800, lineHeight: 1.25, letterSpacing: 1 }}>
                  草木沈塘
                </Title>
                <Paragraph style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16, marginBottom: 28, maxWidth: 480, lineHeight: 1.8 }}>
                  专注传统中药知识科普与优质药材甄选，为您提供专业的中药调理方向参考与品质药材服务。
                </Paragraph>
                <Space size={12} wrap>
                  <Button size="large" icon={<MedicineBoxOutlined />} onClick={() => navigate('/diagnosis')}
                    style={{ height: 46, paddingInline: 28, fontSize: 15, background: '#fff', color: '#2c6b4f', borderColor: '#fff', fontWeight: 600, borderRadius: 10 }}>
                    开始问诊
                  </Button>
                  <Button size="large" ghost icon={<ReadOutlined />} onClick={() => navigate('/herbs')}
                    style={{ height: 46, paddingInline: 28, fontSize: 15, borderColor: 'rgba(255,255,255,0.4)', color: '#fff', borderRadius: 10 }}>
                    探索本草
                  </Button>
                </Space>
              </motion.div>
            </Col>
            <Col xs={24} md={10}>
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 0.2 }}>
                <Row gutter={[12, 12]}>
                  {[
                    { icon: <ReadOutlined />, value: mockStats.herbCount, label: '中药品种', suffix: '+' },
                    { icon: <ShopOutlined />, value: mockStats.productCount, label: '精选商品', suffix: '款' },
                    { icon: <TeamOutlined />, value: mockStats.userCount, label: '服务用户', suffix: '+' },
                    { icon: <HeartOutlined />, value: mockStats.consultCount, label: '咨询服务', suffix: '次' },
                  ].map((stat, i) => (
                    <Col span={12} key={i}>
                      <div style={{
                        background: 'rgba(255,255,255,0.08)',
                        backdropFilter: 'blur(8px)',
                        borderRadius: 14,
                        padding: '18px 14px',
                        textAlign: 'center',
                        border: '1px solid rgba(255,255,255,0.1)',
                      }}>
                        <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 20, marginBottom: 6 }}>{stat.icon}</div>
                        <Statistic value={stat.value} suffix={stat.suffix} valueStyle={{ color: '#fff', fontSize: 26, fontWeight: 700 }} />
                        <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11 }}>{stat.label}</Text>
                      </div>
                    </Col>
                  ))}
                </Row>
              </motion.div>
            </Col>
          </Row>
        </div>
      </div>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
        {/* ===== Quick Entries ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: -36, position: 'relative', zIndex: 2 }}>
          <Card style={{ borderRadius: 16, border: 'none', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' }}
            styles={{ body: { padding: '20px 16px' } }}>
            <Row gutter={[8, 12]} justify="space-around">
              {quickEntries.map((entry, i) => (
                <Col xs={8} sm={4} key={entry.path}>
                  <motion.div custom={i} variants={fadeUp}>
                    <div
                      onClick={() => navigate(entry.path)}
                      style={{ textAlign: 'center', cursor: 'pointer', padding: '8px 0' }}
                    >
                      <div style={{
                        width: 52, height: 52, borderRadius: 14, background: entry.bg,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        margin: '0 auto 8px', color: entry.color,
                        transition: 'transform 0.2s',
                      }}>
                        {entry.icon}
                      </div>
                      <Text style={{ fontSize: 12, fontWeight: 500 }}>{entry.label}</Text>
                    </div>
                  </motion.div>
                </Col>
              ))}
            </Row>
          </Card>
        </motion.div>

        {/* ===== Promo Banner ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: 32 }}>
          <Card
            hoverable
            onClick={() => navigate('/membership')}
            style={{
              borderRadius: 16, border: 'none', overflow: 'hidden',
              background: 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%)',
            }}
            styles={{ body: { padding: '20px 24px' } }}
          >
            <Row align="middle" gutter={16}>
              <Col flex="auto">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <CrownOutlined style={{ color: '#f9a825', fontSize: 20 }} />
                  <Text strong style={{ color: '#e65100', fontSize: 16 }}>新人专享</Text>
                  <Tag color="red" style={{ margin: 0 }}><ThunderboltOutlined /> 限时</Tag>
                </div>
                <Text style={{ color: '#bf360c', fontSize: 13 }}>注册即享 9.8 折优惠 + 免费问诊 1 次 + 128 积分</Text>
              </Col>
              <Col>
                <Button type="primary" style={{ borderRadius: 20, background: '#e65100', borderColor: '#e65100' }}>
                  立即领取 <ArrowRightOutlined />
                </Button>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* ===== Daily Herb ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: 40 }}>
          <SectionHeader title="今日草本推荐" extra={
            <Button type="link" onClick={() => navigate('/herbs')} style={{ fontSize: 13 }}>查看全部 <ArrowRightOutlined /></Button>
          } />
          <Card
            hoverable
            onClick={() => dailyHerb && navigate(`/herbs/${dailyHerb.id}`)}
            style={{ borderRadius: 16, overflow: 'hidden', border: 'none' }}
          >
            <Row gutter={24} align="middle">
              <Col xs={24} md={8}>
                <div style={{
                  background: 'linear-gradient(135deg, #edf7f0 0%, #d4edda 100%)',
                  borderRadius: 12, padding: 28, textAlign: 'center', minHeight: 170,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                }}>
                  <HerbLeafIcon style={{ fontSize: 56, color: '#2c6b4f', marginBottom: 10 }} />
                  <Title level={3} style={{ color: '#1a3c2e', margin: 0 }}>
                    {loading ? '...' : (dailyHerb?.name || '黄芪')}
                  </Title>
                  <Tag color="green" style={{ marginTop: 8 }}>{dailyHerb?.category || '补益药'}</Tag>
                </div>
              </Col>
              <Col xs={24} md={16}>
                <div style={{ padding: '4px 0' }}>
                  <Title level={4} style={{ marginBottom: 8 }}>
                    {dailyHerb?.name || '黄芪'} · {dailyHerb?.category || '补益药'}
                  </Title>
                  <Paragraph type="secondary" style={{ marginBottom: 10, lineHeight: 1.8, fontSize: 13 }}>
                    {dailyHerb?.origin_and_form || '豆科植物蒙古黄芪的干燥根。主产于内蒙古、山西等地。'}
                  </Paragraph>
                  <Space size={[6, 6]} wrap>
                    <Tag color="processing">{dailyHerb?.flavor_meridian?.slice(0, 15) || '甘，微温。归肺、脾经'}</Tag>
                    <Tag color="default" style={{ cursor: 'pointer' }}>点击查看详情 →</Tag>
                  </Space>
                </div>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* ===== Health Tips ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: 40 }}>
          <SectionHeader title="养生小贴士" />
          <Carousel autoplay autoplaySpeed={5000} dots={{ className: 'custom-dots' }}>
            {healthTips.map((tip, i) => (
              <div key={i}>
                <Card style={{
                  borderRadius: 16, border: 'none', margin: '0 2px',
                  background: i % 2 === 0 ? 'linear-gradient(135deg, #edf7f0 0%, #d4edda 100%)' : 'linear-gradient(135deg, #fef9e7 0%, #fef0e6 100%)',
                }}>
                  <Row align="middle" gutter={20}>
                    <Col flex="72px">
                      <div style={{
                        width: 56, height: 56, borderRadius: 16,
                        background: 'rgba(255,255,255,0.7)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 26,
                      }}>
                        {tip.season === '春' ? '🌸' : tip.season === '夏' ? '☀️' : tip.season === '秋' ? '🍂' : '❄️'}
                      </div>
                    </Col>
                    <Col flex="auto">
                      <Title level={5} style={{ marginBottom: 2 }}>{tip.title}</Title>
                      <Text type="secondary" style={{ fontSize: 13 }}>{tip.content}</Text>
                    </Col>
                  </Row>
                </Card>
              </div>
            ))}
          </Carousel>
        </motion.div>

        {/* ===== Hot Herbs ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: 40 }}>
          <SectionHeader title="热门中药" extra={
            <Button type="link" onClick={() => navigate('/herbs')} style={{ fontSize: 13 }}>更多 <ArrowRightOutlined /></Button>
          } />
          <Row gutter={[12, 12]}>
            {mockHerbs.slice(0, 8).map((herb, i) => {
              const hue = [142, 160, 180, 200, 120, 90, 280, 320][i % 8]
              return (
                <Col xs={12} sm={8} md={6} lg={3} key={herb.id}>
                  <motion.div custom={i} variants={fadeUp}>
                    <Card hoverable onClick={() => navigate(`/herbs/${herb.id}`)}
                      style={{ borderRadius: 12, border: 'none' }}
                      styles={{ body: { padding: 12 } }}>
                      <div style={{
                        height: 80, borderRadius: 8, marginBottom: 10,
                        background: `linear-gradient(135deg, hsl(${hue}, 35%, 93%) 0%, hsl(${hue}, 40%, 87%) 100%)`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        <HerbLeafIcon style={{ fontSize: 36, color: `hsl(${hue}, 40%, 38%)` }} />
                      </div>
                      <Text strong style={{ display: 'block', fontSize: 13, marginBottom: 2 }}>{herb.name}</Text>
                      <Tag color="green" style={{ fontSize: 10, lineHeight: '18px', padding: '0 6px' }}>{herb.category}</Tag>
                    </Card>
                  </motion.div>
                </Col>
              )
            })}
          </Row>
        </motion.div>

        {/* ===== Hot Products ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: 40 }}>
          <SectionHeader title="精选好物" extra={
            <Button type="link" onClick={() => navigate('/products')} style={{ fontSize: 13 }}>更多 <ArrowRightOutlined /></Button>
          } />
          <Row gutter={[12, 12]}>
            {mockProducts.slice(0, 4).map((product, i) => (
              <Col xs={12} sm={8} md={6} key={product.id}>
                <motion.div custom={i} variants={fadeUp}>
                  <Card hoverable onClick={() => navigate(`/products/${product.id}`)}
                    style={{ borderRadius: 12, border: 'none' }}
                    styles={{ body: { padding: 12 } }}>
                    <div style={{
                      height: 110, borderRadius: 8, marginBottom: 10,
                      background: 'linear-gradient(135deg, #fafbfa 0%, #f0f2f0 100%)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      {productIcons[i % productIcons.length]}
                    </div>
                    <Text strong style={{ display: 'block', fontSize: 13, marginBottom: 2 }} ellipsis>{product.name}</Text>
                    <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 6 }}>{product.specification}</Text>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
                      <Text style={{ color: '#c62828', fontSize: 11 }}>¥</Text>
                      <Text style={{ color: '#c62828', fontSize: 20, fontWeight: 700, lineHeight: 1 }}>{product.price.toFixed(0)}</Text>
                    </div>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>
        </motion.div>

        {/* ===== Hot Searches ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ marginTop: 40 }}>
          <SectionHeader title="热门搜索" />
          <Space size={[8, 8]} wrap>
            {hotSearches.map((kw, i) => (
              <Tag key={kw} onClick={() => navigate('/herbs')}
                style={{ cursor: 'pointer', padding: '5px 16px', borderRadius: 20, fontSize: 13, background: i === 0 ? '#edf7f0' : undefined, color: i === 0 ? '#2c6b4f' : undefined }}>
                {i === 0 && <FireOutlined style={{ marginRight: 4, color: '#ff6d00' }} />}
                {kw}
              </Tag>
            ))}
          </Space>
        </motion.div>

        {/* ===== Trust ===== */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} style={{ margin: '40px 0 32px' }}>
          <Card style={{ borderRadius: 16, border: 'none', background: 'linear-gradient(135deg, #edf7f0 0%, #d4edda 100%)' }}
            styles={{ body: { padding: '28px 24px' } }}>
            <Row gutter={[24, 20]} justify="center">
              {[
                { icon: <SafetyCertificateOutlined style={{ fontSize: 28, color: '#2c6b4f' }} />, title: '品质保障', desc: '严选道地药材' },
                { icon: <MedicineBoxOutlined style={{ fontSize: 28, color: '#2c6b4f' }} />, title: '专业科普', desc: '中医师团队审核' },
                { icon: <HeartOutlined style={{ fontSize: 28, color: '#2c6b4f' }} />, title: '用心服务', desc: '一对一咨询' },
                { icon: <TeamOutlined style={{ fontSize: 28, color: '#2c6b4f' }} />, title: '千人信赖', desc: '1280+ 用户选择' },
              ].map((item, i) => (
                <Col xs={12} md={6} key={i} style={{ textAlign: 'center' }}>
                  <motion.div custom={i} variants={fadeUp}>
                    {item.icon}
                    <Title level={5} style={{ marginTop: 6, marginBottom: 2, fontSize: 14 }}>{item.title}</Title>
                    <Text type="secondary" style={{ fontSize: 11 }}>{item.desc}</Text>
                  </motion.div>
                </Col>
              ))}
            </Row>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
