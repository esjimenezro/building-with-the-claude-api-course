# Building with the Claude API

Repositorio de aprendizaje del curso **Building with the Claude API** de [Anthropic Academy](https://anthropic.skilljar.com/).

Preparación para la certificación **Claude Certified Architect (CCA) — Foundations**.

---

## Estructura del repositorio

```
building-with-the-claude-api-course/
├── notebooks/
│   ├── 01-basics/              # Primeras llamadas a la API, mensajes, roles
│   ├── 02-tool-use/            # Tool use, function calling
│   ├── 03-agentic-loop/        # Loop agéntico, stop_reason, iteraciones
│   ├── 04-multi-agent/         # Sistemas multi-agente, coordinador + subagentes
│   ├── 05-structured-outputs/  # JSON estructurado, extracción de datos
│   └── 06-context-management/  # Manejo de contexto, ventana, "lost in the middle"
├── src/
│   └── utils.py                # Helpers reutilizables
├── exercises/                  # Ejercicios prácticos por módulo
├── resources/                  # Notas, cheatsheets y material de referencia
├── .env.example                # Variables de entorno requeridas
├── requirements.txt            # Dependencias Python
└── README.md
```

---

## Setup

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/building-with-the-claude-api-course.git
cd building-with-the-claude-api-course
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env y agregar tu ANTHROPIC_API_KEY
```

Obtén tu API key en: https://console.anthropic.com/

---

## Módulos

| # | Módulo | Dominio del examen | Estado |
|---|--------|--------------------|--------|
| 01 | Basics: mensajes, roles, system prompt | Context Management (15%) | ⬜ |
| 02 | Tool use: diseño y routing | Tool Design & MCP (18%) | ⬜ |
| 03 | Agentic loop: stop_reason, iteraciones | Agentic Architecture (27%) | ⬜ |
| 04 | Multi-agent: coordinador + subagentes | Agentic Architecture (27%) | ⬜ |
| 05 | Structured outputs: extracción JSON | Prompt Engineering (20%) | ⬜ |
| 06 | Context management: ventana y límites | Context Management (15%) | ⬜ |

---

## Recursos

- [Anthropic Academy](https://anthropic.skilljar.com/)
- [Documentación oficial de Claude](https://docs.claude.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [Claude Certifications — simulacros](https://claudecertifications.com/)

---

## Autor

**Esteban Jimenez** — Senior Data Scientist @ EPAM NEORIS
