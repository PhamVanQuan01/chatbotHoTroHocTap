import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import pytesseract
from PIL import Image
import PyPDF2
from docx import Document
# Load biến môi trường từ tệp .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print("API Key Loaded:", api_key)  # Dòng debug để kiểm tra xem khóa API có được tải không

# Cấu hình API của Google Generative AI
genai.configure(api_key=api_key)  # Đọc API key từ biến môi trường

# Cấu hình Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Đường dẫn tới Tesseract

# Cấu hình chatbot
generation_config = {
    "temperature": 0.5,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Khởi tạo trạng thái chat
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "history" not in st.session_state:
    st.session_state.history = []

# Giao diện ứng dụng
st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖", layout="wide")

# Đọc và chèn file CSS
with open("style.css", "r", encoding="utf-8") as f:
    css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


# Tiêu đề trung tâm với hiệu ứng gradient
st.markdown('<h1>Gemini Learning Assist</h1>', unsafe_allow_html=True)

# Các cột, hình ảnh và các phần khác trong ứng dụng


# Sử dụng st.image và đặt ảnh vào các cột với kích thước đã giảm


col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1: st.markdown('<a href="#" class="button-custom">🤖 Assistant</a>', unsafe_allow_html=True)
with col2: st.markdown('<a href="#" class="button-custom">💻 CodeAgent</a>', unsafe_allow_html=True)
with col3: st.markdown('<a href="#" class="button-custom">🔍 Web-Search</a>', unsafe_allow_html=True)
with col4: st.markdown('<a href="#" class="button-custom">➕ More</a>', unsafe_allow_html=True)

# Sidebar với viền xung quanh phần tùy chọn câu hỏi
st.sidebar.markdown("""<div class="sidebar-container"><h3 class="sidebar-title">Tùy chọn câu hỏi</h3>""", unsafe_allow_html=True)

# Chọn kiểu câu hỏi và số lượng câu hỏi bên trong khung có viền
question_type = st.sidebar.radio("Chọn kiểu câu hỏi:", ("Câu hỏi trắc nghiệm", "Câu hỏi tự luận"))
num_questions = st.sidebar.slider("Chọn số lượng câu hỏi", 1, 20, 5)

st.sidebar.markdown("</div>", unsafe_allow_html=True)  # Đóng khung

st.sidebar.divider()

# Tải file
uploaded_file = st.file_uploader("Tải lên file hình ảnh, tài liệu (PDF, Word)", type=["jpg", "jpeg", "png", "pdf", "docx"])

# Khởi tạo biến để chứa văn bản trích xuất
extracted_text = ""

# Xử lý tải file và trích xuất văn bản
if uploaded_file is not None:
    st.success(f"File đã tải lên: {uploaded_file.name}")
    file_type = uploaded_file.type

    try:
        if "image" in file_type:
            image = Image.open(uploaded_file)
            st.image(image, caption="Hình ảnh đã tải lên", use_column_width=True)
            extracted_text = pytesseract.image_to_string(image)

        elif "pdf" in file_type:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            extracted_text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        elif "word" in file_type:
            doc = Document(uploaded_file)
            extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text])

        if extracted_text:
            st.subheader("Văn bản trích xuất:")
            st.write(extracted_text)
        else:
            st.warning("Không có văn bản nào được trích xuất từ file này.")

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {e}")

# Tạo câu hỏi từ văn bản trích xuất
if st.sidebar.button("Tạo câu hỏi") and extracted_text:
    user_input = f"Tạo {num_questions} {'câu hỏi trắc nghiệm' if question_type == 'Câu hỏi trắc nghiệm' else 'câu hỏi tự luận'} từ văn bản sau: {extracted_text}."
    
    response = st.session_state.chat.send_message(user_input)
    st.subheader(f"{question_type}:")
    st.markdown(response.text.replace("\n", "\n\n"))

st.divider()

# Lịch sử trò chuyện
st.sidebar.title("Lịch sử trò chuyện")
if st.session_state.history:
    for message in st.session_state.history:
        st.sidebar.write(message)
        st.sidebar.markdown("---")

# Nhập câu hỏi từ người dùng
user_input = st.chat_input("Nhập câu hỏi của bạn...")
if user_input:
    st.chat_message("user").markdown(user_input)
    response = st.session_state.chat.send_message(user_input)
    st.session_state.history.append(f"User: {user_input}")
    st.session_state.history.append(f"Assistant: {response.text}")
    with st.chat_message("assistant"):
        st.markdown(response.text)