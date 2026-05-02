import streamlit as st
from google import genai
from PIL import Image
import io

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="SafeEat AI - ปลอดภัยเพื่อลูก", page_icon="🛡️")

st.title("🛡️ SafeEat: ผู้ช่วยตรวจเช็กของกินให้ลูกสาว")
st.write("ระบุสิ่งที่แพ้ ถ่ายรูปฉลาก แล้วให้ AI ช่วยตัดสินใจเพื่อความปลอดภัยครับ")

# เชื่อมต่อ API Key 
client = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
    else:
        st.error("❌ ไม่พบ GEMINI_API_KEY ใน Secrets ของ Streamlit")
except Exception as e:
    st.error(f"⚠️ ปัญหาการเชื่อมต่อ API: {e}")

# ส่วนระบุข้อมูลการแพ้
st.markdown("### 📋 ข้อมูลการแพ้อาหาร")
allergy_list = st.text_input(
    "ระบุชื่ออาหารที่แพ้ (แยกด้วยจุลภาค):", 
    value="เม็ดมะม่วงหิมพานต์, อัลมอนด์, วอลนัท",
    help="เช่น ถั่วลิสง, นมวัว, ไข่"
)

target_language = st.selectbox("เลือกภาษาในการแสดงผล:", ["ภาษาไทย", "English"])

# อัปโหลดรูปภาพ
st.markdown("### 📸 ถ่ายรูปฉลากส่วนผสม")
uploaded_file = st.file_uploader("เลือกรูปภาพฉลาก (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and client is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปฉลากที่กำลังตรวจสอบ", use_container_width=True)

    if st.button("🚀 เริ่มวิเคราะห์ความปลอดภัย", type="primary"):
        with st.spinner('⏳ AI กำลังตรวจสอบส่วนผสมอย่างละเอียด...'):
            
            # Prompt 
            prompt = f"""
            You are a Food Safety Expert. 
            Task: Check if this label contains: "{allergy_list}".
            
            Format the output strictly in {target_language}:
            1. **Risk Level**: [Danger] / [Warning] / [Safe]
            2. **Reason**: Short explanation.
            3. **Detected Ingredients**: Summary of main ingredients found.
            
            If the label is in another language, translate to {target_language}.
            """
            
            try:
                # เปลี่ยนรุ่นเป็น 1.5-flash เพื่อเลี่ยงปัญหาโควตาเต็ม (429) ของรุ่น 2.0
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=[prompt, image]
                )
                
                result_text = response.text
                
                # แสดงแถบสีตามความเสี่ยง
                if any(x in result_text for x in ["อันตราย", "Danger", "เสี่ยงสูง"]):
                    st.error("🛑 ผลการวิเคราะห์: พบส่วนผสมที่อันตราย!")
                elif any(x in result_text for x in ["ระวัง", "Warning", "Caution"]):
                    st.warning("⚠️ ผลการวิเคราะห์: มีความเสี่ยงหรือควรระวัง")
                else:
                    st.success("✅ ผลการวิเคราะห์: ไม่พบส่วนผสมที่แพ้")
                
                st.divider()
                st.markdown(result_text)
                st.info("💡 หมายเหตุ: ควรตรวจสอบฉลากด้วยตนเองอีกครั้งเพื่อความแม่นยำสูงสุด")

            except Exception as e:
                # ดักจับ Error 429 (โควตาเต็ม) ให้ชัดเจน
                if "429" in str(e):
                    st.error("🚫 โควตาฟรีของวันนี้หมดแล้วครับ (Google Limit) กรุณาลองใหม่พรุ่งนี้ หรือเปลี่ยน API Key")
                elif "404" in str(e):
                    st.error("🚫 ไม่พบโมเดล (404) กรุณาตรวจสอบว่า API Key รองรับโมเดล gemini-1.5-flash")
                else:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
