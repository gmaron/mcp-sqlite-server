"""Configuración centralizada de MongoDB para middlewares.

Lee las variables de entorno ``MONGO_URI`` y ``MONGO_DATABASE``
definidas en ``.env`` y provee el cliente y las colecciones
necesarias para los middlewares de logging.
"""

import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "mcp_logs")

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
database = client[MONGO_DATABASE]

# Colecciones utilizadas por los middlewares
tool_calls_collection = database["tool_calls"]
rate_limit_collection = database["rate_limit_exceeded"]
