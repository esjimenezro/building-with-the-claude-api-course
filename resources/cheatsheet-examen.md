# Cheatsheet — Claude Certified Architect (CCA) Foundations

Referencia rápida de los conceptos más evaluados en el examen.

---

## Distribución del examen

| Dominio | Peso |
|---------|------|
| Agentic Architecture & Orchestration | 27% |
| Claude Code Configuration & Workflows | 20% |
| Prompt Engineering & Structured Output | 20% |
| Tool Design & MCP Integration | 18% |
| Context Management & Reliability | 15% |

---

## Concepto #1: Enforcement programático vs. guía por prompt

**Regla:** Cuando algo DEBE ocurrir sin excepción, usa código. No prompts.

```
✅ Programático: verificar identidad ANTES de ejecutar reembolso
❌ Prompt: "siempre verifica la identidad antes de un reembolso"
```

Los prompts tienen tasa de fallo no-cero. En producción, eso no es aceptable.

---

## Concepto #2: Agentic Loop

```python
while True:
    response = client.messages.create(...)
    
    if response.stop_reason == "end_turn":
        break  # ✅ Terminar aquí
    
    if response.stop_reason == "tool_use":
        # Ejecutar tools y devolver resultados
        ...
```

❌ NO: detectar fin del loop por contenido de texto
❌ NO: usar un contador de iteraciones como mecanismo principal de parada

---

## Concepto #3: Subagentes no heredan contexto

En multi-agent, CADA subagente recibe solo lo que le pasas explícitamente.

```
Coordinador                Subagente
────────────────           ──────────────────────────────
historial completo    →    SOLO lo que pasas en el prompt
                           No hay memoria compartida
```

---

## Concepto #4: Tool descriptions son el mecanismo de routing

La descripción es lo que Claude usa para decidir qué tool llamar.

```python
# ❌ Descripción vaga — Claude adivinará
{"name": "search", "description": "Busca información"}

# ✅ Descripción precisa — Claude rutea bien
{
    "name": "search_web",
    "description": (
        "Busca información actual en internet. "
        "Úsala para: noticias recientes, precios actuales, eventos. "
        "NO para: documentos internos, datos históricos de la empresa."
    )
}
```

---

## Concepto #5: Batch API vs. Real-time API

| | Batch API | Real-time API |
|-|-----------|---------------|
| Costo | 50% menos | Precio normal |
| SLA | Hasta 24 hrs, sin garantía | Inmediato |
| Usar para | Reportes nocturnos, auditorías | Workflows bloqueantes |

**Regla:** La elección NO es por costo — es por latencia y bloqueo.

---

## Trampas comunes del examen

| Lo que parece correcto | Por qué está mal |
|------------------------|------------------|
| Few-shot examples para ordenar tools | El orden es compliance → usa prerequisites programáticos |
| Self-reported confidence para escalación | LLM calibra mal su confianza en casos difíciles |
| Batch API para ahorrar en todo | No tiene SLA; workflows bloqueantes necesitan real-time |
| Ventana de contexto más grande = mejor atención | Context window ≠ calidad de atención |
| Retornar vacío en fallo de subagente | Suprime errores → el coordinador no puede recuperarse |
| Dar todas las tools a todos los agentes | Degrada la selección; usa 4-5 tools por agente |

---

## Los 6 escenarios del examen (estudia todos — solo 4 aparecen)

1. Customer Support Resolution Agent
2. Code Generation with Claude Code
3. Multi-Agent Research System
4. Developer Productivity with Claude
5. Claude Code for CI/CD
6. Structured Data Extraction

---

## Resources

- https://docs.claude.com
- https://anthropic.skilljar.com
- https://claudecertifications.com
