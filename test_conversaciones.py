import asyncio
from dotenv import load_dotenv 
from google.genai import types
from almacen_simple.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import make_fs_request

from tenacity import retry, wait_random_exponential, stop_after_attempt

load_dotenv()

APP_NAME = "Agente_de_almacenes"
USER_ID = "user_1"
SESSION_ID = "session_001"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent,
                app_name=APP_NAME,
                session_service=session_service)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
async def call_agent_async(query: str, runner, user_id, session_id) -> str:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                return event.content.parts[0].text.lower()
            elif event.actions and event.actions.escalate:
                return f"escalado: {event.error_message or 'sin mensaje'}".lower()
    return "sin respuesta"

async def test_listar_almacenes():
    response = await call_agent_async("Quiero ver todos los almacenes.", runner, USER_ID, SESSION_ID)
    api_response = make_fs_request("GET", "/almacenes")
    message = api_response.get("message_for_user", "").lower()
    if message in response:
        print("✅ test_listar_almacenes: PASA")
    else:
        print("❌ test_listar_almacenes: FALLA")

async def test_crear_fabricante():
    response = await call_agent_async("Agrega un nuevo fabricante con nombre ACME y código 8.", runner, USER_ID, SESSION_ID)
    api_response = make_fs_request("POST", "/fabricantes", data={"nombre": "ACME", "codigo": "8"})
    message = api_response.get("message_for_user", "").lower()
    if message in response:
        print("✅ test_crear_fabricante")
    else:
        print("❌ test_crear_fabricante")

async def test_actualizar_fabricante():
    # Buscar el fabricante por código
    consulta = make_fs_request("GET", "/fabricantes", params={"codfabricante": "8"})
    fabricantes = consulta.get("data", [])
    if not fabricantes:
        print("❌ test_actualizar_fabricante: FABRICANTE NO ENCONTRADO")
        return
    fabricante_id = fabricantes[0].get("codfabricante")
    if not fabricante_id:
        print("❌ test_actualizar_fabricante: ID NO DISPONIBLE")
        return

    # Ejecutar la consulta del agente
    response = await call_agent_async("Elimina el fabricante con código 8.", runner, USER_ID, SESSION_ID)

    # Eliminar por ID directamente (lo que el agente también debería hacer)
    api_response = make_fs_request("DELETE", f"/fabricantes/{fabricante_id}")
    message = api_response.get("message_for_user", "").lower()

    if message in response:
        print("✅ test_eliminar_fabricante: PASA")
    else:
        print("❌ test_eliminar_fabricante: FALLA")

async def test_eliminar_fabricante():
    # Buscar el fabricante por código
    consulta = make_fs_request("GET", "/fabricantes", params={"codfabricante": "8"})
    fabricantes = consulta.get("data", [])
    if not fabricantes:
        print("❌ test_eliminar_fabricante: FABRICANTE NO ENCONTRADO")
        return
    fabricante_id = fabricantes[0].get("codfabricante")
    if not fabricante_id:
        print("❌ test_eliminar_fabricante: ID NO DISPONIBLE")
        return

    # Ejecutar la consulta del agente
    response = await call_agent_async("Elimina el fabricante con código 8.", runner, USER_ID, SESSION_ID)

    # Eliminar por ID directamente (lo que el agente también debería hacer)
    api_response = make_fs_request("DELETE", f"/fabricantes/{fabricante_id}")
    message = api_response.get("message_for_user", "").lower()

    if message in response:
        print("✅ test_eliminar_fabricante: PASA")
    else:
        print("❌ test_eliminar_fabricante: FALLA")


async def main():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    await test_listar_almacenes()
    await test_crear_fabricante()
    await test_eliminar_fabricante()

if __name__ == "__main__":
    asyncio.run(main())
