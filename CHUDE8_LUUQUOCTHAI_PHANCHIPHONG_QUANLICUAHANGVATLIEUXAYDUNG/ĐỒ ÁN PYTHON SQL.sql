
-- 1. TẠO DATABASE
CREATE DATABASE QLVATLIEUXAYDUNG
GO
On (
	name = QLVATLIEUXAYDUNG_mdf,
	filename = 'D:\QLVATLIEUXAYDUNG.mdf',
	size = 10,
	maxsize = 50,
	filegrowth = 5)
Log on (
	name = QLVATLIEUXAYDUNG_log,
	filename = 'D:\QLVATLIEUXAYDUNG.log',
	size = 10,
	maxsize = 50,
	filegrowth = 5)
USE QLVATLIEUXAYDUNG
GO


-- 2. BẢNG TÀI KHOẢN (Phục vụ chức năng Đăng nhập trong Python)
CREATE TABLE TAIKHOAN(
	TENDANGNHAP NVARCHAR(50) NOT NULL PRIMARY KEY,
	MATKHAU NVARCHAR(50) NOT NULL,
	HOTEN NVARCHAR(50),
	QUYEN NVARCHAR(20) DEFAULT 'NHANVIEN' -- Admin hoặc NhanVien
)

-- Thêm tài khoản mẫu để đăng nhập ngay
INSERT INTO TAIKHOAN (TENDANGNHAP, MATKHAU, HOTEN, QUYEN) 
VALUES ('sa', '240106', N'Quản Trị Viên', 'ADMIN')
GO

-- 3. BẢNG KHÁCH HÀNG
CREATE TABLE KHACHHANG(
	MAKH INT IDENTITY(1,1) PRIMARY KEY, -- Tự động tăng ID (1, 2, 3...) cho dễ quản lý
	HOTEN NVARCHAR(100) NOT NULL,
	SDT VARCHAR(15),
	DIACHI NVARCHAR(200),
	GIOITINH NVARCHAR(10) CHECK (GIOITINH IN (N'Nam', N'Nữ', N'Khác'))
)
GO

-- 4. BẢNG VẬT LIỆU (Nguyên liệu đầu vào/bán ra)
CREATE TABLE VATLIEU(
	STT INT,
	MAVL NVARCHAR(20) NOT NULL PRIMARY KEY, -- Cho phép nhập mã tự do (VD: XM01, CAT01)
	TENVL NVARCHAR(100) NOT NULL,
	DONVITINH NVARCHAR(20), -- Thêm đơn vị tính (Bao, Khối, Kg)
	XUATXU NVARCHAR(50),    -- Thay cho NOISX + NGAYSX (Date nên để quản lý lô hàng, ở mức đơn giản thì bỏ qua)
	GIABAN FLOAT DEFAULT 0,
	SOLUONGTON INT DEFAULT 0, -- Quản lý kho trực tiếp tại đây cho đơn giản
	MOTA NVARCHAR(MAX)        -- Mô tả chi tiết
)
GO

-- 5. BẢNG SẢN PHẨM (Hàng thành phẩm)
CREATE TABLE SANPHAM(
	STT INT,
	MASP NVARCHAR(20) NOT NULL PRIMARY KEY,
	TENSP NVARCHAR(100) NOT NULL,
	DONVITINH NVARCHAR(20),
	MAUMA NVARCHAR(50),
	GIABAN FLOAT DEFAULT 0,
	SOLUONGTON INT DEFAULT 0,
	MOTA NVARCHAR(MAX)
)
GO

-- 6. BẢNG HÓA ĐƠN (Lưu thông tin chung của lần giao dịch)
-- Thay thế cho bảng BANHANG cũ
CREATE TABLE HOADON(
	MAHD INT IDENTITY(1,1) PRIMARY KEY,
	MAKH INT, -- Link tới khách hàng
	NGAYLAP DATETIME DEFAULT GETDATE(),
	TONGTIEN FLOAT DEFAULT 0,
	NGUOILAP NVARCHAR(50), -- Link tới TENDANGNHAP của bảng TAIKHOAN
	TRANGTHAI NVARCHAR(50) DEFAULT N'Đã thanh toán',
	
	CONSTRAINT FK_HOADON_KHACHHANG FOREIGN KEY (MAKH) REFERENCES KHACHHANG(MAKH),
	CONSTRAINT FK_HOADON_TAIKHOAN FOREIGN KEY (NGUOILAP) REFERENCES TAIKHOAN(TENDANGNHAP)
)
GO

-- 7. BẢNG CHI TIẾT HÓA ĐƠN (Lưu khách mua món gì, số lượng bao nhiêu)
-- Đây là bảng quan trọng nhất để biết bán cái gì
CREATE TABLE CHITIET_HOADON(
	MACT INT IDENTITY(1,1) PRIMARY KEY,
	MAHD INT NOT NULL,
	
	-- Một dòng chi tiết có thể là Vật liệu HOẶC Sản phẩm
	MAVL NVARCHAR(20) NULL, 
	MASP NVARCHAR(20) NULL,
	
	SOLUONG INT NOT NULL CHECK (SOLUONG > 0),
	DONGIA FLOAT NOT NULL, -- Lưu giá tại thời điểm bán (đề phòng sau này đổi giá)
	THANHTIEN AS (SOLUONG * DONGIA), -- Cột tự động tính toán

	CONSTRAINT FK_CTHD_HOADON FOREIGN KEY (MAHD) REFERENCES HOADON(MAHD),
	CONSTRAINT FK_CTHD_VATLIEU FOREIGN KEY (MAVL) REFERENCES VATLIEU(MAVL),
	CONSTRAINT FK_CTHD_SANPHAM FOREIGN KEY (MASP) REFERENCES SANPHAM(MASP),
	
	-- Ràng buộc: Chỉ được chọn 1 trong 2 (hoặc là Vật liệu, hoặc là Sản phẩm)
	CONSTRAINT CHK_LOAIHANG CHECK (
		(MAVL IS NOT NULL AND MASP IS NULL) OR 
		(MAVL IS NULL AND MASP IS NOT NULL)
	)
)
GO


-- 8. TẠO BẢNG MÃ GIẢM GIÁ
CREATE TABLE MAGIAMGIA(
    CODE NVARCHAR(20) PRIMARY KEY,
    GIAM_PHANTRAM INT DEFAULT 0, -- Giảm theo % (VD: 10 = 10%)
    GIAM_TIEN FLOAT DEFAULT 0,   -- Giảm tiền mặt (VD: 50000)
    TRANGTHAI NVARCHAR(20) DEFAULT 'Active' -- Active / Used / Expired
)
GO

-- 9. VIEW DOANH THU (Thay thế bảng DOANHTHU cũ)
-- Dùng View để tự động tính tổng tiền mà không cần nhập tay
CREATE VIEW V_DOANHTHU AS
SELECT 
	FORMAT(NGAYLAP, 'yyyy-MM') AS THANG,
	COUNT(MAHD) AS SO_DON_HANG,
	SUM(TONGTIEN) AS DOANH_THU
FROM HOADON
GROUP BY FORMAT(NGAYLAP, 'yyyy-MM')
GO

USE QLVATLIEUXAYDUNG
GO

-- =======================================================
-- 1. LÀM SẠCH DỮ LIỆU CŨ (Để tránh lỗi trùng lặp)
-- =======================================================
DELETE FROM CHITIET_HOADON;
DELETE FROM HOADON;
DELETE FROM SANPHAM;
DELETE FROM VATLIEU;
DELETE FROM KHACHHANG;
DELETE FROM TAIKHOAN;

-- Reset lại bộ đếm tự tăng (Identity) về 0 để ID bắt đầu từ 1
DBCC CHECKIDENT ('KHACHHANG', RESEED, 0);
DBCC CHECKIDENT ('HOADON', RESEED, 0);
DBCC CHECKIDENT ('CHITIET_HOADON', RESEED, 0);
GO

-- =======================================================
-- 2. NHẬP BẢNG TÀI KHOẢN (TAIKHOAN)
-- Cấu trúc: TENDANGNHAP, MATKHAU, HOTEN, QUYEN
-- =======================================================
INSERT INTO TAIKHOAN (TENDANGNHAP, MATKHAU, HOTEN, QUYEN) VALUES ('sa', '240106', N'Quản Trị Viên', 'ADMIN');
INSERT INTO TAIKHOAN (TENDANGNHAP, MATKHAU, HOTEN, QUYEN) VALUES ('admin', '123', N'Admin Test', 'ADMIN');
INSERT INTO TAIKHOAN (TENDANGNHAP, MATKHAU, HOTEN, QUYEN) VALUES ('nv01', '1', N'Nguyễn Văn A', 'NHANVIEN');
INSERT INTO TAIKHOAN (TENDANGNHAP, MATKHAU, HOTEN, QUYEN) VALUES ('nv02', '1', N'Trần Thị B', 'NHANVIEN');
GO

-- =======================================================
-- 3. NHẬP BẢNG KHÁCH HÀNG (KHACHHANG)
-- Cấu trúc: HOTEN, SDT, DIACHI, GIOITINH (Check: Nam/Nữ/Khác)
-- =======================================================
INSERT INTO KHACHHANG (HOTEN, SDT, DIACHI, GIOITINH) VALUES (N'Lê Văn Tèo', '0901234567', N'Châu Thành, An Giang', N'Nam');
INSERT INTO KHACHHANG (HOTEN, SDT, DIACHI, GIOITINH) VALUES (N'Nguyễn Thị Nở', '0912345678', N'Long Xuyên, An Giang', N'Nữ');
INSERT INTO KHACHHANG (HOTEN, SDT, DIACHI, GIOITINH) VALUES (N'Trần Văn Búa', '0987654321', N'Thốt Nốt, Cần Thơ', N'Nam');
GO

-- =======================================================
-- 4. NHẬP BẢNG VẬT LIỆU (VATLIEU)
-- Cấu trúc: STT, MAVL, TENVL, DONVITINH, XUATXU, GIABAN, SOLUONGTON, MOTA
-- Lưu ý: Cột XUATXU đúng theo file SQL gốc
-- =======================================================
INSERT INTO VATLIEU (STT, MAVL, TENVL, DONVITINH, XUATXU, GIABAN, SOLUONGTON, MOTA) 
VALUES (1, 'VL01', N'Xi măng Hà Tiên', N'Bao', N'Việt Nam', 90000, 100, N'Xi măng đa dụng PCB40');

INSERT INTO VATLIEU (STT, MAVL, TENVL, DONVITINH, XUATXU, GIABAN, SOLUONGTON, MOTA) 
VALUES (2, 'VL02', N'Cát xây tô', N'Khối', N'Sông Tiền', 250000, 50, N'Cát sạch, hạt mịn');

INSERT INTO VATLIEU (STT, MAVL, TENVL, DONVITINH, XUATXU, GIABAN, SOLUONGTON, MOTA) 
VALUES (3, 'VL03', N'Đá 1x2', N'Khối', N'An Giang', 320000, 40, N'Đá xanh đổ bê tông');

INSERT INTO VATLIEU (STT, MAVL, TENVL, DONVITINH, XUATXU, GIABAN, SOLUONGTON, MOTA) 
VALUES (4, 'VL04', N'Gạch ống', N'Viên', N'Đồng Nai', 1200, 5000, N'Gạch tuynel 4 lỗ');

INSERT INTO VATLIEU (STT, MAVL, TENVL, DONVITINH, XUATXU, GIABAN, SOLUONGTON, MOTA) 
VALUES (5, 'VL05', N'Thép Pomina', N'Cây', N'Việt Nam', 115000, 200, N'Thép phi 10');
GO

-- =======================================================
-- 5. NHẬP BẢNG SẢN PHẨM (SANPHAM)
-- Cấu trúc: STT, MASP, TENSP, DONVITINH, MAUMA, GIABAN, SOLUONGTON, MOTA
-- =======================================================
INSERT INTO SANPHAM (STT, MASP, TENSP, DONVITINH, MAUMA, GIABAN, SOLUONGTON, MOTA) 
VALUES (1, 'SP01', N'Chậu cây cảnh', N'Cái', N'Trắng', 150000, 20, N'Chậu xi măng đúc khuôn');

INSERT INTO SANPHAM (STT, MASP, TENSP, DONVITINH, MAUMA, GIABAN, SOLUONGTON, MOTA) 
VALUES (2, 'SP02', N'Tượng trang trí', N'Cái', N'Xám', 500000, 10, N'Tượng điêu khắc sân vườn');

INSERT INTO SANPHAM (STT, MASP, TENSP, DONVITINH, MAUMA, GIABAN, SOLUONGTON, MOTA) 
VALUES (3, 'SP03', N'Bàn ghế đá', N'Bộ', N'Giả gỗ', 2500000, 5, N'Bộ bàn ghế đá mài');
GO

-- =======================================================
-- 6. NHẬP BẢNG HÓA ĐƠN (HOADON)
-- Cấu trúc: MAKH, NGAYLAP, TONGTIEN, NGUOILAP, TRANGTHAI
-- =======================================================
-- Hóa đơn 1: Khách hàng số 1 (Lê Văn Tèo) mua
INSERT INTO HOADON (MAKH, NGAYLAP, TONGTIEN, NGUOILAP, TRANGTHAI) 
VALUES (1, '2024-12-01', 0, 'sa', N'Đã thanh toán'); -- Tổng tiền sẽ tính sau hoặc update code trigger

-- Hóa đơn 2: Khách hàng số 2 (Nguyễn Thị Nở) mua
INSERT INTO HOADON (MAKH, NGAYLAP, TONGTIEN, NGUOILAP, TRANGTHAI) 
VALUES (2, '2024-12-02', 0, 'nv01', N'Công nợ');
GO

-- =======================================================
-- 7. NHẬP BẢNG CHI TIẾT HÓA ĐƠN (CHITIET_HOADON)
-- Cấu trúc: MAHD, MAVL, MASP, SOLUONG, DONGIA
-- Ràng buộc: Phải chọn hoặc MAVL hoặc MASP, cái còn lại phải NULL
-- =======================================================

-- Chi tiết cho Hóa đơn 1 (Mua Vật liệu)
INSERT INTO CHITIET_HOADON (MAHD, MAVL, MASP, SOLUONG, DONGIA) 
VALUES (1, 'VL01', NULL, 10, 90000); -- Mua 10 bao xi măng

INSERT INTO CHITIET_HOADON (MAHD, MAVL, MASP, SOLUONG, DONGIA) 
VALUES (1, 'VL04', NULL, 1000, 1200); -- Mua 1000 viên gạch

-- Chi tiết cho Hóa đơn 2 (Mua Sản phẩm)
INSERT INTO CHITIET_HOADON (MAHD, MAVL, MASP, SOLUONG, DONGIA) 
VALUES (2, NULL, 'SP01', 2, 150000); -- Mua 2 cái chậu cây

INSERT INTO CHITIET_HOADON (MAHD, MAVL, MASP, SOLUONG, DONGIA) 
VALUES (2, NULL, 'SP03', 1, 2500000); -- Mua 1 bộ bàn ghế đá
GO

-- Cập nhật lại tổng tiền cho bảng HOADON (Tính tổng từ chi tiết)
UPDATE HOADON
SET TONGTIEN = (SELECT SUM(SOLUONG * DONGIA) FROM CHITIET_HOADON WHERE CHITIET_HOADON.MAHD = HOADON.MAHD);
GO
--  THÊM VÀI MÃ MẪU
INSERT INTO MAGIAMGIA (CODE, GIAM_PHANTRAM, TRANGTHAI) VALUES ('XINCHAO', 10, 'Active'); -- Giảm 10%
INSERT INTO MAGIAMGIA (CODE, GIAM_TIEN, TRANGTHAI) VALUES ('TET2025', 100000, 'Active'); -- Giảm 100k
GO

SELECT * FROM KHACHHANG
SELECT * FROM TAIKHOAN
SELECT * FROM VATLIEU
SELECT * FROM SANPHAM
SELECT * FROM HOADON
SELECT * FROM CHITIET_HOADON
