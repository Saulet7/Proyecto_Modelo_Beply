import asyncio
from dotenv import load_dotenv 
from google.genai import types
from almacen_simple.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

load_dotenv()

APP_NAME = "Agente_de_almacenes"
USER_ID = "user_1"
SESSION_ID = "session_001"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent,
                app_name=APP_NAME,
                session_service=session_service)

async def call_agent_async(query: str, runner, user_id, session_id) -> str:
    print(f"\n>>> Consulta del usuario: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "El agente no produjo una respuesta final."
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"El agente escaló: {event.error_message or 'Sin mensaje específico.'}"
            break
    print(f"<<< Respuesta del agente: {final_response_text}")
    return final_response_text.lower()

"""
async def run_and_check(user_input, expected_keywords, unexpected_keywords):
    response = await call_agent_async(user_input, runner, USER_ID, SESSION_ID)
    print(f"💬 USER: {user_input}")
    print(f"🤖 AGENT: {response}")

    for kw in expected_keywords:
        assert kw.lower() in response, f"❌ FALTA palabra clave esperada: '{kw}'"

    for bad_kw in unexpected_keywords:
        assert bad_kw.lower() not in response, f"❌ RESPUESTA contiene error: '{bad_kw}'"

    print("✅ Test PASADO")
"""

async def run_and_check(user_input):
    response = await call_agent_async(user_input, runner, USER_ID, SESSION_ID)
    print(f"💬 USER: {user_input}")
    print(f"🤖 AGENT: {response}")

"""
async def test_listar_almacenes():
    await run_and_check(
        user_input="Quiero ver todos los almacenes.",
        expected_keywords=["almacenes", "encontrado", "nombre", "dirección"],
        unexpected_keywords=["error", "no se pudo", "falló", "inténtalo de nuevo"]
    )


async def test_crear_fabricante():
    await run_and_check(
        user_input="Agrega un nuevo fabricante con nombre ACME y código FAB001.",
        expected_keywords=["fabricante", "guardado", "acme", "fab001"],
        unexpected_keywords=["error", "no se pudo", "falló", "inténtalo de nuevo"]
    )


async def test_eliminar_fabricante():
    await run_and_check(
        user_input="Elimina el fabricante con código FAB001.",
        expected_keywords=["fabricante", "eliminado", "fab001"],
        unexpected_keywords=["error", "no se pudo", "falló"]
    )



async def test_listar_atributos():
    await run_and_check(
        user_input="¿Qué atributos hay disponibles?",
        expected_keywords=["atributo", "nombre", "valor", "encontrado"],
        unexpected_keywords=["error", "no se pudo", "falló"]
    )
"""

async def test_listar_almacenes():
    await run_and_check("Quiero ver todos los almacenes.")

async def test_crear_fabricante():
    await run_and_check("Agrega un nuevo fabricante con nombre ACME y código FAB001.")

async def test_eliminar_fabricante():
    await run_and_check("Elimina el fabricante con código FAB001.")

async def test_listar_atributos():
    await run_and_check("¿Qué atributos hay disponibles?")


async def main():
    # Crear sesión antes de ejecutar tests
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    await test_listar_almacenes()
    await test_crear_fabricante()
    await test_eliminar_fabricante()
    await test_listar_atributos()


if __name__ == "__main__":
    asyncio.run(main())
