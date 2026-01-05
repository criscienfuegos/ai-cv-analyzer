from typing import List, Dict, Any
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class Requirement(BaseModel):
    description: str
    is_mandatory: bool

class EvaluationResult(BaseModel):
    score: int
    discarded: bool
    matching_requirements: List[str]
    unmatching_requirements: List[str]
    not_found_requirements: List[str]

class CVAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def parse_requirements(self, requirements_text: str) -> List[Requirement]:
        """Parsea el texto de requisitos y los convierte en objetos Requirement"""
        requirements = []
        lines = requirements_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_mandatory = not any(keyword in line.lower() for keyword in ['valorable', 'opcional', 'deseable'])
            
            # Limpiar el texto del requisito
            clean_req = line
            if any(keyword in line.lower() for keyword in ['valorable', 'opcional', 'deseable']):
                clean_req = line.split('valorable')[-1].split('opcional')[-1].split('deseable')[-1].strip()
                clean_req = clean_req.replace('conocimientos en', '').replace('experiencia en', '').strip()
            
            requirements.append(Requirement(
                description=clean_req if clean_req else line.strip(),
                is_mandatory=is_mandatory
            ))
        
        return requirements
    
    def analyze_cv_against_requirements(self, cv_text: str, requirements: List[Requirement]) -> Dict[str, Any]:
        """Analiza el CV contra los requisitos usando LLM"""
        
        requirements_list = "\n".join([
            f"- {req.description} ({'OBLIGATORIO' if req.is_mandatory else 'OPCIONAL'})"
            for req in requirements
        ])
        
        system_prompt = """
        Eres un experto en recursos humanos especializado en evaluar CVs contra requisitos de ofertas laborales.
        Analiza el CV proporcionado y determina para cada requisito si:
        1. El candidato cumple con el requisito (basado en información explícita en el CV)
        2. El candidato no cumple con el requisito
        3. No se puede determinar si cumple o no (la información no aparece en el CV)
        
        Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
        {
            "analysis": [
                {
                    "requirement": "texto del requisito",
                    "status": "matched|unmatched|not_found",
                    "explanation": "breve explicación"
                }
            ]
        }
        """
        
        human_prompt = f"""
        REQUISITOS DE LA OFERTA:
        {requirements_list}
        
        CV DEL CANDIDATO:
        {cv_text}
        
        Analiza cada requisito y determina su estado.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            import json
            analysis_data = json.loads(response.content)
            return analysis_data
        except json.JSONDecodeError:
            # Si hay error en el JSON, intenta extraer la parte JSON
            content = response.content
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No se pudo procesar la respuesta del LLM")
    
    def calculate_score(self, analysis: Dict[str, Any], requirements: List[Requirement]) -> EvaluationResult:
        """Calcula la puntuación final basada en el análisis"""
        
        matching_requirements = []
        unmatching_requirements = []
        not_found_requirements = []
        discarded = False
        
        # Mapear requisitos por descripción para fácil acceso
        req_map = {req.description: req for req in requirements}
        
        for item in analysis.get('analysis', []):
            req_desc = item['requirement']
            status = item['status']
            
            # Buscar requisito correspondiente (búsqueda flexible)
            matching_req = None
            for req in requirements:
                if req_desc.lower() in req.description.lower() or req.description.lower() in req_desc.lower():
                    matching_req = req
                    break
            
            if not matching_req:
                continue
                
            if status == 'matched':
                matching_requirements.append(matching_req.description)
            elif status == 'unmatched':
                unmatching_requirements.append(matching_req.description)
                # Si es requisito obligatorio no cumplido, descartar
                if matching_req.is_mandatory:
                    discarded = True
            elif status == 'not_found':
                not_found_requirements.append(matching_req.description)
        
        # Calcular puntuación
        total_requirements = len(requirements)
        if total_requirements == 0:
            score = 0
        elif discarded:
            score = 0
        else:
            matched_count = len(matching_requirements)
            score = int((matched_count / total_requirements) * 100)
        
        return EvaluationResult(
            score=score,
            discarded=discarded,
            matching_requirements=matching_requirements,
            unmatching_requirements=unmatching_requirements,
            not_found_requirements=not_found_requirements
        )
