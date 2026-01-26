from typing import List
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.database import Case

class OrderGenerator:
    def __init__(self, model_name="gpt-4"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        
    def generate_draft(self, submissions: str, precedents: List[Case], judge_name: str, section: str) -> str:
        """
        Generate a legal order draft tailored to the judge's style.
        """
        
        # Format precedents
        precedents_text = ""
        for i, p in enumerate(precedents):
            # Extract relevant snippet if set by retriever, else first 500 chars
            snippet = getattr(p, 'relevance_snippet', p.text_content[:500] if p.text_content else "")
            precedents_text += f"Precedent {i+1} (Case {p.case_id} by {p.judge_name}):\n{snippet}\n---\n"
            
        system_template = """You are {judge_name}. Write a {section} order."""
        
        user_template = """
        Here are the Establishment's submissions:
        {submissions}
        
        Here are similar precedents you have passed:
        {precedents}
        
        Accept/Reject the arguments based on the precedents and draft the final Speaking Order.
        Start with a standard header and the word ORDER in the body.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", user_template)
        ])
        
        input_data = {
            "judge_name": judge_name,
            "section": section,
            "submissions": submissions,
            "precedents": precedents_text
        }
        
        # Use simple invoke flow to be mock-friendly
        messages = prompt.format_messages(**input_data)
        response = self.llm.invoke(messages)
        
        return response.content

