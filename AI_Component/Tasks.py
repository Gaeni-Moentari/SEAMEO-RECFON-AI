from crewai import Task
from AI_Component.Agents import *
from AI_Component.Tools import *


agents = Agents()

class Tasks:
    def __init__(self, input, lang):
        self.input=input
        self.lang=lang
    
    def general_search_task(self):
        return Task(
            description=f"Tugas akmu adalah mencari Data seputar informasi perikanan berdasarkan input {self.input} beserta dengan link referensinya"
                         "kamu akan memberikan hasil pencarian mu kepada penulis jawaban"
                         "Kamu akan menggunakan alat [WebSearch]",
            expected_output="sebuah hasil pencarian yang lengkap dari berbagai sumber dengan link sumber nya"
                            " gunakan format yang mudah dipahami untuk bahan menyusun jawaban yang komprehensif",
            agent=agents.data_search(),
            tools=[WebSearch]
        )
    
    def general_answer_task(self):
        return Task(
            description="Tugas kamu adalah :"
                        f"Menjawab pertanyaan seputar perikanan berikut : {self.input}"
                        "Menggunakan data yang dicari sebelumnya"
                        "sematkan link referensi yang mendukung jawabanmu dari informasi yang disediakan",
            expected_output="Jawaban dibuat dengan markdown dengan format seperti wikipedia singkat"
                            "Jawaban menyertakan referensi yang bisa dikunjungi di akhir"
                            f"jawaban HARUS Menggunakan bahasa berikut = {self.lang}",
            agent=agents.general_answer()
        )