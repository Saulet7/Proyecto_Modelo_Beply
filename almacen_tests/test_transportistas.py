import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from tenacity import retry, wait_random_exponential, stop_after_attempt

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import make_fs_request
from almacen_subagentes.agent import root_agent


load_dotenv()

APP_NAME = "Agente_de_transportistaes"
USER_ID = "user_1"
SESSION_ID = "session_transportistas"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
async def call_agent_async(query: str) -> str:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text.lower()
    return "sin respuesta"

async def test_listar_transportistas():
    try:
        response = await call_agent_async("Enséñame todos los transportistas disponibles.")
        api_response = make_fs_request("GET", "/agenciatransportes")

        if api_response["status"] != "success":
            print("❌ test_listar_transportistas: ERROR API")
            return

        transportistas = api_response["data"]
        if transportistas and any(str(a["codtrans"]).lower() in response for a in transportistas):
            print("✅ test_listar_transportistas: PASA")
        else:
            print("❌ test_listar_transportistas: FALLA")
    except:
        print("❌ test_listar_transportistas: FALLA")

async def test_crear_transportista():
    try:
        cod = "ZZZZ"
        make_fs_request("DELETE", f"/agenciatransportes/{cod}")  # Asegura limpieza previa

        query = (
            f"Crea un transportista nuevo con código {cod}, nombre {cod} y que este activo"
        )
        response = await call_agent_async(query)
        print(response)

        consulta = make_fs_request("GET", "/agenciatransportes")
        transportistas = consulta.get("data", [])

        if any(a["codtrans"] == cod for a in transportistas):
            print("✅ test_crear_transportista: PASA")
        else:
            print("❌ test_crear_transportista: FALLA")
    except:
        print("❌ test_crear_transportista: FALLA")

async def test_actualizar_transportista():
    try:
        cod = "ZZZZ"
        nuevo_nombre = "TEST"

        query = f"Cambia el nombre del transportista con código {cod} a {nuevo_nombre}"
        response = await call_agent_async(query)

        consulta = make_fs_request("GET", "/agenciatransportes")
        transportistas = consulta.get("data", [])

        if any(a["codtrans"] == cod and a["nombre"] == nuevo_nombre for a in transportistas):
            print("✅ test_actualizar_transportista: PASA")
        else:
            print("❌ test_actualizar_transportista: FALLA")
    except:
        print("❌ test_actualizar_transportista: FALLA")

async def test_eliminar_transportista():
    try:
        cod = "ZZZZ"
        query = f"Elimina el transportista con código {cod}, si existe"
        response = await call_agent_async(query)

        consulta = make_fs_request("GET", "/agenciatransportes")
        transportistas = consulta.get("data", [])

        if not any(a["codtrans"] == cod for a in transportistas):
            print("✅ test_eliminar_transportista: PASA")
        else:
            print("❌ test_eliminar_transportista: FALLA")
    except:
        print("❌ test_eliminar_transportista: FALLA")

async def main():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    await test_listar_transportistas()
    await test_crear_transportista()
    await test_actualizar_transportista()
    await test_eliminar_transportista()

if __name__ == "__main__":
    asyncio.run(main())
