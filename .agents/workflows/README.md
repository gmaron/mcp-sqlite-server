# 🧠 Skills — Guías de Estándares

Las **skills** son documentos de referencia que definen los estándares de calidad del proyecto. Son utilizadas tanto por desarrolladores humanos como por agentes de IA (como Antigravity) para mantener consistencia en el código.

## Skills disponibles

| Skill | Descripción |
|:------|:------------|
| `skill-clean-programming-python.md` | Estándares de código limpio: typing estricto (PEP 585), naming conventions, funciones clean, tooling (Black, isort, Flake8), testing TDD con pytest |
| `skill-architecture-python.md` | Principios de arquitectura: Clean Architecture, SOLID, inyección de dependencias, manejo de errores por dominio |

## ¿Cómo se usan?

### Para desarrolladores

Leé estos documentos antes de contribuir código. Funcionan como una guía de estilo extendida que complementa el linter.

### Para agentes de IA

Los agentes con soporte de workflows (como Antigravity) detectan automáticamente estos archivos en `.agents/workflows/` y los aplican como contexto al generar o revisar código. Podés referenciarlos explícitamente:

> *"Usá la skill-clean-programming-python para validar este módulo"*

## ¿Cómo agregar nuevas skills?

Creá un archivo `.md` en este directorio siguiendo el formato:

```markdown
# Role: [rol del agente]
# Objective: [objetivo principal]

## 1. Sección
- Regla 1
- Regla 2
```

Las skills deben ser **específicas**, **accionables** y **verificables**.
