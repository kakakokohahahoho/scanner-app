import streamlit as st
from google import genai
from PIL import Image

#ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="สแกนฉลากอาหาร", page_icon="🔍")

st.title("🔍 แอพสแกนและแปลฉลากอาหาร")
st.write("ถ่ายรูปฉลากหลังซองมาได้เลย!")

#API Key
try:
    api_key = st.secrets["AIzaSyAULsj8QugcEXt-hBnpaT9wafUsZEMCkOE"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.warning(f"⚠️ พบปัญหา: {e}")

#เลือกภาษา
st.markdown("### 🌐 เลือกภาษาที่ต้องการ")

popular_languages = [
    "ภาษาไทย", "English (ภาษาอังกฤษ)", "日本語 (ภาษาญี่ปุ่น)", 
    "한국어 (ภาษาเกาหลี)", "中文 (ภาษาจีน)", "Español (ภาษาสเปน)", 
    "Français (ภาษาฝรั่งเศส)", "Deutsch (ภาษาเยอรมัน)"
]

# ดึงค่าภาษาจาก Dropdown มาใช้งานโดยตรง
target_language = st.selectbox("เลือกจากรายการ:", popular_languages)

# ปุ่มอัปโหลดรูปภาพ
st.markdown("### 📸 อัปโหลดรูปภาพฉลาก")
uploaded_file = st.file_uploader("เลือกรูปภาพของคุณ", type=["jpg", "jpeg", "png"])

# process
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปฉลากที่คุณอัปโหลด", use_container_width=True)

    if st.button("🚀 เริ่มสแกนและแปลผล", type="primary"):
        with st.spinner(f'⏳ กำลังให้ AI ช่วยอ่านและแปลเป็น {target_language}...'):
            
            # ส่งภาษาเป้าหมายเข้าไปในคำสั่ง
            prompt = f"""
ทำหน้าที่เป็นผู้เชี่ยวชาญด้านโภชนาการและนักแปลภาษา
จงอ่านรูปภาพฉลากสินค้านี้ ค้นหาข้อมูลที่เกี่ยวกับ 'ส่วนผสม (Ingredients)' และ 'ข้อมูลสำหรับผู้แพ้อาหาร (Allergen Information)'

จากนั้นให้แปลเฉพาะข้อมูล 2 ส่วนนี้เป็น '{target_language}' โดยมีเงื่อนไขบังคับดังนี้:
1. จัดรูปแบบข้อความให้อ่านง่าย ใช้ตัวหนา (Bold) สำหรับหัวข้อ และใช้ Bullet points สำหรับรายการส่วนผสม
2. ห้ามพิมพ์ข้อความเกริ่นนำ ชวนคุย หรือสรุปใดๆ (เช่น ไม่ต้องพิมพ์ว่า 'ได้เลย นี่คือคำแปล...') ให้แสดงผลเฉพาะข้อมูลเนื้อหาที่แปลแล้วเท่านั้น
3. หากบนฉลากไม่มีข้อมูลผู้แพ้อาหารระบุไว้ ให้ขึ้นข้อความเตือนตัวหนาว่า '⚠️ **ไม่พบข้อมูลผู้แพ้อาหารที่ระบุไว้อย่างชัดเจน โปรดตรวจสอบด้วยความระมัดระวัง**'
"""
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt, image]
                )
                
                st.success(f"✨ ประมวลผลสำเร็จ! (แปลเป็น {target_language})")
                st.write("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
