import type { ThemeConfig } from 'antd'

const theme: ThemeConfig = {
  token: {
    colorPrimary: '#2c6b4f',
    colorSuccess: '#38a169',
    colorWarning: '#dd6b20',
    colorError: '#e53e3e',
    colorInfo: '#3182ce',
    borderRadius: 8,
    fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif`,
    fontSize: 14,
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f5f7f5',
    colorText: '#1a202c',
    colorTextSecondary: '#718096',
    colorBorder: '#e2e8f0',
    controlHeight: 40,
    wireframe: false,
  },
  components: {
    Button: {
      primaryShadow: '0 2px 8px rgba(44, 107, 79, 0.3)',
      borderRadius: 8,
      controlHeight: 40,
      controlHeightLG: 48,
    },
    Card: {
      borderRadiusLG: 12,
      boxShadowTertiary: '0 1px 4px rgba(0,0,0,0.06)',
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Menu: {
      itemBorderRadius: 8,
    },
    Tag: {
      borderRadiusSM: 6,
    },
  },
}

export default theme
