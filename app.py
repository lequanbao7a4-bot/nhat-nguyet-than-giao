import streamlit as st
import json
import os
from google import genai
from google.genai import types

# 1. Cấu hình giao diện trang Web
st.set_page_config(page_title="Nhật Nguyệt Thần Giáo", page_icon="🔥")
st.title("🔥 Nhật Nguyệt Thần Giáo")
st.markdown("*Giáo chủ: Đông Phương Bất Bại*")

# 2. Khởi tạo kết nối AI
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
FILE_LICH_SU = "tri_nho_su_phu.json"

# 3. TRÍ NHỚ NGẦM: Đọc lịch sử cũ để AI không bị mất trí nhớ
if "lich_su_luu_tru" not in st.session_state:
    if os.path.exists(FILE_LICH_SU):
        with open(FILE_LICH_SU, "r", encoding="utf-8") as f:
            st.session_state.lich_su_luu_tru = json.load(f)
    else:
        st.session_state.lich_su_luu_tru = []

# Đưa lịch sử vào form chuẩn của Gemini
lich_su_gemini = []
for item in st.session_state.lich_su_luu_tru:
    lich_su_gemini.append(
        types.Content(role=item["role"], parts=[types.Part.from_text(text=item["text"])])
    )

# 4. MÀN HÌNH HIỂN THỊ: Chỉ lưu trữ các tin nhắn của lần mở web hiện tại
if "tin_nhan_hien_tai" not in st.session_state:
    st.session_state.tin_nhan_hien_tai = []

# 5. Cài đặt tính cách Đông Phương Bất Bại
loi_dan = (
    "Ngươi là Đông Phương Bất Bại của Nhật Nguyệt Thần Giáo, đang truyền thụ kiến thức "
    "bằng phương pháp Socratic Tutor. Hãy đặt câu hỏi gợi mở, tuyệt đối không đưa ngay đáp án cuối cùng. "
    "Xưng là 'bổn tọa', gọi người đối diện là 'ngươi'. "
    "YÊU CẦU QUAN TRỌNG: Khi giảng về vật lý, toán học,và tất cả các khoa học khác HÃY SỬ DỤNG định dạng Markdown và mã LaTeX "
    "(như $$ công thức $$) để trình bày các công thức toán học một cách trực quan, đẹp mắt nhất."
)

cai_dat = types.GenerateContentConfig(system_instruction=loi_dan)
chat = client.chats.create(
    model="gemini-3.8-flash", 
    config=cai_dat, 
    history=lich_su_gemini if lich_su_gemini else None
)

# In câu chào mặc định nếu chưa chat gì trong phiên này
if not st.session_state.tin_nhan_hien_tai:
    with st.chat_message("assistant", avatar="🔥"):
        st.markdown("**Đông Phương Bất Bại:** Kẻ nào dám làm phiền bổn tọa thanh tu? Có chuyện gì cần thỉnh giáo?")

# 6. Chỉ in các tin nhắn MỚI lên màn hình web
for msg in st.session_state.tin_nhan_hien_tai:
    if msg["role"] == "user":
        # Sửa role thành user, icon hình người
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**Khách:** {msg['text']}")
    else:
        # Sửa role thành assistant, icon ngọn lửa
        with st.chat_message("assistant", avatar="🔥"):
            st.markdown(f"**Đông Phương Bất Bại:** {msg['text']}")

# 7. Khung nhập tin nhắn mới
if prompt := st.chat_input("Thỉnh giáo..."):
    # Lưu vào cả 2 nơi: Màn hình và Trí nhớ ngầm
    st.session_state.tin_nhan_hien_tai.append({"role": "user", "text": prompt})
    st.session_state.lich_su_luu_tru.append({"role": "user", "text": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"**Khách:** {prompt}")
    
    # Lấy câu trả lời từ Đông Phương Bất Bại
    with st.chat_message("assistant", avatar="🔥"):
        response = chat.send_message(prompt)
        st.markdown(f"**Đông Phương Bất Bại:** {response.text}")
        
        # Lưu câu trả lời
        st.session_state.tin_nhan_hien_tai.append({"role": "model", "text": response.text})
        st.session_state.lich_su_luu_tru.append({"role": "model", "text": response.text})
        
        # Ghi đè file JSON để AI không bao giờ quên
        with open(FILE_LICH_SU, "w", encoding="utf-8") as f:
            json.dump(st.session_state.lich_su_luu_tru, f, ensure_ascii=False, indent=4)