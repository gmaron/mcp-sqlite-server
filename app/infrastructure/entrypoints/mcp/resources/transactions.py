"""Sub-servidor MCP con tools transaccionales de demostración.

Este módulo se monta como namespace ``transactions`` en el servidor
principal definido en ``main.py``.
"""

from fastmcp import FastMCP, Context

transactions = FastMCP("transactions")


@transactions.tool
async def collect_user_info(name: str, age: int) -> str:
    """Registra información del usuario.

    Args:
        name: Nombre del usuario.
        age: Edad del usuario.

    Returns:
        Cadena de saludo con nombre y edad.
    """
    return f"Hello {name}, you are {age} years old"


@transactions.tool
async def process_transaction(
    transaction_id: str, amount: float, ctx: Context
) -> None:
    """Procesa una transacción y emite un log informativo.

    Args:
        transaction_id: Identificador único de la transacción.
        amount: Monto de la transacción en USD.
        ctx: Contexto de MCP para logging.
    """
    await ctx.info(
        f"Processing transaction {transaction_id}",
        extra={
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": "USD",
        },
    )