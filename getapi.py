from androguard.misc import AnalyzeAPK, get_default_session
import os 
import time
import pandas as pd

# Thư mục chứa các file APK
os.chdir('../FileAPK')

# Hàm trích xuất cuộc gọi API từ một tệp APK
def EXTRACT_API_CALLS(apk):
    res = []
    sess = get_default_session()
    app, list_of_dex, dx = AnalyzeAPK(apk, session=sess)
    for method in dx.get_methods():
        for _, call, _ in method.get_xref_to():
            temp_list = call.class_name.split('/')
            if temp_list[0] == "Landroid" and temp_list[1] in ["content", "app", "bluetooth", "location", "media", "net", "nfc", "provider", "telecom", "telephony"]:
                res.append(temp_list[-1] + call.name)
    sess.reset()
    return list(set(res))

# Đọc danh sách API từ tệp Excel
filename = "../apilist.xlsx"
df = pd.read_excel(filename)

# Kiểm tra dữ liệu đã được đọc chính xác chưa
print("Predefined API List:")
print(df.head())

# Tạo một DataFrame trống để lưu kết quả
result_df = pd.DataFrame(columns=df.columns)

# Duyệt qua tất cả các tệp APK trong thư mục
for apk in os.listdir():
    if apk.endswith(".apk"):  # Chỉ xử lý các tệp có phần mở rộng là .apk
        res = []
        start = time.time()
        apkapi = EXTRACT_API_CALLS(apk)
        for api in df.columns:
            if api in apkapi:
                res.append(1)
            else:
                res.append(0)
                
        new_row = pd.Series(res, index=df.columns)
        result_df = pd.concat([result_df, new_row.to_frame().T], ignore_index=True)
        print(f"Processed APK: {apk}, Elapsed Time: {time.time() - start:.2f} seconds")

# Lưu kết quả vào tệp CSV
output_csv = "../apioutput.csv"
result_df.to_csv(output_csv, sep=",", index=True)
print(f"Results saved to: {output_csv}")
