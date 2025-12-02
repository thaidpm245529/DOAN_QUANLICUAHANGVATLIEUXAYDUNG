import pyodbc

# THÔNG TIN KẾT NỐI
server = r'LAPTOP-N5F015RA\SQLEXPRESS'  #TÊN MÁY CHỦ
database = 'QLVATLIEUXAYDUNG'
username = 'sa'  #TÊN TÀI KHOẢN SQL
password = '240106' #MẬT KHẨU

try:
    # TẠO CHUỖI KẾT NỐI THÔNG QUA DRIVER
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # MỞ KẾT NỐI
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # LỆNH KIỂM THỬ KẾT NỐI NẾU THÀNH CÔNG
    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    print("Kết nối thành công! Phiên bản SQL:", row[0])

    # ĐÓNG KẾT NỐI
    conn.close()
    #KIỂM THỬ KẾT NỐI NẾU THẤT BẠI
except Exception as e:
    print("Lỗi kết nối:", e)
