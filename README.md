# 🗄️ MCP Server SQLite

Servidor **MCP (Model Context Protocol)** escrito en Python que expone una base de datos SQLite a través de herramientas (*tools*) y recursos (*resources*) consumibles por cualquier cliente MCP — incluidos IDEs como **Antigravity**.

---

## 📖 Tabla de contenidos

1. [¿Qué es MCP?](#qué-es-mcp)
2. [Arquitectura del proyecto](#arquitectura-del-proyecto)
3. [Paso a paso: cómo lo construí](#paso-a-paso-cómo-lo-construí)
4. [Requisitos previos](#requisitos-previos)
5. [Instalación](#instalación)
6. [Configuración](#configuración)
7. [Ejecución](#ejecución)
8. [Tests](#tests)
9. [Probarlo en Antigravity IDE](#probarlo-en-antigravity-ide)
10. [Estructura de directorios](#estructura-de-directorios)
11. [Skills (estándares de código)](#skills-estándares-de-código)
12. [Licencia](#licencia)

---

## ¿Qué es MCP?

El **Model Context Protocol (MCP)** es un estándar abierto que conecta sistemas de IA con fuentes de datos y herramientas externas. Un servidor MCP expone:

| Concepto     | Descripción                                                  |
|:-------------|:-------------------------------------------------------------|
| **Tools**    | Funciones que un modelo puede invocar (ej. `collect_user_info`, `obtener_usuarios`). |
| **Resources**| Datos de solo lectura accesibles mediante URIs (ej. `db://usuarios/todos`). |
| **Middleware**| Capas intermedias para logging, rate-limiting, manejo de errores, etc. |

---

## Arquitectura del proyecto

El proyecto sigue los principios de **Clean Architecture** para mantener las responsabilidades separadas:

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│               (FastMCP + Middleware chain)                   │
└──────────┬──────────────────────────┬───────────────────────┘
           │ monta                    │ monta
┌──────────▼──────────┐  ┌───────────▼────────────┐
│  queries (namespace)│  │ transactions (namespace)│
│   obtener_usuarios  │  │  collect_user_info      │
│   resource_usuarios │  │  process_transaction    │
└──────────┬──────────┘  └────────────────────────┘
           │ usa
┌──────────▼──────────────────────────────────────┐
│             application / use_cases              │
│                  get_users.py                     │
└──────────┬──────────────────────────────────────┘
           │ depende de
┌──────────▼──────────────────────────────────────┐
│                   domain                         │
│   entities/usuario.py   interfaces/user_repo.py  │
└─────────────────────────────────────────────────┘
```

**Capas:**

- **Domain** — Entidades (`Usuario`) e interfaces abstractas (`UserRepository`).
- **Application** — Casos de uso que orquestan la lógica de negocio (`GetUsersUseCase`).
- **Infrastructure** — Implementaciones concretas: repositorio SQLite, servidor MCP, middlewares de logging y rate-limiting con MongoDB.

---

## Paso a paso: cómo lo construí

### 1. Definir el dominio

Creé la entidad `Usuario` con Pydantic y una interfaz abstracta `UserRepository` (patrón *Repository*) para desacoplar la capa de datos del negocio.

### 2. Implementar el caso de uso

`GetUsersUseCase` recibe un repositorio por inyección de dependencias y ejecuta la consulta, opcionalmente filtrando por nacionalidad.

### 3. Crear el repositorio SQLite

`SqliteUserRepository` implementa `UserRepository` usando `sqlite3` de la stdlib. Conecta a un archivo `.db` y mapea filas a entidades `Usuario`.

### 4. Armar el servidor MCP con FastMCP

En `main.py` inicialicé una instancia de `FastMCP` y monté dos sub-servidores como namespaces independientes:
- **queries** — operaciones de lectura sobre la base de datos.
- **transactions** — tools de prueba (`collect_user_info`, `process_transaction`).

### 5. Crear el sub-servidor de queries

`queries.py` es otro `FastMCP` que expone el tool `obtener_usuarios` y el resource `db://usuarios/todos`. Se monta con `mcp.mount(queries, namespace="queries")`.

### 6. Crear el sub-servidor de transactions

`transactions.py` expone `collect_user_info` (saludo de prueba) y `process_transaction` (demuestra logging contextual). Se monta con `mcp.mount(transactions, namespace="transactions")`.

### 7. Agregar middlewares

Se encadenaron middlewares para:
- **Error handling** (`ErrorHandlingMiddleware`) — captura excepciones no manejadas.
- **Rate limit event** (`RateLimitEventMiddleware`) — registra en MongoDB cuando se excede el rate-limit.
- **Rate limiting** (`SlidingWindowRateLimitingMiddleware`) — ventana deslizante de 25 req/min.
- **Logging stdout** (`LoggingMiddleware`) — log estándar por consola.
- **Tool call logging** (`ToolCallLoggingMiddleware`) — persiste cada llamada a tool en MongoDB.

### 8. Poblar la base de datos de ejemplo

`setup_db.py` genera 10 usuarios aleatorios con datos representativos.

---

## Funcionalidad RAG (Knowledge Base)

El servidor incluye una tool montada en el namespace `knowledge` orientada a consultar una base de conocimiento usando **Generative AI** (Gemini) y una base de datos vectorial local (**ChromaDB**). 

Esta funcionalidad fue construida respetando la Clean Architecture del proyecto:
- **Dominio**: Se define la interfaz `KnowledgeRepository` como contrato para las consultas, protegiendo al núcleo del uso de librerías externas.
- **Caso de Uso**: `query_knowledge.py` orquesta la consulta de información sin acoplarse a LangChain o a FastMCP.
- **Adaptador**: `rag_langchain_adapter.py` provee la implementación concreta del repositorio utilizando **LangChain** para integrarse con ChromaDB y Gemini.

---

## Requisitos previos

| Requisito | Versión mínima |
|:----------|:---------------|
| Python    | 3.10+          |
| Docker y Docker Compose | (para MongoDB de logging) |

> **Nota:** MongoDB es opcional. Si no está corriendo, el servidor funciona pero los middlewares de logging a Mongo fallarán silenciosamente en la primera llamada.

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/mcp-server-sqlite.git
cd mcp-server-sqlite

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar variables de entorno
cp .env.example .env
# Editá .env si necesitás cambiar DB_PATH, MONGO_URI, etc.

# 5. (Opcional) Levantar MongoDB para logging
docker compose up -d

# 6. Crear la base de datos de ejemplo
python setup_db.py
```

---

## Configuración

Toda la configuración se gestiona mediante variables de entorno en el archivo `.env`. El servidor usa `python-dotenv` para cargarlas automáticamente al iniciar.

```bash
# ─── App ───
PYTHONPATH=.
DB_PATH=./users.db

# ─── MongoDB (debe coincidir con docker-compose.yml) ───
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=mcp_logs
```

Las variables `MONGO_URI` y `MONGO_DATABASE` están **sincronizadas con `docker-compose.yml`** — el compose las lee del mismo `.env` usando `${MONGO_URI:-fallback}`. Esto significa que si cambiás el nombre de la base de datos o la URI, solo necesitás modificar `.env` y ambos (app y Docker) se actualizan.

---

## Ejecución

### Modo HTTP (Streamable HTTP)

```bash
fastmcp run main.py:mcp --transport http --port 8000
```

El servidor arranca en `http://127.0.0.1:8000/mcp`.

### Modo desarrollo con hot-reload

```bash
fastmcp run main.py:mcp --transport http --port 8000 --reload
```

### Modo desarrollo con MCP Inspector

```bash
fastmcp dev main.py
```

Esto abre el **MCP Inspector** en el navegador para probar tools y resources de forma interactiva.

---

## Tests

El proyecto incluye tests unitarios y de integración con **pytest**.

### Tests unitarios (no requieren servidor)

```bash
pytest tests/unit/ -v
```

Estos tests usan una base de datos SQLite temporal que se crea y destruye automáticamente en cada ejecución. Cubren:

| Archivo | Qué testea | Tests |
|:--------|:-----------|:-----:|
| `test_usuario.py` | Entidad Pydantic: validación, serialización | 6 |
| `test_repository.py` | Repositorio SQLite: consultas, filtros | 8 |
| `test_use_cases.py` | Caso de uso con DB real y con mocks | 6 |

### Tests de integración (requieren servidor corriendo)

```bash
# Terminal 1: levantar servicios
docker compose up -d
fastmcp run main.py:mcp --transport http --port 8000

# Terminal 2: correr tests
pytest tests/integration/ -v
```

Si el servidor **no está corriendo**, estos tests se **skipean automáticamente**.

### Todos los tests juntos

```bash
pytest -v
```

### Test de rate-limiting (lento)

```bash
pytest -v -m slow
```

Este test hace 30 llamadas rápidas y verifica que el rate-limiter bloquee a partir de la 26.

---

## Probarlo en Antigravity IDE

### 1. Configurar el servidor MCP en Antigravity

Agregá la siguiente entrada en tu archivo de configuración MCP del IDE (`mcp_config.json` o equivalente):

```json
{
  "mcpServers": {
    "sqlite-server": {
      "command": "/ruta/a/tu/.venv/bin/python",
      "args": ["/ruta/a/tu/mcp-server-sqlite/main.py"],
      "env": {
        "PYTHONPATH": "/ruta/a/tu/mcp-server-sqlite",
        "DB_PATH": "/ruta/a/tu/mcp-server-sqlite/users.db",
        "MONGO_URI": "mongodb://localhost:27017/",
        "MONGO_DATABASE": "mcp_logs"
      }
    }
  }
}
```

> Reemplazá `/ruta/a/tu/` con las rutas reales de tu sistema.

### 2. Reiniciar Antigravity

Una vez guardada la configuración, reiniciá el IDE para que detecte el nuevo servidor MCP.

### 3. Usar los tools desde el chat

En el chat de Antigravity podés invocar directamente las herramientas:

- **`transactions_collect_user_info`** — *"Registrá un usuario llamado Juan de 30 años"*
- **`queries_obtener_usuarios`** — *"Obtené todos los usuarios"* o *"Listá los usuarios de Argentina"*
- **`transactions_process_transaction`** — *"Procesá la transacción TX-001 por 150.50"*

### 4. Ver resultados

Los resultados se mostrarán en línea en el chat. Si tenés MongoDB corriendo, podés inspeccionar los logs en `http://localhost:8081` (Mongo Express).

---

## Estructura de directorios

```
mcp-server-sqlite/
├── main.py                              # Punto de entrada principal
├── setup_db.py                          # Script para crear la DB de ejemplo
├── pyproject.toml                       # Configuración del proyecto Python
├── requirements.txt                     # Dependencias pip
├── docker-compose.yml                   # MongoDB + Mongo Express
├── .env.example                         # Template de variables de entorno
├── .gitignore
├── .agents/
│   └── workflows/
│       ├── skill-clean-programming-python.md
│       └── skill-architecture-python.md
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── usuario.py               # Entidad Usuario (Pydantic)
│   │   └── interfaces/
│   │       └── user_repository.py        # Interfaz abstracta
│   ├── application/
│   │   └── use_cases/
│   │       └── get_users.py              # Caso de uso
│   └── infrastructure/
│       ├── database/
│       │   └── sqlite_repository.py      # Repositorio SQLite
│       ├── entrypoints/
│       │   └── mcp/resources/
│       │       ├── queries.py            # Sub-servidor de queries
│       │       └── transactions.py       # Sub-servidor de transactions
│       └── middleware/
│           ├── mongo_config.py                  # Config centralizada de MongoDB
│           ├── tool_call_logging_middleware.py   # Logging de cada tool call
│           └── rate_limit_event_middleware.py    # Logging de rate-limit events
├── tests/
│   ├── conftest.py                      # Fixtures compartidos
│   ├── unit/
│   │   ├── test_usuario.py              # Tests entidad Usuario
│   │   ├── test_repository.py           # Tests repositorio SQLite
│   │   └── test_use_cases.py            # Tests caso de uso
│   └── integration/
│       └── test_mcp_server.py           # Tests contra servidor MCP
└── README.md
```

---

## Skills (estándares de código)

El proyecto incluye **skills** en `.agents/workflows/` que documentan los estándares de calidad aplicados:

| Skill | Qué define |
|:------|:-----------|
| `skill-clean-programming-python.md` | Typing estricto (PEP 585), naming conventions, funciones clean, testing TDD |
| `skill-architecture-python.md` | Clean Architecture, SOLID, inyección de dependencias, manejo de errores |

Estas guías son utilizadas tanto por desarrolladores como por agentes de IA para mantener la consistencia del código. Ver [`.agents/workflows/README.md`](.agents/workflows/README.md) para más detalles.

---

## Licencia

MIT © 2025
