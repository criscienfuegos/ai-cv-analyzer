"""
Sistema de Evaluación de Candidatos con IA Gen
Prueba técnica - 26 de diciembre de 2025
"""

import json
import os
from typing import Dict, Any
#from cv_analyzer import CVAnalyzer, EvaluationResult
#from conversation_manager import ConversationManager

def load_text_from_file(file_path: str) -> str:
    """Carga el contenido de un archivo de texto"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""
    except Exception as e:
        print(f"Error al leer el archivo {file_path}: {e}")
        return ""

def get_sample_requirements() -> str:
    """Retorna los requisitos de ejemplo del PDF"""
    return """Experiencia mínima de 3 años en Python
Formación mínima requerida: Ingeniería/Grado en informática o Master en IA
Valorable conocimientos en FastAPI y LangChain"""

def get_sample_cv() -> str:
    """Retorna el CV de ejemplo del PDF"""
    return """Experiencia:
Desarrollador de IA Generativa - EMPRESA A (Abril 2023 - Actualidad)
Encargado de desarrollar sistemas de IA generativa en Python, diseñando prompts eficientes y sistemas escalables

Data Science / LLM - EMPRESA B (Enero 2022 - Abril 2023)
Analista de datos para el entrenamiento de modelos LLM. Entre mis funciones reentrenamiento y validación con prompt diseñados para validar su correcto funcionamiento

Formación:
Ingeniería Informática (2017 - 2021)"""

def display_results(evaluation_result: EvaluationResult, title: str = "RESULTADO DE LA EVALUACIÓN"):
    """Muestra los resultados de la evaluación de forma formateada"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print('='*50)
    print(f"Puntuación: {evaluation_result.score}%")
    print(f"Descartado: {'Sí' if evaluation_result.discarded else 'No'}")
    
    print(f"\n✅ Requisitos cumplidos ({len(evaluation_result.matching_requirements)}):")
    for req in evaluation_result.matching_requirements:
        print(f"  - {req}")
    
    print(f"\n Requisitos no cumplidos ({len(evaluation_result.unmatching_requirements)}):")
    for req in evaluation_result.unmatching_requirements:
        print(f"  - {req}")
    
    print(f"\n Requisitos no encontrados en CV ({len(evaluation_result.not_found_requirements)}):")
    for req in evaluation_result.not_found_requirements:
        print(f"  - {req}")
    
    print('='*50)

def save_results_to_json(evaluation_result: EvaluationResult, filename: str = "evaluation_result.json"):
    """Guarda los resultados en un archivo JSON"""
    result_dict = {
        "score": evaluation_result.score,
        "discarded": evaluation_result.discarded,
        "matching_requirements": evaluation_result.matching_requirements,
        "unmatching_requirements": evaluation_result.unmatching_requirements,
        "not_found_requirements": evaluation_result.not_found_requirements
    }
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(result_dict, file, indent=2, ensure_ascii=False)
    
    print(f"\nResultados guardados en: {filename}")

def main():
    """Función principal del sistema"""
    print(" SISTEMA DE EVALUACIÓN DE CANDIDATOS CON IA")
    print("="*50)
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("  ADVERTENCIA: No se encontró OPENAI_API_KEY en el archivo .env")
        print("Por favor, configura tu API key de OpenAI en el archivo .env")
        return
    
    # Inicializar componentes
    analyzer = CVAnalyzer()
    conversation_manager = ConversationManager()
    
    # Menu de opciones
    print("\n¿Cómo desea ingresar los datos?")
    print("1. Usar datos de ejemplo (del PDF)")
    print("2. Ingresar manualmente")
    print("3. Cargar desde archivos")
    
    choice = input("\nSeleccione una opción (1-3): ").strip()
    
    requirements_text = ""
    cv_text = ""
    
    if choice == "1":
        # Usar datos de ejemplo
        requirements_text = get_sample_requirements()
        cv_text = get_sample_cv()
        print("\n Usando datos de ejemplo del PDF")
        
    elif choice == "2":
        # Ingresar manualmente
        print("\n Ingrese los requisitos de la oferta (una por línea, línea vacía para terminar):")
        req_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            req_lines.append(line)
        requirements_text = "\n".join(req_lines)
        
        print("\n Ingrese el CV del candidato (línea vacía para terminar):")
        cv_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            cv_lines.append(line)
        cv_text = "\n".join(cv_lines)
        
    elif choice == "3":
        # Cargar desde archivos
        req_file = input("\n Ruta del archivo de requisitos: ").strip()
        cv_file = input(" Ruta del archivo del CV: ").strip()
        
        requirements_text = load_text_from_file(req_file)
        cv_text = load_text_from_file(cv_file)
        
        if not requirements_text or not cv_text:
            print(" Error al cargar los archivos. Verifique las rutas.")
            return
    
    else:
        print(" Opción no válida")
        return
    
    # Verificar que se tengan los datos
    if not requirements_text or not cv_text:
        print(" Error: No se proporcionaron requisitos o CV")
        return
    
    print(f"\n Analizando CV contra {len(requirements_text.split())} requisitos...")
    
    try:
        # Paso 1: Parsear requisitos
        requirements = analyzer.parse_requirements(requirements_text)
        print(f" Se identificaron {len(requirements)} requisitos")
        
        # Paso 2: Analizar CV
        analysis = analyzer.analyze_cv_against_requirements(cv_text, requirements)
        
        # Paso 3: Calcular puntuación inicial
        initial_result = analyzer.calculate_score(analysis, requirements)
        
        # Mostrar resultados iniciales
        display_results(initial_result, "EVALUACIÓN INICIAL DEL CV")
        
        # Guardar resultados iniciales
        save_results_to_json(initial_result, "initial_evaluation.json")
        
        # Paso 4: Conversación si no está descartado y hay requisitos no encontrados
        if not initial_result.discarded and initial_result.not_found_requirements:
            print("\n  Iniciando conversación con el candidato...")
            
            # Preguntar si desea continuar con la conversación
            continue_conversation = input("\n¿Desea continuar con la conversación? (s/n): ").strip().lower()
            
            if continue_conversation in ['s', 'si', 'sí']:
                final_result = conversation_manager.conduct_conversation(initial_result)
                
                # Mostrar resultados finales
                display_results(final_result, "EVALUACIÓN FINAL")
                
                # Guardar resultados finales
                save_results_to_json(final_result, "final_evaluation.json")
                
                # Mostrar mejora
                improvement = final_result.score - initial_result.score
                if improvement > 0:
                    print(f"\n ¡Mejora de +{improvement}% gracias a la conversación!")
                elif improvement < 0:
                    print(f"\n Cambio de {improvement}% en la puntuación")
                else:
                    print("\n La puntuación se mantuvo igual")
            else:
                print("\n Proceso finalizado. Se conservó la evaluación inicial.")
        
        elif initial_result.discarded:
            print("\n El candidato ha sido descartado por no cumplir requisitos obligatorios.")
        else:
            print("\n El candidato cumple con todos los requisitos detectados. ¡Excelente!")
        
        print("\n Proceso de evaluación completado")
        
    except Exception as e:
        print(f"\n Error durante el proceso: {e}")
        print("Por favor, verifique su conexión a internet y la configuración de la API key")

if __name__ == "__main__":
    main()