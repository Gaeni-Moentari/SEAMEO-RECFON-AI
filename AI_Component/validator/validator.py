from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()
# Konfigurasi API Key OpenAI
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Prompt Template untuk validasi RECFON
validator_prompt = PromptTemplate(
    input_variables=["question", "chat_history"],
    template=(
        "Kamu adalah Validation Agent - RECFON yang bertugas mendeteksi apakah pertanyaan user berkaitan dengan SEAMEO RECFON.\n\n"
        "Analisis pertanyaan berikut dan tentukan apakah pertanyaan ini berkaitan dengan SEAMEO RECFON (Regional Center for Food and Nutrition).\n\n"
        "Kata kunci yang perlu diperhatikan:\n"
        "- RECFON\n"
        "- regional center\n"
        "- nutrition, gizi\n"
        "- community nutrition, gizi komunitas\n"
        "- research, riset, penelitian\n"
        "- education, pendidikan\n"
        "- training, pelatihan\n"
        "- Indonesia\n"
        "- UI (Universitas Indonesia)\n"
        "- food, makanan\n"
        "- health, kesehatan\n"
        "- Asia, Asia Tenggara\n\n"
        "Konteks implisit yang perlu diperhatikan:\n"
        "- Pertanyaan tentang kegiatan gizi komunitas\n"
        "- Pertanyaan tentang pelatihan regional\n"
        "- Pertanyaan tentang pusat riset nutrisi Asia Tenggara\n\n"
        "Pertanyaan: {question}\n\n"
        "Riwayat chat: {chat_history}\n\n"
        "Jawab dengan format JSON: {{'is_recfon_context': true/false, 'reason': 'alasan singkat'}}"
    ),
)

# Integrasi LLM untuk validasi
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
validator_chain = LLMChain(llm=llm, prompt=validator_prompt)

# Daftar kata kunci untuk rule-based fallback
recfon_keywords = [
    r"recfon",
    r"seameo",
    r"regional center",
    r"pusat regional",
    r"gizi (komunitas|masyarakat)",
    r"nutrition",
    r"nutrisi",
    r"pelatihan (gizi|nutrisi)",
    r"training",
    r"asia tenggara",
    r"southeast asia"
]

# Daftar frasa untuk fallback
fallback_phrases = [
    r"kegiatan apa( saja| aja)?",
    r"program(nya)? apa",
    r"lokasi(nya)? (di|dimana|di mana)",
    r"tujuan(nya)? apa",
    r"fokus(nya)? (ke|kemana|ke mana)",
    r"apa itu (recfon|seameo)",
    r"gizi masyarakat",
    r"pelatihan"
]

# Fungsi untuk rule-based fallback
def check_fallback_rules(question):
    # Konversi ke lowercase untuk case-insensitive matching
    question_lower = question.lower()
    
    # Cek apakah ada frasa fallback dalam pertanyaan
    for phrase in fallback_phrases:
        if re.search(phrase, question_lower):
            # Pastikan tidak ada entitas lain yang aktif
            # Ini adalah simplifikasi, dalam implementasi nyata
            # mungkin perlu cek entitas lain yang sedang aktif
            return True
    
    return False

# Fungsi untuk rule-based keyword matching
def check_recfon_keywords(question):
    # Konversi ke lowercase untuk case-insensitive matching
    question_lower = question.lower()
    
    # Cek apakah ada keyword RECFON dalam pertanyaan
    for keyword in recfon_keywords:
        if re.search(keyword, question_lower):
            return True
    
    return False

# Fungsi Validator
def recfon_validator(question, chat_history=""):
    # Coba deteksi dengan rule-based keyword matching dulu
    if check_recfon_keywords(question):
        return {
            "is_recfon_context": True,
            "reason": "Keyword match",
            "fallback_active": False
        }
    
    # Jika tidak ada keyword, coba dengan LLM
    try:
        response = validator_chain.run(question=question, chat_history=chat_history)
        # Parse JSON response
        import json
        result = json.loads(response)
        result["fallback_active"] = False
        return result
    except Exception as e:
        # Jika LLM gagal atau tidak mengembalikan JSON yang valid
        # Cek dengan rule-based fallback
        if check_fallback_rules(question):
            return {
                "is_recfon_context": True,
                "reason": "Fallback rule match",
                "fallback_active": True
            }
        else:
            # Default fallback jika semua metode gagal
            return {
                "is_recfon_context": False,
                "reason": "No match found",
                "fallback_active": False
            }

# Fungsi untuk mendapatkan prompt injection jika konteks RECFON terdeteksi
def get_recfon_context_injection():
    return """User is asking about SEAMEO RECFON. Answer concisely and based on available information from RECFON, with a focus on nutrition, community health, and Southeast Asian regional collaboration."""
