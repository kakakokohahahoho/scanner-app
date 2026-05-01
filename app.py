import streamlit as st
from google import genai
from PIL import Image

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SafeEat - เครื่องมือสแกนเพื่อลูก", page_icon="🛡️")

st.title("🛡️ SafeEat: ผู้ช่วยตรวจเช็กของกินให้ลูกสาว")
st.write("ระบุสิ่งที่แพ้ ถ่ายรูปฉลาก แล้วให้ AI ช่วยตัดสินใจเพื่อความปลอดภัยครับ")

# เชื่อมต่อ API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.warning(f"⚠️ พบปัญหาการเชื่อมต่อ: {e}")

# ระบุข้อมูลผู้แพ้
st.markdown("### 📋 ข้อมูลการแพ้อาหาร")
allergy_list = st.text_input(
    "ระบุชื่ออาหารที่แพ้ (แยกด้วยจุลภาค):", 
    value="เม็ดมะม่วงหิมพานต์, อัลมอนด์, วอลนัท",
    help="เช่น ถั่วลิสง, นมวัว, ไข่"
)

target_language = st.selectbox("เลือกภาษาในการแสดงผลคำแปล:", ["ภาษาไทย", "English"])

# อัปโหลดรูปภาพ
st.markdown("### 📸 ถ่ายรูปฉลากส่วนผสม")
uploaded_file = st.file_uploader("เลือกรูปภาพฉลาก", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปฉลากที่ตรวจเช็ก", use_container_width=True)

    if st.button("🚀 เริ่มวิเคราะห์ความปลอดภัย", type="primary"):
        with st.spinner('⏳ AI กำลังวิเคราะห์ส่วนผสมอย่างละเอียด...'):
            
            # Prompt ใหม่ที่สั่งให้ AI วิเคราะห์ความปลอดภัยโดยเฉพาะ
            prompt = f"""
            ทำหน้าที่เป็นผู้เชี่ยวชาญด้านความปลอดภัยอาหาร (Food Safety Expert)
            ภารกิจ: ตรวจสอบรูปภาพฉลากนี้ว่ามีส่วนผสมที่ผู้ใช้แพ้คือ "{allergy_list}" หรือไม่
            
            ให้แสดงผลลัพธ์ตามโครงสร้างนี้เท่านั้น (แปลเป็น {target_language}):
            
            1. **ระดับความเสี่ยง**: 
               - [อันตราย] หากพบส่วนผสมที่แพ้โดยตรง
               - [ควรระวัง] หากพบคำเตือนว่า 'อาจมีส่วนผสมของ...' หรือโรงงานผลิตร่วมกับสิ่งที่แพ้
               - [ปลอดภัย] หากไม่พบส่วนผสมที่แพ้เลย
            
            2. **เหตุผล**: อธิบายสั้นๆ ว่าเจออะไร หรือไม่เจออะไร
            
            3. **รายการส่วนผสมที่พบ**: สรุปรายการส่วนผสมหลักที่อ่านได้จากภาพ
            
            หมายเหตุ: หากเป็นภาษาต่างประเทศ ให้แปลเป็น {target_language} ให้ด้วย
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[prompt, image]
                )
                
                # ตกแต่งการแสดงผลตามระดับความเสี่ยง
                result_text = response.text
                if "อันตราย" in result_text or "Danger" in result_text:
                    st.error("🛑 ผลการวิเคราะห์: มีความเสี่ยงสูง")
                elif "ระวัง" in result_text or "Warning" in result_text:
                    st.warning("⚠️ ผลการวิเคราะห์: ควรระมัดระวัง")
                else:
                    st.success("✅ ผลการวิเคราะห์: ไม่พบส่วนผสมที่ระบุว่าแพ้")
                
                st.write("---")
                st.markdown(result_text)
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
