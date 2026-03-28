// ===== 假数据：让页面不再是空壳 =====

import type { HerbListItem, HerbDetail, Product, CartItem, Order, DiagnosisHistoryItem } from '../types'

export const mockHerbs: HerbListItem[] = [
  { id: '1', name: '黄芪', category: '补益药', status: 'active' },
  { id: '2', name: '当归', category: '补益药', status: 'active' },
  { id: '3', name: '枸杞子', category: '补益药', status: 'active' },
  { id: '4', name: '金银花', category: '清热药', status: 'active' },
  { id: '5', name: '菊花', category: '清热药', status: 'active' },
  { id: '6', name: '板蓝根', category: '清热药', status: 'active' },
  { id: '7', name: '麻黄', category: '解表药', status: 'active' },
  { id: '8', name: '桂枝', category: '解表药', status: 'active' },
  { id: '9', name: '陈皮', category: '理气药', status: 'active' },
  { id: '10', name: '木香', category: '理气药', status: 'active' },
  { id: '11', name: '丹参', category: '活血药', status: 'active' },
  { id: '12', name: '川芎', category: '活血药', status: 'active' },
  { id: '13', name: '人参', category: '补益药', status: 'active' },
  { id: '14', name: '白术', category: '补益药', status: 'active' },
  { id: '15', name: '茯苓', category: '补益药', status: 'active' },
  { id: '16', name: '甘草', category: '补益药', status: 'active' },
  { id: '17', name: '连翘', category: '清热药', status: 'active' },
  { id: '18', name: '薄荷', category: '解表药', status: 'active' },
  { id: '19', name: '香附', category: '理气药', status: 'active' },
  { id: '20', name: '红花', category: '活血药', status: 'active' },
]

export const mockHerbDetails: Record<string, HerbDetail> = {
  '1': {
    id: '1', name: '黄芪', category: '补益药', status: 'active',
    origin_and_form: '豆科植物蒙古黄芪或膜荚黄芪的干燥根。主产于内蒙古、山西、甘肃等地。秋季采挖，除去须根和根头，晒干。',
    flavor_meridian: '甘，微温。归肺、脾经。',
    common_pairings: '常与人参、白术、茯苓配伍，用于补气健脾；与当归配伍，用于补气生血。',
    unsuitable_groups: '表实邪盛、气滞湿阻、食积内停、阴虚阳亢者慎用。',
    precautions: '不宜与龟甲、白鲜皮同用。用量一般为9-30g。',
    created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z',
  },
  '2': {
    id: '2', name: '当归', category: '补益药', status: 'active',
    origin_and_form: '伞形科植物当归的干燥根。主产于甘肃、云南、四川等地。秋末采挖，除去须根和泥沙，待水分稍蒸发后捆成小把，上棚，用烟火慢慢熏干。',
    flavor_meridian: '甘、辛，温。归肝、心、脾经。',
    common_pairings: '与黄芪配伍补气生血，与川芎、白芍、熟地黄组成四物汤，为补血调经基础方。',
    unsuitable_groups: '湿盛中满、大便溏泄者慎用。',
    precautions: '用量一般为6-12g。酒当归活血作用增强。',
    created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z',
  },
  '3': {
    id: '3', name: '枸杞子', category: '补益药', status: 'active',
    origin_and_form: '茄科植物宁夏枸杞的干燥成熟果实。主产于宁夏、甘肃、青海等地。夏、秋二季果实呈红色时采收，热风烘干。',
    flavor_meridian: '甘，平。归肝、肾经。',
    common_pairings: '与菊花配伍明目，与熟地黄、山茱萸配伍滋补肝肾。',
    unsuitable_groups: '外邪实热、脾虚有湿及泄泻者慎用。',
    precautions: '用量一般为6-12g。',
    created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z',
  },
}


export const mockProducts: Product[] = [
  { id: 'p1', name: '精选黄芪片 250g', category: '原药材', price: 38.00, specification: '250g/袋', description: '甘肃道地黄芪，精选大片，色泽金黄，质地紧实。适合日常煲汤、泡水。', image_url: null, stock: 200, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p2', name: '宁夏枸杞王 500g', category: '原药材', price: 68.00, specification: '500g/罐', description: '宁夏中宁特级枸杞，颗粒饱满，色泽鲜红，甘甜可口。', image_url: null, stock: 150, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p3', name: '当归头片 200g', category: '原药材', price: 45.00, specification: '200g/袋', description: '甘肃岷县当归头，油性足，香气浓郁，补血佳品。', image_url: null, stock: 100, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p4', name: '金银花茶 100g', category: '简加工产品', price: 32.00, specification: '100g/罐', description: '河南封丘金银花，手工采摘，低温烘干，花蕾完整。', image_url: null, stock: 300, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p5', name: '菊花枸杞茶包 30袋', category: '简加工产品', price: 28.00, specification: '30袋/盒', description: '精选杭白菊与宁夏枸杞科学配比，独立茶包，方便冲泡。', image_url: null, stock: 500, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p6', name: '四物汤料包', category: '调理组合包', price: 58.00, specification: '10包/盒', description: '当归、川芎、白芍、熟地黄经典配方，每包独立包装，方便煎煮。', image_url: null, stock: 80, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p7', name: '补气养血组合', category: '调理组合包', price: 88.00, specification: '7天量/盒', description: '黄芪、当归、党参、大枣科学配比，适合气血两虚人群日常调理。', image_url: null, stock: 60, status: 'active', created_at: '2024-01-01T00:00:00Z' },
  { id: 'p8', name: '陈皮丝 150g', category: '简加工产品', price: 25.00, specification: '150g/袋', description: '广东新会陈皮，陈化三年以上，香气醇厚，理气健脾。', image_url: null, stock: 200, status: 'active', created_at: '2024-01-01T00:00:00Z' },
]

export const mockCartItems: CartItem[] = [
  { id: 'c1', product_id: 'p1', product_name: '精选黄芪片 250g', product_price: 38.00, product_image: '', quantity: 2 },
  { id: 'c2', product_id: 'p5', product_name: '菊花枸杞茶包 30袋', product_price: 28.00, product_image: '', quantity: 1 },
]

export const mockOrders: Order[] = [
  {
    id: 'o1', order_no: 'CMT20240315001', total_amount: 134.00, status: 'completed',
    items: [
      { product_id: 'p1', product_name: '精选黄芪片 250g', quantity: 2, unit_price: 38.00 },
      { product_id: 'p4', product_name: '金银花茶 100g', quantity: 1, unit_price: 32.00 },
      { product_id: 'p5', product_name: '菊花枸杞茶包 30袋', quantity: 1, unit_price: 28.00 },
    ],
    created_at: '2024-03-15T10:30:00Z',
  },
  {
    id: 'o2', order_no: 'CMT20240320002', total_amount: 88.00, status: 'shipped',
    items: [
      { product_id: 'p7', product_name: '补气养血组合', quantity: 1, unit_price: 88.00 },
    ],
    created_at: '2024-03-20T14:20:00Z',
  },
  {
    id: 'o3', order_no: 'CMT20240325003', total_amount: 45.00, status: 'pending',
    items: [
      { product_id: 'p3', product_name: '当归头片 200g', quantity: 1, unit_price: 45.00 },
    ],
    created_at: '2024-03-25T09:15:00Z',
  },
]

export const mockDiagnosisHistory: DiagnosisHistoryItem[] = [
  {
    id: 'd1',
    input_data: { age: 35, gender: '女', symptoms: '近期感觉疲劳乏力，面色偏黄，手脚冰凉', allergies: '无', medications: '无' },
    ai_output: '根据您描述的症状（疲劳乏力、面色偏黄、手脚冰凉），从中医角度分析，可能与气血不足有关。\n\n调理方向建议：\n1. 可考虑补气养血类中药，如黄芪、当归、党参等\n2. 日常可用黄芪大枣泡水代茶饮\n3. 注意保暖，适当运动促进气血运行\n4. 饮食上可多食用红枣、桂圆、山药等温补食材\n\n⚠️ 以上仅为中医调理方向参考，具体用药请咨询专业中医师。',
    created_at: '2024-03-10T08:30:00Z',
  },
  {
    id: 'd2',
    input_data: { age: 28, gender: '男', symptoms: '经常上火，口腔溃疡反复发作，咽喉干痛', allergies: '青霉素过敏', medications: '维生素B族' },
    ai_output: '根据您描述的症状（反复口腔溃疡、咽喉干痛），从中医角度分析，可能与阴虚火旺或胃火上炎有关。\n\n调理方向建议：\n1. 可考虑清热滋阴类中药，如金银花、菊花、麦冬等\n2. 日常可用金银花菊花茶清热降火\n3. 避免辛辣刺激、煎炸食物\n4. 保持充足睡眠，避免熬夜\n\n⚠️ 以上仅为中医调理方向参考，具体用药请咨询专业中医师。',
    created_at: '2024-03-18T15:45:00Z',
  },
]

// 首页统计数据
export const mockStats = {
  herbCount: 200,
  productCount: 56,
  userCount: 1280,
  consultCount: 368,
}

// 健康小贴士
export const healthTips = [
  { title: '春季养生', content: '春季宜养肝，可适当食用枸杞、菊花等，保持心情舒畅。', season: '春' },
  { title: '夏季清热', content: '夏季炎热，可用金银花、菊花泡茶清热解暑，注意补充水分。', season: '夏' },
  { title: '秋季润燥', content: '秋季干燥，可用百合、麦冬、梨等滋阴润燥，保护肺部。', season: '秋' },
  { title: '冬季进补', content: '冬季适合温补，可用黄芪、当归、人参等补气养血。', season: '冬' },
]

// 热门搜索
export const hotSearches = ['黄芪', '枸杞', '当归', '金银花', '人参', '陈皮']
