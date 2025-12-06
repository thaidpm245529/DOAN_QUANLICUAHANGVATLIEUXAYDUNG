-- Đặt lại mật khẩu cho sa (ví dụ đặt là 123456)
ALTER LOGIN [sa] WITH PASSWORD=N'240106';

-- Bật tài khoản sa (tránh trường hợp bị Disable)
ALTER LOGIN [sa] ENABLE;