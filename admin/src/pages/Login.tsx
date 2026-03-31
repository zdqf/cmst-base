import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message, Typography, Tabs } from 'antd';
import { PhoneOutlined, SafetyOutlined, LockOutlined } from '@ant-design/icons';
import { login, sendSmsCode, adminLogin } from '@/api/auth';
import { setToken } from '@/utils/auth';

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [smsForm] = Form.useForm();
  const [pwdForm] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startCountdown = useCallback(() => {
    setCountdown(60);
    timerRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          if (timerRef.current) clearInterval(timerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  const handleSendCode = async () => {
    try {
      const phone = smsForm.getFieldValue('phone');
      await smsForm.validateFields(['phone']);
      const res = await sendSmsCode(phone);
      const { code, message: msg } = res.data;
      if (code === 0) {
        message.success('验证码已发送');
        startCountdown();
      } else {
        message.error(msg || '发送失败');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.message;
      if (msg) {
        message.error(msg);
      }
    }
  };

  const onSmsLogin = async (values: { phone: string; code: string }) => {
    setLoading(true);
    try {
      const res = await login(values.phone, values.code);
      const { code, message: msg, data } = res.data;
      if (code === 0 && data?.access_token) {
        setToken(data.access_token);
        message.success('登录成功');
        navigate('/');
      } else {
        message.error(msg || '登录失败');
      }
    } catch {
      message.error('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const onPwdLogin = async (values: { phone: string; password: string }) => {
    setLoading(true);
    try {
      const res = await adminLogin(values.phone, values.password);
      const { code, message: msg, data } = res.data;
      if (code === 0 && data?.access_token) {
        setToken(data.access_token);
        message.success('登录成功');
        navigate('/');
      } else {
        message.error(msg || '登录失败');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.message;
      message.error(msg || '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Card style={{ width: 420, borderRadius: 12, boxShadow: '0 8px 32px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3} style={{ marginBottom: 4 }}>草木沈塘</Title>
          <Text type="secondary">管理后台登录</Text>
        </div>
        <Tabs defaultActiveKey="sms" centered items={[
          {
            key: 'sms',
            label: '验证码登录',
            children: (
              <Form form={smsForm} layout="vertical" onFinish={onSmsLogin} autoComplete="off">
                <Form.Item name="phone" rules={[{ required: true, message: '请输入手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]}>
                  <Input prefix={<PhoneOutlined />} placeholder="手机号" size="large" />
                </Form.Item>
                <Form.Item name="code" rules={[{ required: true, message: '请输入验证码' }]}>
                  <Input
                    prefix={<SafetyOutlined />}
                    placeholder="验证码"
                    size="large"
                    suffix={
                      <Button
                        type="link"
                        size="small"
                        disabled={countdown > 0}
                        onClick={handleSendCode}
                        style={{ padding: 0 }}
                      >
                        {countdown > 0 ? `${countdown}秒后重试` : '获取验证码'}
                      </Button>
                    }
                  />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block size="large">登录</Button>
                </Form.Item>
              </Form>
            ),
          },
          {
            key: 'password',
            label: '密码登录',
            children: (
              <Form form={pwdForm} layout="vertical" onFinish={onPwdLogin} autoComplete="off">
                <Form.Item name="phone" rules={[{ required: true, message: '请输入手机号' }, { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]}>
                  <Input prefix={<PhoneOutlined />} placeholder="手机号" size="large" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }, { min: 6, max: 32, message: '密码长度6-32位' }]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" size="large" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block size="large">登录</Button>
                </Form.Item>
              </Form>
            ),
          },
        ]} />
      </Card>
    </div>
  );
};

export default Login;