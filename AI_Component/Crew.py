from crewai import Crew, Process
from AI_Component.Agents import *
from AI_Component.Tasks import *
from AI_Component.Llms import *
from AI_Component.recfon_agent_chain import RecfonAgentChain
from AI_Component.validator.validator import recfon_validator

class RecfonCrew:
    def __init__(self, input, lang, chat_history=""):
        self.input = input
        self.lang = lang
        self.chat_history = chat_history
        self.tasks = Tasks(self.input, self.lang)
        self.agents = Agents()

    def generalCrew(self):
        """
        General crew for handling all types of queries.
        For RECFON-specific queries, it will use the RECFON QA Chain.
        For other queries, it will use the general nutrition crew.
        """
        # First, check if this is a RECFON-related query
        validation_result = recfon_validator(self.input, self.chat_history)
        
        if validation_result["is_recfon_context"]:
            # If it's RECFON-related, use the RECFON QA Chain
            recfon_chain = RecfonAgentChain(self.input, self.lang, self.chat_history)
            result = recfon_chain.process()
            
            # If the RECFON chain processed the query successfully, return the result
            if result:
                return result
        
        # If it's not RECFON-related or the RECFON chain didn't process it,
        # fall back to the general nutrition crew
        task = self.tasks
        agent = self.agents
        crew = Crew(
            tasks=[task.general_search_task(), task.general_answer_task()],
            agents=[agent.data_search(), agent.general_answer()],
            process=Process.sequential,
            manager_llm=openai
        )
        
        return crew.kickoff()