# Agente Autónomo de Análisis y Síntesis de Documentación Técnica

## Descripción

Este proyecto implementa un agente de IA capaz de recibir la URL de una documentación técnica (librería, framework, API, etc.), procesarla, entenderla y responder preguntas complejas sobre ella. El sistema expone una API RESTful y orquesta su lógica mediante un grafo de estados (inspirado en LangGraph), con scraping, segmentación, embeddings y recuperación de información relevante.

---

## Arquitectura de la Solución

### Diagrama General

graph TD
    A[Usuario/Frontend] -->|1. POST doc_url| B[API RESTful: /process-documentation]
    B -->|Procesamiento asíncrono| C[Scraping y Chunking]
    C --> D[Generación de Embeddings]
    D --> E[Base de Datos Vectorial]
    A -->|2. GET status| F[API RESTful: /processing-status]
    A -->|3. POST pregunta| G[API RESTful: /chat]
    G -->|RAG| E
    G --> H[LLM + Formateo]
    H --> I[Respuesta al usuario]
    G --> J[Historial en DB]
    A -->|4. GET historial| K[API RESTful: /chat-history]
    K --> J
```

También puedes consultar la imagen en:  
![Diagrama Arquitectura](docs/diagrama-arquitectura.png)

---

## Grafo de Estados (LangGraph inspirado)

stateDiagram-v2
    [*] --> EsperandoInput
    EsperandoInput --> Procesando : Recibe doc_url
    Procesando --> Chunking : Scraping y segmentación
    Chunking --> Embeddings : Genera embeddings
    Embeddings --> EsperandoPregunta : Embeddings listos
    EsperandoPregunta --> Contestando : Recibe pregunta
    Contestando --> EsperandoPregunta : Responde y guarda en historial
    EsperandoPregunta --> [*] : Termina sesión
```

---

## Justificación de Decisiones Técnicas

**Framework:**  
Se elige Django por su robustez,tambien por que he trabajado con este framework y me siento muy cómodo con el y se estructura para proyectos backend grandes.

**Procesamiento:**  
- Scraping con BeautifulSoup para flexibilidad y limpieza.
- Chunking por párrafos/secciones, listo para chunking semántico futuro.
- Embeddings almacenados para búsqueda rápida y escalable.

**Persistencia:**  
- Base relacional para historial y chunks, compatible con FAISS/ChromaDB para vector search real.

**Extensibilidad:**  
- Arquitectura desacoplada, fácil de migrar a Celery para procesamiento asíncrono real y añadir nuevos motores de embeddings.

---

## Endpoints de la API

| Endpoint                                      | Método | Descripción                                               |
|----------------------------------------------- |--------|-----------------------------------------------------------|
| `/api/v1/process-documentation`               | POST   | Recibe una URL y un chatId. Procesa la documentación.     |
| `/api/v1/processing-status/<chatId>`          | GET    | Devuelve el estado del procesamiento.                     |
| `/api/v1/chat/<chatId>`                       | POST   | Recibe una pregunta y responde usando la documentación.   |
| `/api/v1/chat-history/<chatId>`               | GET    | Devuelve el historial completo de la conversación.        |

---

## Ejemplo de Uso de la API

### 1. Procesar Documentación

```bash
curl -X POST -F "chatId=demo1" -F "doc_url=https://developer.mozilla.org/es/docs/Web/JavaScript" http://localhost:8000/api/v1/process-documentation
```
Respuesta:
```json
{"status": "processing", "chat_id": "demo1"}
```

### 2. Consultar Estado

```bash
curl http://localhost:8000/api/v1/processing-status/demo1
```
Respuesta:
```json
{"status": "processed"}
```

### 3. Preguntar

```bash
curl -X POST -H "Content-Type: application/json" -d '{"question": "¿Qué es JavaScript?"}' http://localhost:8000/api/v1/chat/demo1
```
Respuesta:
```json
{"question": "¿Qué es JavaScript?", "answer": "..."}
```

### 4. Historial

```bash
curl http://localhost:8000/api/v1/chat-history/demo1
```
Respuesta:
```json
{"history": [...]}
```

---

## Instrucciones de Instalación y Ejecución

### 1. Clona el repositorio y entra al proyecto

```bash
git clone https://github.com/IngLuisM/indra.git
cd indra
```

### 2. Crea un entorno virtual e instala dependencias

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configura variables de entorno

Crea un archivo `.env` y coloca tus variables (por ejemplo: claves API, configuración de DB, etc.).

### 4. Ejecuta las migraciones

```bash
python manage.py migrate
```

### 5. Corre el servidor

```bash
python manage.py runserver
```

### 6. Accede al frontend de prueba

Abre en tu navegador:  
[http://localhost:8000/api/v1/prueba-de-formulario/](http://localhost:8000/api/v1/prueba-de-formulario/)

---

## Estructura del Proyecto

```
indra/
├── agent/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils/
│   │   ├── rag.py
│   │   └── scraper.py
│   └── templates/
│       └── form.html
├── indra/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── README.md
└── docs/
    ├── diagrama-arquitectura.png
    └── grafo-langgraph.png
```

---

## Mejoras Futuras

- Integrar embeddings y recuperación semántica real (OpenAI, HuggingFace, FAISS/ChromaDB).
- Chunking semántico avanzado (por secciones o encabezados).
- Mejorar scraping para limpiar menús y secciones no relevantes.
- Mejorar frontend (React/Vue) y agregar autenticación.
- Escalar procesamiento asíncrono con Celery y Redis.
- Despliegue en producción con Docker, Gunicorn, Nginx.

---

## Créditos y Licencia

Desarrollado por IngLuisM.  
Licencia: MIT
