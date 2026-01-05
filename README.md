#  Sistema de Evaluación de Candidatos con IA Gen

Prueba técnica de IA Gen - 26 de diciembre de 2025

##  Descripción

Sistema basado en LLM para evaluar candidatos contra requisitos de ofertas laborales. El sistema consta de dos fases:

1. **Fase 1**: Análisis autónomo de la oferta y el CV para obtener una puntuación inicial
2. **Fase 2**: Conversación interactiva con el candidato para obtener información faltante

##  Arquitectura

- **Python** como lenguaje principal
- **LangChain** para abstracción del LLM (compatible con múltiples proveedores)
- **OpenAI GPT-3.5-turbo** como modelo de lenguaje
- **Flask** para interfaz web opcional
- **Pydantic** para validación de datos

##  Instalación

1. Clonar o descargar el proyecto
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar la API key de OpenAI en el archivo `.env`:
```
OPENAI_API_KEY=tu_api_key_aqui
```

##  Uso

### Opción 1: Interfaz por Terminal

Ejecutar el script principal:
```bash
python main.py
```

El sistema ofrecerá tres opciones:
1. Usar datos de ejemplo (del PDF)
2. Ingresar datos manualmente
3. Cargar desde archivos

### Opción 2: Interfaz Web

Iniciar el servidor web:
```bash
python web_interface.py
```

Abrir en el navegador: http://localhost:5000

##  Funcionalidades

###  Análisis de CV
- Identificación automática de requisitos obligatorios vs opcionales
- Análisis semántico del contenido del CV
- Detección de información explícita y ausencia de datos

###  Sistema de Puntuación
- Puntuación sobre 100% basada en requisitos cumplidos
- Descarte automático por requisitos obligatorios no cumplidos
- Recálculo dinámico durante la conversación

###  Conversación Inteligente
- Preguntas contextuales sobre requisitos no encontrados
- Análisis de respuestas del candidato
- Actualización en tiempo real de la puntuación

##  Estructura del Proyecto

```
├── main.py                 # Script principal (terminal)
├── web_interface.py        # Interfaz web Flask
├── cv_analyzer.py          # Módulo de análisis de CV
├── conversation_manager.py # Gestor de conversaciones
├── requirements.txt        # Dependencias Python
├── .env                   # Variables de entorno (API key)
├── templates/
│   └── index.html         # Interfaz web
└── README.md              # Este archivo
```

##  Ejemplo de Uso

### Datos de Entrada

**Requisitos:**
```
Experiencia mínima de 3 años en Python
Formación mínima requerida: Ingeniería/Grado en informática o Master en IA
Valorable conocimientos en FastAPI y LangChain
```

**CV:**
```
Experiencia:
Desarrollador de IA Generativa - EMPRESA A (Abril 2023 - Actualidad)
Encargado de desarrollar sistemas de IA generativa en Python...

Formación:
Ingeniería Informática (2017 - 2021)
```

### Resultado Inicial
```json
{
  "score": 50,
  "discarded": false,
  "matching_requirements": [
    "3 años de experiencia en Python",
    "Formación en Ingeniería en informática"
  ],
  "unmatching_requirements": [],
  "not_found_requirements": [
    "Conocimientos en FastAPI",
    "Conocimientos en LangChain"
  ]
}
```

### Conversación y Resultado Final
El sistema preguntará sobre FastAPI y LangChain, y si el candidato confirma experiencia en FastAPI, la puntuación final será de 75%.

##  Configuración

### Variables de Entorno
- `OPENAI_API_KEY`: API key de OpenAI (requerida)

### Personalización
- Cambiar el modelo LLM en `cv_analyzer.py` y `conversation_manager.py`
- Modificar prompts para ajustar el tono y comportamiento
- Extender el sistema para otros proveedores de LLM

##  Características Técnicas

- **Modularidad**: Código organizado en módulos especializados
- **Extensibilidad**: Fácil agregar nuevos proveedores de LLM
- **Robustez**: Manejo de errores y validación de datos
- **UX**: Interfaz amigable tanto en terminal como web
- **JSON Output**: Resultados estructurados para integración

##  Troubleshooting

### Problemas Comunes

1. **Error de API key**: Verificar que el archivo `.env` contenga una API key válida
2. **Error de conexión**: Asegurar conexión a internet y que la API key tenga créditos
3. **Error de módulos**: Ejecutar `pip install -r requirements.txt` en un entorno virtual limpio

### Logs y Debug

El sistema muestra mensajes de estado detallados durante la ejecución. Para debugging adicional, se pueden modificar los prompts para incluir más información.

##  Mejoras Futuras

- [ ] Soporte para múltiples proveedores de LLM (Gemini, Claude, etc.)
- [ ] Interfaz de usuario más avanzada
- [ ] Sistema de persistencia de evaluaciones
- [ ] Integración con ATS (Applicant Tracking Systems)
- [ ] Análisis de sentimiento en las respuestas
- [ ] Generación de reportes PDF

##  Licencia

Proyecto desarrollado como prueba técnica de evaluación.

---

**Nota**: Este sistema está diseñado específicamente para la prueba técnica descrita en el documento proporcionado.