from crewai import Crew, Process
from AI_Component.Agents import *
from AI_Component.Tasks import *
from AI_Component.Llms import *
from AI_Component.Tools import WebSearch
from AI_Component.validator.validator import recfon_validator, get_recfon_context_injection

class RecfonAgentChain:
    """
    SEAMEO RECFON QA Chain
    
    Flow: Validation Agent → Fallback → Inject Prompt → Answer Agent
    
    This chain handles the processing of user queries related to SEAMEO RECFON:
    1. Validates if the query is related to SEAMEO RECFON
    2. Applies fallback rules if needed
    3. Injects context into the prompt if the query is RECFON-related
    4. Routes to the appropriate answer agent
    """
    
    def __init__(self, input_query, lang="english", chat_history=""):
        self.input = input_query
        self.lang = lang
        self.chat_history = chat_history
        self.tasks = Tasks(self.input, self.lang)
        self.agents = Agents()
        self.validation_result = None
        
    def validate_query(self):
        """
        Validates if the query is related to SEAMEO RECFON using the validator
        """
        self.validation_result = recfon_validator(self.input, self.chat_history)
        return self.validation_result["is_recfon_context"]
    
    def get_injected_prompt(self):
        """
        Returns the injected prompt if the query is RECFON-related
        """
        if self.validation_result and self.validation_result["is_recfon_context"]:
            return get_recfon_context_injection()
        return ""
    
    def create_recfon_search_task(self):
        """
        Creates a task for searching RECFON-related information
        """
        injected_prompt = self.get_injected_prompt()
        
        return Task(
            description=f"{injected_prompt}\n\nTugas akmu adalah mencari Data seputar informasi SEAMEO RECFON berdasarkan input {self.input} beserta dengan link referensinya"
                        "kamu akan memberikan hasil pencarian mu kepada penulis jawaban"
                        "Kamu akan menggunakan alat [WebSearch]",
            expected_output="sebuah hasil pencarian yang lengkap dari berbagai sumber dengan link sumber nya"
                           " gunakan format yang mudah dipahami untuk bahan menyusun jawaban yang komprehensif",
            agent=self.agents.data_search(),
            tools=[WebSearch]
        )
    
    def create_recfon_answer_task(self):
        """
        Creates a task for answering RECFON-related queries
        """
        injected_prompt = self.get_injected_prompt()
        
        return Task(
            description=f"{injected_prompt}\n\nTugas kamu adalah :"
                        f"Menjawab pertanyaan seputar SEAMEO RECFON berikut : {self.input}"
                        "Menggunakan data yang dicari sebelumnya"
                        "sematkan link referensi yang mendukung jawabanmu dari informasi yang disediakan",
            expected_output="Jawaban dibuat dengan markdown dengan format seperti wikipedia singkat"
                           "Jawaban menyertakan referensi yang bisa dikunjungi di akhir"
                           f"jawaban HARUS Menggunakan bahasa berikut = {self.lang}",
            agent=self.agents.recfon_answer()
        )
    
    def process(self):
        """
        Processes the query through the RECFON agent chain
        """
        # Step 1: Validate if the query is related to SEAMEO RECFON
        is_recfon_context = self.validate_query()
        
        # If not related to RECFON, return None to indicate that this chain shouldn't handle it
        if not is_recfon_context:
            return None
        
        # Step 2: Create the RECFON crew with the appropriate tasks and agents
        recfon_crew = Crew(
            tasks=[self.create_recfon_search_task(), self.create_recfon_answer_task()],
            agents=[self.agents.data_search(), self.agents.recfon_answer()],
            process=Process.sequential,
            manager_llm=openai
        )
        
        # Step 3: Execute the crew and return the result
        return recfon_crew.kickoff()