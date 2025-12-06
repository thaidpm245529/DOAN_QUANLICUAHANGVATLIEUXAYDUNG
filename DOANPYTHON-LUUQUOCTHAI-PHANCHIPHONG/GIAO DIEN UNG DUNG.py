import customtkinter as ctk
from tkinter import ttk, messagebox
import pyodbc
from PIL import Image, ImageTk

# =============================================================================
# CẤU HÌNH KẾT NỐI DATABASE
# =============================================================================
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'LAPTOP-N5F015RA\SQLEXPRESS',  # <--- HÃY THAY TÊN SERVER CỦA BẠN VÀO ĐÂY (VD: DESKTOP-ABC\SQLEXPRESS)
    'database': 'QLVATLIEUXAYDUNG',
    'uid': 'sa',
    'pwd': '240106'
}


class Database:
    def __init__(self):
        self.conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']}"
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.conn_str)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối SQL Server:\n{e}")
            return False

    def query(self, sql, params=()):
        if not self.conn: self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)
            if sql.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.conn.commit()
                return True
        except Exception as e:
            messagebox.showerror("Lỗi SQL", str(e))
            return None


db = Database()


# =============================================================================
# MÀN HÌNH ĐĂNG NHẬP (GIAO DIỆN MỚI THEO THIẾT KẾ)
# =============================================================================
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập hệ thống")
        self.geometry("700x450")
        self.resizable(False, False)

        # Cấu hình màu sắc chủ đạo theo thiết kế (Trắng/Đen)
        self.configure(fg_color="#F0F0F0")  # Màu nền xám nhạt như hình

        # 1. Logo/Badge góc trái trên (CỬA HÀNG VẬT LIỆU XÂY DỰNG)
        self.badge_frame = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="black", corner_radius=0)
        self.badge_frame.place(x=0, y=10)  # Vị trí sát góc trái

        ctk.CTkLabel(self.badge_frame, text=" CỬA HÀNG VẬT LIỆU XÂY DỰNG ",
                     font=("Arial", 12), text_color="black").pack(padx=10, pady=5)

        # 2. Tiêu đề lớn (ĐĂNG NHẬP HỆ THỐNG)
        self.lbl_title = ctk.CTkLabel(self, text="ĐĂNG NHẬP HỆ THỐNG",
                                      font=("Arial", 26), text_color="black")
        self.lbl_title.pack(pady=(60, 30))  # Khoảng cách từ trên xuống

        # 3. Form nhập liệu (Căn chỉnh Label và Entry thẳng hàng)
        self.frame_form = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_form.pack(pady=10)

        # -- Dòng 1: Tên tài khoản --
        ctk.CTkLabel(self.frame_form, text="Tên tài khoản", font=("Arial", 14), text_color="black", anchor="w").grid(
            row=0, column=0, padx=20, pady=15, sticky="w")

        self.entry_user = ctk.CTkEntry(self.frame_form, width=300, height=40,
                                       border_width=2, border_color="black",  # Viền đen đậm
                                       fg_color="white", text_color="black", corner_radius=0)
        self.entry_user.grid(row=0, column=1, padx=0, pady=15)

        # -- Dòng 2: Mật khẩu --
        ctk.CTkLabel(self.frame_form, text="Mật khẩu", font=("Arial", 14), text_color="black", anchor="w").grid(row=1,
                                                                                                                column=0,
                                                                                                                padx=20,
                                                                                                                pady=15,
                                                                                                                sticky="w")

        self.entry_pass = ctk.CTkEntry(self.frame_form, width=300, height=40,
                                       border_width=2, border_color="black",  # Viền đen đậm
                                       fg_color="white", text_color="black", show="*", corner_radius=0)
        self.entry_pass.grid(row=1, column=1, padx=0, pady=15)

        # 4. Các tùy chọn (Xem mật khẩu - Quên mật khẩu)
        self.frame_opts = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opts.pack(fill="x", padx=140)  # Căn lề để khớp với form ở trên

        # Checkbox Xem mật khẩu (bên trái)
        self.chk_show = ctk.CTkCheckBox(self.frame_opts, text="Xem mật khẩu",
                                        text_color="black", border_color="black", fg_color="black",
                                        command=self.toggle_password, font=("Arial", 12))
        self.chk_show.pack(side="left")

        # Label Quên mật khẩu (bên phải)
        self.lbl_forgot = ctk.CTkLabel(self.frame_opts, text="☐ Quên mật khẩu",
                                       text_color="black", font=("Arial", 12))
        self.lbl_forgot.pack(side="right")

        # 5. Nút Đăng nhập (Màu đen, bo góc)
        self.btn_login = ctk.CTkButton(self, text="ĐĂNG NHẬP", width=300, height=50,
                                       fg_color="black", hover_color="#333",  # Màu đen như thiết kế
                                       font=("Arial", 16, "bold"), corner_radius=10,
                                       command=self.check_login)
        self.btn_login.pack(pady=40)

        # Bind phím Enter để đăng nhập nhanh
        self.bind('<Return>', lambda event: self.check_login())

    def toggle_password(self):
        # Hàm ẩn/hiện mật khẩu khi tích vào checkbox
        if self.chk_show.get() == 1:
            self.entry_pass.configure(show="")
        else:
            self.entry_pass.configure(show="*")

    def check_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if not db.connect(): return

        # Kiểm tra tài khoản trong DB
        result = db.query("SELECT * FROM TAIKHOAN WHERE TENDANGNHAP=? AND MATKHAU=?", (username, password))

        if result:
            self.destroy()
            # Mở màn hình chính và truyền thông tin user
            app = MainWindow(user_info=result[0])
            app.mainloop()
        else:
            messagebox.showerror("Thất bại", "Sai tên đăng nhập hoặc mật khẩu!")



# =============================================================================
# MÀN HÌNH CHÍNH (MAIN WINDOW)
# =============================================================================
class MainWindow(ctk.CTk):
    def __init__(self, user_info):
        super().__init__()
        self.title("Phần mềm Quản lý Vật liệu Xây dựng")
        self.geometry("1200x700")
        self.user_info = user_info

        # --- HEADER MENU ---
        self.frame_menu = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.frame_menu.pack(side="top", fill="x")

        buttons = ["Quản lý nguyên vật liệu", "Quản lý sản phẩm", "Quản lý doanh thu", "Đề xuất và thanh toán"]
        self.btn_tabs = {}
        for btn_text in buttons:
            btn = ctk.CTkButton(self.frame_menu, text=btn_text, width=180, fg_color="transparent", text_color="black",
                                hover_color="#ddd", border_width=1, border_color="gray",
                                command=lambda t=btn_text: self.show_tab(t))
            btn.pack(side="left", padx=5, pady=5)
            self.btn_tabs[btn_text] = btn

        # --- BODY CONTENT ---
        self.frame_content = ctk.CTkFrame(self)
        self.frame_content.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Khởi tạo các view (nhưng chưa hiển thị)
        self.view_dexuat = ProposalAndPaymentView(self.frame_content)
        self.view_vatlieu = MaterialView(self.frame_content)
        self.view_sanpham = ProductView(self.frame_content)
        self.view_banhang = SalesView(self.frame_content)

        # Mặc định hiện tab đầu tiên
        self.show_tab("Quản lý nguyên vật liệu")

    def show_tab(self, tab_name):
        # Ẩn tất cả các view
        for widget in self.frame_content.winfo_children():
            widget.pack_forget()

        # Highlight nút đang chọn
        for btn in self.btn_tabs.values():
            btn.configure(fg_color="transparent")
        self.btn_tabs[tab_name].configure(fg_color="#ccc")

        # Hiển thị view tương ứng
        if tab_name == "Quản lý nguyên vật liệu":
            self.view_vatlieu.pack(fill="both", expand=True)
            self.view_vatlieu.load_data()
        elif tab_name == "Quản lý sản phẩm":
            self.view_sanpham.pack(fill="both", expand=True)
            self.view_sanpham.load_data()
        elif tab_name == "Quản lý doanh thu":
            self.view_banhang.pack(fill="both", expand=True)
        elif tab_name == "Đề xuất và thanh toán":
            self.view_dexuat.pack(fill="both", expand=True)
            self.view_dexuat.load_invoices()


# =============================================================================
# VIEW: QUẢN LÝ VẬT LIỆU (Giống hình 1 & 4)
# =============================================================================
class MaterialView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e6e6e6")

        # --- Cột trái: Danh sách ---
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(self.left_frame, text="DANH SÁCH NGUYÊN VẬT LIỆU", font=("Arial", 18, "bold")).pack(pady=10)

        # Thanh tìm kiếm
        search_frame = ctk.CTkFrame(self.left_frame, fg_color="white", border_width=1)
        search_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(search_frame, text="🔍").pack(side="left", padx=5)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Tìm kiếm vật liệu...", border_width=0,
                                         fg_color="white", width=300)
        self.entry_search.pack(side="left", fill="x", expand=True)
        self.entry_search.bind("<Return>", self.search_data)

        # Bảng (Treeview)
        cols = ("STT", "Mã VL", "Tên Vật Liệu", "Giá Bán", "Tồn Kho")
        self.tree = ttk.Treeview(self.left_frame, columns=cols, show="headings", height=20)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- Cột phải: Thông tin chi tiết ---
        self.right_frame = ctk.CTkFrame(self, width=350, fg_color="white", border_width=1, border_color="black")
        self.right_frame.pack(side="right", fill="y", padx=5, pady=5)
        self.right_frame.pack_propagate(False)  # Cố định kích thước

        ctk.CTkLabel(self.right_frame, text="THÔNG TIN CHI TIẾT", font=("Arial", 16, "bold"), fg_color="#ccc",
                     corner_radius=0).pack(fill="x", pady=(0, 20), ipady=10)

        # Các trường nhập liệu
        self.entries = {}
        fields = [("MÃ VẬT LIỆU", "MAVL"), ("TÊN VẬT LIỆU", "TENVL"), ("SỐ LƯỢNG TỒN", "SOLUONGTON"),
                  ("XUẤT XỨ", "XUATXU"), ("ĐƠN VỊ TÍNH", "DONVITINH"), ("GIÁ BÁN", "GIABAN")]

        for label_text, key in fields:
            f = ctk.CTkFrame(self.right_frame, fg_color="transparent")
            f.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(f, text=label_text + ":", width=100, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(f, height=30)
            entry.pack(side="right", fill="x", expand=True)
            self.entries[key] = entry

        # Nút chức năng
        btn_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="Thêm", width=80, command=self.add_data).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Sửa", width=80, command=self.update_data).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Xóa", width=80, fg_color="red", command=self.delete_data).pack(side="left",
                                                                                                      padx=5)
        ctk.CTkButton(btn_frame, text="Làm mới", width=60, fg_color="gray", command=self.clear_form).pack(side="left",
                                                                                                          padx=5)

    def load_data(self):
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Lấy dữ liệu từ SQL
        rows = db.query("SELECT STT, MAVL, TENVL, GIABAN, SOLUONGTON, DONVITINH, XUATXU FROM VATLIEU")
        if rows:
            for row in rows:
                # Format giá tiền
                price = "{:,.0f}".format(row[3])
                self.tree.insert("", "end", values=(row[0], row[1], row[2], price, row[4], row[5],
                                                    row[6]))  # Lưu ẩn các cột phụ nếu cần

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0], 'values')
        # values: STT(0), MAVL(1), TENVL(2), GIABAN(3), SL(4), DVT(5), XX(6) (Note: Treeview lưu text)

        # Để lấy chính xác, nên query lại theo MAVL hoặc map đúng index (ở đây map tạm theo thứ tự insert)
        # Cần query lại full info vì treeview có thể không hiện hết hoặc format số
        mavl = values[1]
        data = db.query("SELECT * FROM VATLIEU WHERE MAVL=?", (mavl,))
        if data:
            row = data[0]
            # row: STT, MAVL, TENVL, DVT, XUATXU, GIABAN, SL, MOTA
            self.set_entry("MAVL", row[1])
            self.set_entry("TENVL", row[2])
            self.set_entry("DONVITINH", row[3])
            self.set_entry("XUATXU", row[4])
            self.set_entry("GIABAN", int(row[5]))
            self.set_entry("SOLUONGTON", row[6])

    def set_entry(self, key, value):
        self.entries[key].delete(0, "end")
        self.entries[key].insert(0, str(value))

    def get_entry(self, key):
        return self.entries[key].get()

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.load_data()

    def search_data(self, event=None):
        keyword = self.entry_search.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = f"SELECT STT, MAVL, TENVL, GIABAN, SOLUONGTON, DONVITINH, XUATXU FROM VATLIEU WHERE TENVL LIKE N'%{keyword}%' OR MAVL LIKE '%{keyword}%'"
        rows = db.query(query)
        if rows:
            for row in rows:
                price = "{:,.0f}".format(row[3])
                self.tree.insert("", "end", values=(row[0], row[1], row[2], price, row[4], row[5], row[6]))

    def add_data(self):
        # 1. Tính toán STT mới tự động
        # Lấy số STT lớn nhất hiện tại trong bảng VATLIEU
        res = db.query("SELECT MAX(STT) FROM VATLIEU")
        # Nếu chưa có gì thì là 0, nếu có rồi thì lấy số đó
        current_max = res[0][0] if res and res[0][0] is not None else 0
        new_stt = current_max + 1

        # 2. Thực hiện lệnh INSERT có thêm cột STT
        sql = "INSERT INTO VATLIEU (STT, MAVL, TENVL, SOLUONGTON, XUATXU, DONVITINH, GIABAN) VALUES (?, ?, ?, ?, ?, ?, ?)"

        # Nhớ thêm new_stt vào đầu danh sách tham số (params)
        params = (new_stt,
                  self.get_entry("MAVL"),
                  self.get_entry("TENVL"),
                  self.get_entry("SOLUONGTON"),
                  self.get_entry("XUATXU"),
                  self.get_entry("DONVITINH"),
                  self.get_entry("GIABAN"))

        if db.query(sql, params):
            messagebox.showinfo("Thành công", f"Đã thêm vật liệu mới (STT: {new_stt})!")
            self.load_data()
            # Xóa form sau khi thêm để tránh ấn nhầm
            self.clear_form()

    def update_data(self):
        sql = "UPDATE VATLIEU SET TENVL=?, SOLUONGTON=?, XUATXU=?, DONVITINH=?, GIABAN=? WHERE MAVL=?"
        params = (self.get_entry("TENVL"), self.get_entry("SOLUONGTON"), self.get_entry("XUATXU"),
                  self.get_entry("DONVITINH"), self.get_entry("GIABAN"), self.get_entry("MAVL"))
        if db.query(sql, params):
            messagebox.showinfo("Thành công", "Cập nhật thành công!")
            self.load_data()

    def delete_data(self):
        mavl = self.get_entry("MAVL")
        if not mavl: return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa vật liệu này?"):
            if db.query("DELETE FROM VATLIEU WHERE MAVL=?", (mavl,)):
                messagebox.showinfo("Đã xóa", "Xóa thành công!")
                self.clear_form()


# =============================================================================
# VIEW: QUẢN LÝ SẢN PHẨM (Tương tự Vật liệu)
# =============================================================================
class ProductView(MaterialView):
    # Kế thừa từ MaterialView vì giao diện y hệt, chỉ đổi tên bảng và cột SQL
    def __init__(self, parent):
        super().__init__(parent)
        # Sửa lại tiêu đề và các trường input cho phù hợp Sản phẩm
        for widget in self.left_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == "DANH SÁCH NGUYÊN VẬT LIỆU":
                widget.configure(text="DANH SÁCH SẢN PHẨM")

        # Thay đổi Label các entry cho khớp bảng SANPHAM (Có thêm Mẫu mã)
        # Ở đây dùng lại khung sườn, chỉ override hàm SQL
        pass

    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = db.query("SELECT STT, MASP, TENSP, GIABAN, SOLUONGTON, DONVITINH, MAUMA FROM SANPHAM")
        if rows:
            for row in rows:
                price = "{:,.0f}".format(row[3])
                self.tree.insert("", "end", values=(row[0], row[1], row[2], price, row[4], row[5], row[6]))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0], 'values')
        masp = values[1]
        data = db.query("SELECT * FROM SANPHAM WHERE MASP=?", (masp,))
        if data:
            row = data[0]
            # Map dữ liệu vào Entry (Key của entry đang là MAVL, TENVL.. tái sử dụng UI cũ)
            self.set_entry("MAVL", row[1])  # MASP
            self.set_entry("TENVL", row[2])  # TENSP
            self.set_entry("DONVITINH", row[3])
            self.set_entry("XUATXU", row[4])  # MAUMA (Dùng chung ô Entry XUATXU để hiển thị Mẫu mã cho tiện)
            self.set_entry("GIABAN", int(row[5]))
            self.set_entry("SOLUONGTON", row[6])

    def add_data(self):
        # 1. Tính toán STT mới cho Sản phẩm
        res = db.query("SELECT MAX(STT) FROM SANPHAM")
        current_max = res[0][0] if res and res[0][0] is not None else 0
        new_stt = current_max + 1

        # 2. Insert vào SANPHAM
        sql = "INSERT INTO SANPHAM (STT, MASP, TENSP, SOLUONGTON, MAUMA, DONVITINH, GIABAN) VALUES (?, ?, ?, ?, ?, ?, ?)"

        # Lưu ý: ProductView dùng ô XUATXU để nhập MAUMA (như code cũ)
        params = (new_stt,
                  self.get_entry("MAVL"),  # Đây là MASP
                  self.get_entry("TENVL"),  # Đây là TENSP
                  self.get_entry("SOLUONGTON"),
                  self.get_entry("XUATXU"),  # Đây là MAUMA
                  self.get_entry("DONVITINH"),
                  self.get_entry("GIABAN"))

        if db.query(sql, params):
            messagebox.showinfo("Thành công", f"Đã thêm sản phẩm mới (STT: {new_stt})!")
            self.load_data()
            self.clear_form()

    def update_data(self):
        sql = "UPDATE SANPHAM SET TENSP=?, SOLUONGTON=?, MAUMA=?, DONVITINH=?, GIABAN=? WHERE MASP=?"
        params = (self.get_entry("TENVL"), self.get_entry("SOLUONGTON"), self.get_entry("XUATXU"),
                  self.get_entry("DONVITINH"), self.get_entry("GIABAN"), self.get_entry("MAVL"))
        if db.query(sql, params):
            messagebox.showinfo("Thành công", "Cập nhật sản phẩm thành công!")
            self.load_data()

    def delete_data(self):
        masp = self.get_entry("MAVL")
        if messagebox.askyesno("Xác nhận", "Xóa sản phẩm này?"):
            if db.query("DELETE FROM SANPHAM WHERE MASP=?", (masp,)):
                messagebox.showinfo("Đã xóa", "Thành công!")
                self.clear_form()


# =============================================================================
# =============================================================================
# VIEW: DOANH THU BÁN HÀNG (ĐÃ NÂNG CẤP)
# =============================================================================
class SalesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#bbb")

        ctk.CTkLabel(self, text="DOANH THU BÁN HÀNG (LẬP HÓA ĐƠN)", font=("Arial", 20, "bold")).pack(pady=10)

        # 1. Thông tin khách hàng
        frame_kh = ctk.CTkFrame(self, border_width=1, border_color="gray", fg_color="white")
        frame_kh.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_kh, text="Thông tin khách hàng", font=("Arial", 12, "bold")).grid(row=0, column=0,
                                                                                             sticky="w", padx=10,
                                                                                             pady=5)
        self.entry_tenkh = self.create_input(frame_kh, "Tên khách hàng:", 1, 0)
        self.entry_sdt = self.create_input(frame_kh, "Số điện thoại:", 2, 0)
        self.entry_diachi = self.create_input(frame_kh, "Địa chỉ:", 2, 1)

        # 2. Nhập sản phẩm vào giỏ (Đã nâng cấp)
        frame_add = ctk.CTkFrame(self, border_width=1, border_color="gray", fg_color="#e1e1e1")
        frame_add.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame_add, text="Thêm hàng vào đơn", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w",
                                                                                           padx=10, pady=5)

        # Ô nhập Mã hoặc Tên
        ctk.CTkLabel(frame_add, text="Mã hoặc Tên SP:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_masp = ctk.CTkEntry(frame_add, width=200, placeholder_text="VD: VL01 hoặc Xi măng")
        self.entry_masp.grid(row=1, column=1, padx=5, pady=5)
        self.entry_masp.bind("<Return>", lambda e: self.add_to_cart())  # Nhấn Enter để thêm ngay

        # Nút tra cứu nhanh
        btn_search = ctk.CTkButton(frame_add, text="🔍", width=40, command=self.open_product_list)
        btn_search.grid(row=1, column=2, padx=5)

        # Ô nhập số lượng
        ctk.CTkLabel(frame_add, text="Số lượng:").grid(row=1, column=3, padx=10, pady=5, sticky="e")
        self.entry_soluong = ctk.CTkEntry(frame_add, width=100)
        self.entry_soluong.grid(row=1, column=4, padx=5, pady=5)
        self.entry_soluong.insert(0, "1")  # Mặc định số lượng là 1
        self.entry_soluong.bind("<Return>", lambda e: self.add_to_cart())

        # Nút Thêm
        btn_add = ctk.CTkButton(frame_add, text="THÊM VÀO ĐƠN", command=self.add_to_cart, fg_color="#005b96")
        btn_add.grid(row=1, column=5, padx=20, pady=10)

        # 3. Bảng chi tiết hóa đơn
        self.tree_cart = ttk.Treeview(self, columns=("Mã", "Tên", "ĐVT", "SL", "Đơn Giá", "Thành Tiền"),
                                      show="headings", height=10)
        for col in ("Mã", "Tên", "ĐVT", "SL", "Đơn Giá", "Thành Tiền"):
            self.tree_cart.heading(col, text=col)
            if col in ["Tên"]:
                self.tree_cart.column(col, width=250)
            else:
                self.tree_cart.column(col, width=100, anchor="center")

        self.tree_cart.pack(fill="both", expand=True, padx=10, pady=5)

        # 4. Thanh toán
        frame_bot = ctk.CTkFrame(self, fg_color="transparent")
        frame_bot.pack(fill="x", padx=10, pady=10)

        self.lbl_total = ctk.CTkLabel(frame_bot, text="TỔNG TIỀN: 0 VNĐ", font=("Arial", 20, "bold"), text_color="red")
        self.lbl_total.pack(side="left", padx=10)

        btn_pay = ctk.CTkButton(frame_bot, text="THANH TOÁN & LƯU", fg_color="green", height=40, width=200,
                                command=self.checkout)
        btn_pay.pack(side="right")

        self.cart_items = []

    def create_input(self, parent, label, r, c):
        ctk.CTkLabel(parent, text=label).grid(row=r, column=c * 2, padx=10, pady=5, sticky="e")
        entry = ctk.CTkEntry(parent, width=200)
        entry.grid(row=r, column=c * 2 + 1, padx=10, pady=5)
        return entry

    def open_product_list(self):
        # Tạo cửa sổ con (Popup) để chọn hàng
        top = ctk.CTkToplevel(self)
        top.title("Tra cứu Sản phẩm / Vật liệu")
        top.geometry("600x400")
        top.transient(self)  # Giữ cửa sổ con trên cùng

        # Thanh tìm kiếm trong popup
        entry_search_pop = ctk.CTkEntry(top, placeholder_text="Nhập tên để tìm...")
        entry_search_pop.pack(fill="x", padx=10, pady=10)

        # Bảng danh sách
        cols = ("Mã", "Tên", "ĐVT", "Giá", "Tồn")
        tree_pop = ttk.Treeview(top, columns=cols, show="headings")
        for c in cols:
            tree_pop.heading(c, text=c)
            tree_pop.column(c, width=80)
        tree_pop.column("Tên", width=200)
        tree_pop.pack(fill="both", expand=True, padx=10, pady=10)

        # Hàm load dữ liệu vào popup
        def load_pop_data(keyword=""):
            for i in tree_pop.get_children(): tree_pop.delete(i)
            # Tìm trong VL
            rows_vl = db.query(
                f"SELECT MAVL, TENVL, DONVITINH, GIABAN, SOLUONGTON FROM VATLIEU WHERE TENVL LIKE N'%{keyword}%' OR MAVL LIKE '%{keyword}%'")
            if rows_vl:
                for r in rows_vl: tree_pop.insert("", "end", values=(r[0], r[1], r[2], int(r[3]), r[4]))
            # Tìm trong SP
            rows_sp = db.query(
                f"SELECT MASP, TENSP, DONVITINH, GIABAN, SOLUONGTON FROM SANPHAM WHERE TENSP LIKE N'%{keyword}%' OR MASP LIKE '%{keyword}%'")
            if rows_sp:
                for r in rows_sp: tree_pop.insert("", "end", values=(r[0], r[1], r[2], int(r[3]), r[4]))

        load_pop_data()
        entry_search_pop.bind("<KeyRelease>", lambda e: load_pop_data(entry_search_pop.get()))

        # Sự kiện click chọn
        def on_double_click(event):
            sel = tree_pop.selection()
            if sel:
                val = tree_pop.item(sel[0], "values")
                self.entry_masp.delete(0, "end")
                self.entry_masp.insert(0, val[0])  # Điền mã vào ô chính
                top.destroy()
                self.entry_soluong.focus()  # Chuyển con trỏ sang ô số lượng

        tree_pop.bind("<Double-1>", on_double_click)

    def add_to_cart(self):
        input_str = self.entry_masp.get().strip()
        qty_str = self.entry_soluong.get().strip()

        if not input_str or not qty_str:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã/Tên và Số lượng!")
            return

        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên dương!")
            return

        # 1. Tìm trong Vật liệu (Ưu tiên tìm chính xác Mã trước, sau đó tìm Tên gần đúng)
        res = db.query("SELECT MAVL, TENVL, DONVITINH, GIABAN FROM VATLIEU WHERE MAVL = ?", (input_str,))
        item_type = "VL"

        if not res:  # Nếu không trùng mã, tìm theo Tên
            res = db.query(f"SELECT MAVL, TENVL, DONVITINH, GIABAN FROM VATLIEU WHERE TENVL LIKE N'%{input_str}%'")

        # 2. Nếu vẫn chưa thấy, tìm trong Sản phẩm
        if not res:
            res = db.query("SELECT MASP, TENSP, DONVITINH, GIABAN FROM SANPHAM WHERE MASP = ?", (input_str,))
            item_type = "SP"
            if not res:
                res = db.query(f"SELECT MASP, TENSP, DONVITINH, GIABAN FROM SANPHAM WHERE TENSP LIKE N'%{input_str}%'")

        # Xử lý kết quả
        if res:
            if len(res) > 1:
                messagebox.showinfo("Tìm thấy nhiều kết quả",
                                    "Có nhiều sản phẩm trùng tên, vui lòng dùng nút 🔍 để chọn chính xác!")
                self.open_product_list()  # Mở popup để chọn
                return

            row = res[0]
            # row: [MÃ, TÊN, ĐVT, GIÁ]
            price = int(row[3])
            total_line = price * qty

            # Thêm vào UI
            self.tree_cart.insert("", "end", values=(row[0], row[1], row[2], qty, "{:,.0f}".format(price),
                                                     "{:,.0f}".format(total_line)))

            # Thêm vào List dữ liệu
            self.cart_items.append({
                "type": item_type, "code": row[0], "qty": qty, "price": price
            })

            # Cập nhật tổng tiền
            self.update_total_label()

            # Reset ô nhập để nhập tiếp món sau nhanh hơn
            self.entry_masp.delete(0, "end")
            self.entry_soluong.delete(0, "end")
            self.entry_soluong.insert(0, "1")
            self.entry_masp.focus()
        else:
            messagebox.showerror("Không tìm thấy", f"Không tìm thấy sản phẩm nào có mã hoặc tên: '{input_str}'")

    def update_total_label(self):
        total = sum(item['qty'] * item['price'] for item in self.cart_items)
        self.lbl_total.configure(text=f"TỔNG TIỀN: {total:,.0f} VNĐ")

    def checkout(self):
        if not self.cart_items:
            messagebox.showwarning("Giỏ hàng trống", "Chưa có sản phẩm nào để thanh toán!")
            return

        ten_kh = self.entry_tenkh.get() or "Khách vãng lai"
        sdt = self.entry_sdt.get()

        # Insert KH và Hóa đơn (Logic giữ nguyên)
        if db.query("INSERT INTO KHACHHANG (HOTEN, SDT, GIOITINH) VALUES (?, ?, N'Khác')", (ten_kh, sdt)):
            kh_id = db.query("SELECT MAX(MAKH) FROM KHACHHANG")[0][0]

            # Tạo hóa đơn
            tong_tien = sum(item['qty'] * item['price'] for item in self.cart_items)
            db.query("INSERT INTO HOADON (MAKH, NGUOILAP, TONGTIEN) VALUES (?, ?, ?)",
                     (kh_id, self.master.master.user_info[0], tong_tien))
            mahd = db.query("SELECT MAX(MAHD) FROM HOADON")[0][0]

            # Lưu chi tiết
            for item in self.cart_items:
                col_name = "MAVL" if item['type'] == 'VL' else "MASP"
                # Cẩn thận cú pháp SQL động
                if item['type'] == 'VL':
                    db.query("INSERT INTO CHITIET_HOADON (MAHD, MAVL, SOLUONG, DONGIA) VALUES (?, ?, ?, ?)",
                             (mahd, item['code'], item['qty'], item['price']))
                else:
                    db.query("INSERT INTO CHITIET_HOADON (MAHD, MASP, SOLUONG, DONGIA) VALUES (?, ?, ?, ?)",
                             (mahd, item['code'], item['qty'], item['price']))

            messagebox.showinfo("Thanh toán thành công", f"Đã lưu hóa đơn #{mahd}\nTổng cộng: {tong_tien:,.0f} VNĐ")

            # Reset form
            self.cart_items = []
            for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
            self.update_total_label()
            self.entry_tenkh.delete(0, "end")
            self.entry_sdt.delete(0, "end")
            self.entry_diachi.delete(0, "end")

# =============================================================================
# =============================================================================
# VIEW: ĐỀ XUẤT VÀ THANH TOÁN
# =============================================================================
class ProposalAndPaymentView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e6e6e6")

        # Layout 2 cột
        self.grid_columnconfigure(0, weight=4)  # Cột trái (Lịch sử) nhỏ hơn chút
        self.grid_columnconfigure(1, weight=6)  # Cột phải (POS) rộng hơn

        # CỘT TRÁI: LỊCH SỬ (CRM)
        self.left_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # CỘT PHẢI: POS (THANH TOÁN)
        self.right_frame = ctk.CTkFrame(self, fg_color="#F4F4F4", corner_radius=10, border_width=1, border_color="#ccc")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.cart_items = []
        self.selected_invoice_id = None
        self.discount_percent = 0
        self.discount_cash = 0

        self.setup_left_ui()
        self.setup_right_ui()

    # =========================================================================
    # PHẦN 1: GIAO DIỆN BÊN TRÁI
    # =========================================================================
    def setup_left_ui(self):
        ctk.CTkLabel(self.left_frame, text="LỊCH SỬ GIAO DỊCH", font=("Arial", 16, "bold"), text_color="#333").pack(
            pady=10)

        # Tìm kiếm
        search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10)
        self.entry_search_hd = ctk.CTkEntry(search_frame, placeholder_text="Tìm tên khách...")
        self.entry_search_hd.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(search_frame, text="Tìm", width=60, command=self.load_invoices, fg_color="#555").pack(side="left",
                                                                                                            padx=5)

        # Bảng Hóa đơn
        cols = ("Mã HĐ", "Khách", "Ngày", "Tổng Tiền")
        self.tree_hd = ttk.Treeview(self.left_frame, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree_hd.heading(c, text=c)
            if c == "Khách":
                self.tree_hd.column(c, width=110)
            else:
                self.tree_hd.column(c, width=70)
        self.tree_hd.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_hd.bind("<<TreeviewSelect>>", self.on_select_invoice)

        # Nút chuyển đổi
        self.btn_transfer = ctk.CTkButton(self.left_frame, text="➡️ SAO CHÉP SANG ĐƠN MỚI",
                                          fg_color="#E65100", state="disabled", command=self.transfer_to_cart)
        self.btn_transfer.pack(fill="x", padx=20, pady=10)

        # Gợi ý
        ctk.CTkLabel(self.left_frame, text="Gợi ý thông minh:", font=("Arial", 12, "bold"), anchor="w").pack(fill="x",
                                                                                                             padx=10)
        self.txt_suggestion = ctk.CTkTextbox(self.left_frame, height=80, fg_color="#FFF3E0", text_color="#333")
        self.txt_suggestion.pack(fill="x", padx=10, pady=5)

    # =========================================================================
    # PHẦN 2: GIAO DIỆN BÊN PHẢI
    # =========================================================================
    def setup_right_ui(self):
        ctk.CTkLabel(self.right_frame, text="THANH TOÁN ĐƠN HÀNG", font=("Arial", 16, "bold"),
                     text_color="#00695C").pack(pady=10)

        # 1. Thông tin khách
        info_frame = ctk.CTkFrame(self.right_frame, fg_color="white")
        info_frame.pack(fill="x", padx=10)
        self.entry_kh_new = ctk.CTkEntry(info_frame, placeholder_text="Tên khách hàng")
        self.entry_kh_new.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry_sdt_new = ctk.CTkEntry(info_frame, placeholder_text="SĐT", width=120)
        self.entry_sdt_new.pack(side="left", padx=5)

        # 2. Thêm hàng
        add_frame = ctk.CTkFrame(self.right_frame, fg_color="#E0F2F1")
        add_frame.pack(fill="x", padx=10, pady=5)
        self.entry_masp = ctk.CTkEntry(add_frame, placeholder_text="Nhập Mã/Tên SP...")
        self.entry_masp.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        self.entry_masp.bind("<Return>", lambda e: self.manual_add_to_cart())

        self.entry_soluong = ctk.CTkEntry(add_frame, width=60)
        self.entry_soluong.insert(0, "1")
        self.entry_soluong.pack(side="left", padx=5)
        self.entry_soluong.bind("<Return>", lambda e: self.manual_add_to_cart())

        ctk.CTkButton(add_frame, text="✚ Thêm", width=60, command=self.manual_add_to_cart, fg_color="#00796B").pack(
            side="left", padx=5)

        # 3. Giỏ hàng
        cols = ("Mã", "Tên Hàng", "SL", "Đơn Giá", "Thành Tiền")
        self.tree_cart = ttk.Treeview(self.right_frame, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree_cart.heading(c, text=c)
            if c == "Tên Hàng":
                self.tree_cart.column(c, width=140)
            else:
                self.tree_cart.column(c, width=70)
        self.tree_cart.pack(fill="both", expand=True, padx=10, pady=5)

        # CRUD Buttons
        crud_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        crud_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(crud_frame, text="✏️ Sửa SL", width=80, fg_color="#F9A825", command=self.edit_cart_item).pack(
            side="left", padx=2)
        ctk.CTkButton(crud_frame, text="🗑️ Xóa món", width=80, fg_color="#C62828", command=self.delete_cart_item).pack(
            side="left", padx=2)
        ctk.CTkButton(crud_frame, text="🧹 Xóa hết", width=80, fg_color="gray", command=self.clear_cart_ui).pack(
            side="right", padx=2)

        # =====================================================================
        # KHU VỰC ĐÁY (BOT_FRAME): KHUYẾN MÃI (TRÁI) & THANH TOÁN (PHẢI)
        # =====================================================================
        self.bot_frame = ctk.CTkFrame(self.right_frame, fg_color="white", border_width=2, border_color="#ddd")
        self.bot_frame.pack(fill="x", padx=10, pady=10, ipady=5)

        # --- CỘT TRÁI CỦA BOT: KHUYẾN MÃI ---
        promo_frame = ctk.CTkFrame(self.bot_frame, fg_color="transparent")
        promo_frame.pack(side="left", fill="y", padx=10, pady=5)

        ctk.CTkLabel(promo_frame, text="🎫 Mã Giảm Giá / Voucher", font=("Arial", 12, "bold")).pack(anchor="w")

        # Dùng Combobox để gợi ý mã
        self.combo_coupon = ctk.CTkComboBox(promo_frame, width=150, values=["Đang tải..."])
        self.combo_coupon.pack(pady=5)

        btn_apply = ctk.CTkButton(promo_frame, text="Áp dụng", width=150, fg_color="#F57F17", command=self.apply_coupon)
        btn_apply.pack(pady=2)

        self.lbl_discount_info = ctk.CTkLabel(promo_frame, text="Chưa dùng mã", text_color="gray", font=("Arial", 11))
        self.lbl_discount_info.pack()

        # Đường kẻ dọc phân cách
        ctk.CTkFrame(self.bot_frame, width=2, fg_color="#ccc").pack(side="left", fill="y", padx=5, pady=5)

        # --- CỘT PHẢI CỦA BOT: TỔNG TIỀN & CHECKOUT ---
        pay_frame = ctk.CTkFrame(self.bot_frame, fg_color="transparent")
        pay_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        self.lbl_total = ctk.CTkLabel(pay_frame, text="0 VNĐ", font=("Arial", 26, "bold"), text_color="red")
        self.lbl_total.pack(pady=(5, 10))

        ctk.CTkButton(pay_frame, text="THANH TOÁN NGAY", height=45, width=200,
                      fg_color="green", font=("Arial", 14, "bold"), hover_color="#006400",
                      command=self.checkout).pack()

        # Tự động load danh sách mã khi khởi động
        self.load_active_coupons()

    # =========================================================================
    # LOGIC XỬ LÝ
    # =========================================================================
    def load_active_coupons(self):
        # Lấy danh sách mã Active từ DB để gợi ý vào Combobox
        rows = db.query("SELECT CODE FROM MAGIAMGIA WHERE TRANGTHAI='Active'")
        if rows:
            codes = [r[0] for r in rows]
            self.combo_coupon.configure(values=codes)
            self.combo_coupon.set("Chọn mã...")
        else:
            self.combo_coupon.configure(values=[])
            self.combo_coupon.set("Không có mã")

    def apply_coupon(self):
        code = self.combo_coupon.get().strip()  # Lấy từ combobox
        if not code or code == "Chọn mã...": return

        res = db.query("SELECT GIAM_PHANTRAM, GIAM_TIEN FROM MAGIAMGIA WHERE CODE=? AND TRANGTHAI='Active'", (code,))
        if res:
            self.discount_percent = res[0][0]
            self.discount_cash = res[0][1]
            desc = f"-{self.discount_percent}%" if self.discount_percent > 0 else f"-{self.discount_cash:,.0f}đ"

            self.lbl_discount_info.configure(text=f"Đã dùng: {code} ({desc})", text_color="green")
            messagebox.showinfo("Thành công", f"Đã áp dụng mã {code}!")
            self.update_total_label()
        else:
            messagebox.showerror("Lỗi", "Mã không hợp lệ hoặc hết hạn!")
            self.discount_percent = 0
            self.discount_cash = 0
            self.lbl_discount_info.configure(text="Mã lỗi", text_color="red")
            self.update_total_label()

    # --- Các hàm logic khác (Load Invoice, Transfer, Add to Cart, Checkout...)

    def load_invoices(self):
        for i in self.tree_hd.get_children(): self.tree_hd.delete(i)
        keyword = self.entry_search_hd.get()
        rows = db.query("""SELECT H.MAHD, K.HOTEN, H.NGAYLAP, H.TONGTIEN
                           FROM HOADON H
                                    JOIN KHACHHANG K ON H.MAKH = K.MAKH
                           WHERE K.HOTEN LIKE ?
                           ORDER BY H.MAHD DESC""", (f'%{keyword}%',))
        if rows:
            for r in rows:
                d = r[2].strftime("%d/%m") if r[2] else ""
                self.tree_hd.insert("", "end", values=(r[0], r[1], d, "{:,.0f}".format(r[3])))

    def on_select_invoice(self, event):
        sel = self.tree_hd.selection()
        if not sel: return
        self.selected_invoice_id = self.tree_hd.item(sel[0], "values")[0]
        self.btn_transfer.configure(state="normal", text=f"➡️ SAO CHÉP ĐƠN #{self.selected_invoice_id}")
        # Gợi ý đơn giản
        items = [r[0].lower() for r in db.query(
            "SELECT CASE WHEN CT.MAVL IS NOT NULL THEN V.TENVL ELSE S.TENSP END FROM CHITIET_HOADON CT LEFT JOIN VATLIEU V ON CT.MAVL = V.MAVL LEFT JOIN SANPHAM S ON CT.MASP = S.MASP WHERE CT.MAHD = ?",
            (self.selected_invoice_id,))]
        txt = "Gợi ý:\n" + ("- Mua thêm Cát?" if any("xi măng" in i for i in items) and not any(
            "cát" in i for i in items) else "- Đơn ổn.")
        self.txt_suggestion.configure(state="normal");
        self.txt_suggestion.delete("1.0", "end");
        self.txt_suggestion.insert("end", txt);
        self.txt_suggestion.configure(state="disabled")

    def transfer_to_cart(self):
        if not self.selected_invoice_id: return
        self.clear_cart_ui()
        details = db.query("SELECT MAVL, MASP, SOLUONG FROM CHITIET_HOADON WHERE MAHD = ?", (self.selected_invoice_id,))
        if details:
            for r in details: self.add_item_logic(r[0] if r[0] else r[1], r[2])
            self.entry_kh_new.delete(0, "end")
            self.entry_kh_new.insert(0, self.tree_hd.item(self.tree_hd.selection()[0], "values")[1])

    def manual_add_to_cart(self):
        code = self.entry_masp.get();
        try:
            qty = int(self.entry_soluong.get())
        except:
            return
        if self.add_item_logic(code, qty):
            self.entry_masp.delete(0, "end");
            self.entry_soluong.delete(0, "end");
            self.entry_soluong.insert(0, "1")

    def add_item_logic(self, code, qty):
        res = db.query("SELECT MAVL, TENVL, GIABAN, SOLUONGTON FROM VATLIEU WHERE MAVL=? OR TENVL LIKE ?", (code, code))
        itype = "VL"
        if not res:
            res = db.query("SELECT MASP, TENSP, GIABAN, SOLUONGTON FROM SANPHAM WHERE MASP=? OR TENSP LIKE ?",
                           (code, code))
            itype = "SP"
        if res:
            r = res[0]
            if qty > r[3]: messagebox.showwarning("Kho", f"Chỉ còn {r[3]} {r[1]}"); return False
            price = int(r[2]);
            total = price * qty
            self.tree_cart.insert("", "end", values=(r[0], r[1], qty, "{:,.0f}".format(price), "{:,.0f}".format(total)))
            self.cart_items.append({"type": itype, "code": r[0], "qty": qty, "price": price})
            self.update_total_label();
            return True
        return False

    def edit_cart_item(self):
        sel = self.tree_cart.selection()
        if sel:
            d = ctk.CTkInputDialog(text="Số lượng:", title="Sửa")
            v = d.get_input()
            if v and v.isdigit():
                idx = self.tree_cart.index(sel[0])
                self.cart_items[idx]['qty'] = int(v)
                self.tree_cart.item(sel[0], values=(self.tree_cart.item(sel[0], "values")[0],
                                                    self.tree_cart.item(sel[0], "values")[1], v,
                                                    self.tree_cart.item(sel[0], "values")[3],
                                                    "{:,.0f}".format(self.cart_items[idx]['price'] * int(v))))
                self.update_total_label()

    def delete_cart_item(self):
        sel = self.tree_cart.selection()
        if sel and messagebox.askyesno("Xóa", "Xóa món này?"):
            del self.cart_items[self.tree_cart.index(sel[0])]
            self.tree_cart.delete(sel[0])
            self.update_total_label()

    def clear_cart_ui(self):
        self.cart_items = [];
        for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
        self.update_total_label()

    def update_total_label(self):
        raw = sum(i['qty'] * i['price'] for i in self.cart_items)
        disc = raw * (self.discount_percent / 100) if self.discount_percent > 0 else self.discount_cash
        fin = max(0, raw - disc)
        self.lbl_total.configure(text=f"{fin:,.0f} VNĐ")
        return fin

    def checkout(self):
        if not self.cart_items: return
        total = self.update_total_label()
        kh = self.entry_kh_new.get() or "Khách lẻ"
        db.query("INSERT INTO KHACHHANG (HOTEN, SDT) VALUES (?, ?)", (kh, self.entry_sdt_new.get()))
        kid = db.query("SELECT MAX(MAKH) FROM KHACHHANG")[0][0]
        db.query("INSERT INTO HOADON (MAKH, NGUOILAP, TONGTIEN) VALUES (?, ?, ?)", (kid, 'sa', total))
        hid = db.query("SELECT MAX(MAHD) FROM HOADON")[0][0]
        for i in self.cart_items:
            col = "MAVL" if i['type'] == 'VL' else "MASP";
            tbl = "VATLIEU" if i['type'] == 'VL' else "SANPHAM"
            db.query(f"INSERT INTO CHITIET_HOADON (MAHD, {col}, SOLUONG, DONGIA) VALUES (?, ?, ?, ?)",
                     (hid, i['code'], i['qty'], i['price']))
            db.query(f"UPDATE {tbl} SET SOLUONGTON = SOLUONGTON - ? WHERE {col} = ?", (i['qty'], i['code']))
        messagebox.showinfo("Xong", f"Thanh toán HĐ #{hid}\nĐã trừ kho.");
        self.clear_cart_ui()
# =============================================================================
# CHẠY ỨNG DỤNG
# =============================================================================
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    app = LoginWindow()
    app.mainloop()