#!/usr/bin/env python3
"""
Interfaz Web Simple para el Sistema de Evaluación de Candidatos
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from cv_analyzer import CVAnalyzer, EvaluationResult
from conversation_manager import ConversationManager

app = Flask(__name__)
app.secret_key = 'clave_secreta_temporal'

# Inicializar componentes
analyzer = CVAnalyzer()
conversation_manager = ConversationManager()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Endpoint para evaluar CV"""
    data = request.get_json()
    
    requirements_text = data.get('requirements', '')
    cv_text = data.get('cv', '')
    
    if not requirements_text or not cv_text:
        return jsonify({'error': 'Faltan requisitos o CV'}), 400
    
    try:
        # Parsear requisitos
        requirements = analyzer.parse_requirements(requirements_text)
        
        # Analizar CV
        analysis = analyzer.analyze_cv_against_requirements(cv_text, requirements)
        
        # Calcular puntuación
        result = analyzer.calculate_score(analysis, requirements)
        
        # Guardar en sesión
        session['evaluation_result'] = {
            'score': result.score,
            'discarded': result.discarded,
            'matching_requirements': result.matching_requirements,
            'unmatching_requirements': result.unmatching_requirements,
            'not_found_requirements': result.not_found_requirements
        }
        session['requirements'] = requirements_text
        session['cv'] = cv_text
        
        return jsonify({
            'score': result.score,
            'discarded': result.discarded,
            'matching_requirements': result.matching_requirements,
            'unmatching_requirements': result.unmatching_requirements,
            'not_found_requirements': result.not_found_requirements
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    """Iniciar conversación con el candidato"""
    evaluation_result = session.get('evaluation_result')
    
    if not evaluation_result:
        return jsonify({'error': 'No hay evaluación previa'}), 400
    
    if evaluation_result['discarded']:
        return jsonify({'error': 'Candidato descartado'}), 400
    
    if not evaluation_result['not_found_requirements']:
        return jsonify({'message': 'No hay requisitos pendientes'})
    
    try:
        # Convertir a EvaluationResult
        result = EvaluationResult(
            score=evaluation_result['score'],
            discarded=evaluation_result['discarded'],
            matching_requirements=evaluation_result['matching_requirements'],
            unmatching_requirements=evaluation_result['unmatching_requirements'],
            not_found_requirements=evaluation_result['not_found_requirements']
        )
        
        # Generar saludo y primera pregunta
        greeting = conversation_manager.generate_greeting_and_questions(result)
        
        return jsonify({
            'message': greeting,
            'remaining_requirements': result.not_found_requirements
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Procesar mensaje del candidato"""
    data = request.get_json()
    message = data.get('message', '')
    current_requirement = data.get('current_requirement', '')
    remaining_requirements = data.get('remaining_requirements', [])
    
    if not message or not current_requirement:
        return jsonify({'error': 'Faltan datos'}), 400
    
    try:
        # Analizar respuesta
        meets_requirement = conversation_manager.analyze_candidate_response(message, current_requirement)
        
        # Actualizar evaluación
        evaluation_result = session.get('evaluation_result', {})
        
        if meets_requirement:
            evaluation_result['matching_requirements'].append(current_requirement)
            response = "¡Entendido! Gracias por la información."
        else:
            evaluation_result['unmatching_requirements'].append(current_requirement)
            response = "Entendido, gracias por tu honestidad."
        
        # Eliminar requisito procesado
        if current_requirement in evaluation_result['not_found_requirements']:
            evaluation_result['not_found_requirements'].remove(current_requirement)
        
        # Generar siguiente pregunta o mensaje final
        if evaluation_result['not_found_requirements']:
            next_question = conversation_manager.generate_follow_up_question(evaluation_result['not_found_requirements'])
            response += f"\n\n{next_question}"
            next_requirement = evaluation_result['not_found_requirements'][0]
            continue_chat = True
        else:
            # Recalcular puntuación
            total_requirements = len(evaluation_result['matching_requirements']) + len(evaluation_result['unmatching_requirements'])
            if total_requirements > 0:
                evaluation_result['score'] = int((len(evaluation_result['matching_requirements']) / total_requirements) * 100)
            
            final_message = conversation_manager.generate_final_message(evaluation_result['score'])
            response += f"\n\n{final_message}"
            next_requirement = None
            continue_chat = False
        
        # Actualizar sesión
        session['evaluation_result'] = evaluation_result
        
        return jsonify({
            'response': response,
            'next_requirement': next_requirement,
            'continue_chat': continue_chat,
            'updated_score': evaluation_result['score']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(" Iniciando interfaz web en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
