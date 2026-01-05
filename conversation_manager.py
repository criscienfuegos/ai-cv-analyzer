from typing import List, Dict, Any
from pydantic import BaseModel
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

class ConversationManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def generate_greeting_and_questions(self, evaluation_result: EvaluationResult) -> str:
        """Genera el saludo inicial y las preguntas para los requisitos no encontrados"""
        
        if not evaluation_result.not_found_requirements:
            return "¡Hola! Tu CV ha sido evaluado y cumple con todos los requisitos de la oferta. ¡Felicidades!"
        
        requirements_text = "\n".join([f"- {req}" for req in evaluation_result.not_found_requirements])
        
        system_prompt = """
        Eres un reclutador amable y profesional. Debes saludar al candidato y preguntar sobre los requisitos 
        que no se encontraron en su CV. Sé natural y conversacional, no hables como un robot.
        
        Genera un saludo seguido de preguntas específicas sobre cada requisito no encontrado.
        Haz una pregunta a la vez para mantener la conversación natural.
        """
        
        human_prompt = f"""
        REQUISITOS NO ENCONTRADOS EN EL CV:
        {requirements_text}
        
        PUNTUACIÓN ACTUAL: {evaluation_result.score}%
        
        Genera un saludo amigable y luego pregunta sobre estos requisitos de forma conversacional.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def analyze_candidate_response(self, response: str, requirement: str) -> bool:
        """Analiza la respuesta del candidato para determinar si cumple el requisito"""
        
        system_prompt = """
        Eres un experto en evaluar respuestas de candidatos. Analiza la respuesta y determina si el candidato
        cumple con el requisito mencionado.
        
        Responde ÚNICAMENTe con "SI" o "NO" (sin comillas ni texto adicional).
        - "SI" si la respuesta indica que el candidato cumple con el requisito
        - "NO" si la respuesta indica que no cumple o no está claro
        """
        
        human_prompt = f"""
        REQUISITO: {requirement}
        RESPUESTA DEL CANDIDATO: {response}
        
        ¿El candidato cumple con este requisito?
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip().upper() == "SI"
    
    def generate_follow_up_question(self, remaining_requirements: List[str]) -> str:
        """Genera la siguiente pregunta para los requisitos pendientes"""
        
        if not remaining_requirements:
            return "¡Gracias por tus respuestas! He completado la evaluación de tu perfil."
        
        next_requirement = remaining_requirements[0]
        
        system_prompt = """
        Eres un reclutador conversacional. Formula una pregunta natural sobre el siguiente requisito.
        Sé amable y profesional.
        """
        
        human_prompt = f"""
        SIGUIENTE REQUISITO A PREGUNTAR: {next_requirement}
        
        Formula una pregunta natural y conversacional sobre este requisito.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_final_message(self, updated_score: int) -> str:
        """Genera el mensaje final con la puntuación actualizada"""
        
        system_prompt = """
        Eres un reclutador profesional. Genera un mensaje de cierre agradeciendo al candidato 
        e informándole de su puntuación final. Sé amable y profesional.
        """
        
        human_prompt = f"""
        PUNTUACIÓN FINAL: {updated_score}%
        
        Genera un mensaje de cierre agradeciendo al candidato por su tiempo e informándole 
        de su puntuación final.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def conduct_conversation(self, evaluation_result: EvaluationResult) -> EvaluationResult:
        """Conduce la conversación completa con el candidato"""
        
        # Si no hay requisitos no encontrados, retornar el resultado original
        if not evaluation_result.not_found_requirements:
            return evaluation_result
        
        # Copiar el resultado para actualizarlo
        updated_result = EvaluationResult(
            score=evaluation_result.score,
            discarded=evaluation_result.discarded,
            matching_requirements=evaluation_result.matching_requirements.copy(),
            unmatching_requirements=evaluation_result.unmatching_requirements.copy(),
            not_found_requirements=evaluation_result.not_found_requirements.copy()
        )
        
        # Generar saludo y primera pregunta
        greeting = self.generate_greeting_and_questions(evaluation_result)
        print("\n" + "="*50)
        print("CONVERSACIÓN CON EL CANDIDATO")
        print("="*50)
        print(f"\nAsistente: {greeting}")
        
        remaining_requirements = updated_result.not_found_requirements.copy()
        
        # Iterar sobre cada requisito no encontrado
        while remaining_requirements:
            current_requirement = remaining_requirements[0]
            
            # Obtener respuesta del candidato
            print(f"\nAsistente: ¿Podrías sobre tu experiencia con {current_requirement}?")
            candidate_response = input("\nCandidato: ")
            
            # Analizar la respuesta
            if self.analyze_candidate_response(candidate_response, current_requirement):
                # El candidato cumple el requisito
                updated_result.matching_requirements.append(current_requirement)
                updated_result.not_found_requirements.remove(current_requirement)
                remaining_requirements.remove(current_requirement)
                print("\nAsistente: ¡Entendido! Gracias por la información.")
            else:
                # El candidato no cumple el requisito
                updated_result.unmatching_requirements.append(current_requirement)
                updated_result.not_found_requirements.remove(current_requirement)
                remaining_requirements.remove(current_requirement)
                print("\nAsistente: Entendido, gracias por tu honestidad.")
            
            # Si quedan más requisitos, generar siguiente pregunta
            if remaining_requirements:
                next_question = self.generate_follow_up_question(remaining_requirements)
                print(f"\nAsistente: {next_question}")
        
        # Recalcular puntuación
        total_requirements = len(updated_result.matching_requirements) + len(updated_result.unmatching_requirements)
        if total_requirements > 0:
            updated_result.score = int((len(updated_result.matching_requirements) / total_requirements) * 100)
        
        # Mensaje final
        final_message = self.generate_final_message(updated_result.score)
        print(f"\nAsistente: {final_message}")
        
        return updated_result