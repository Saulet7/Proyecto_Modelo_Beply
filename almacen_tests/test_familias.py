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
from almacen_simple.agent import root_agent

load_dotenv()

APP_NAME = "Agente_de_almacenes"
USER_ID = "user_1"
SESSION_ID = "session_001"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
async def call_agent_async(query: str) -> str:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text.lower()
    return "sin respuesta"

async def test_listar_familias():
    try:
        response = await call_agent_async("Quiero ver todas las familias.")
        api_response = make_fs_request("GET", "/familias")

        if api_response["status"] != "success":
            print("❌ test_listar_familias: ERROR API")
            return

        familias = api_response["data"]
    
        if familias and any(str(a["codfamilia"]).lower() in response for a in familias):
            print("✅ test_listar_familias: PASA")
        else:
            print("❌ test_listar_familias: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_listar_familias: EXCEPCION")

async def test_crear_familia():
    try:
        make_fs_request("DELETE", "/familias/5")  # Asegura limpieza previa

        response = await call_agent_async("Agrega un nuevo familia con descripcion animal, solo uno")
        consulta = make_fs_request("GET", "/familias")
        familias = consulta.get("data", [])

        if any(f["descripcion"] == "animal" for f in familias):
            print("✅ test_crear_familia: PASA")
        else:
            print("❌ test_crear_familia: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_crear_familia: EXCEPCION")

async def test_actualizar_familia():
    try:
        # Asegura existencia previa
        response = await call_agent_async("Actualiza la descripcion de la familia animal a fruta, no crees uno nuevo")
        consulta = make_fs_request("GET", "/familias")
        familias = consulta.get("data", [])

        if any(f["descripcion"].lower() == "fruta" for f in familias):
            print("✅ test_actualizar_familia: PASA")
        else:
            print("❌ test_actualizar_familia: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_actualizar_familia: EXCEPCION")

async def test_eliminar_familia():
    try:
        response = await call_agent_async("Elimina la familia fruta, si no lo encuentras elimina animal el primero que encuentres.")
        consulta = make_fs_request("GET", "/familias")
        familias = consulta.get("data", [])

        if not any(f["descripcion"].lower() == "fruta" for f in familias):
            print("✅ test_eliminar_familia: PASA")
        else:
            print("❌ test_eliminar_familia: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_eliminar_familia: EXCEPCION")

async def main():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    await test_listar_familias()
    await test_crear_familia()
    await test_actualizar_familia()
    await test_eliminar_familia()

if __name__ == "__main__":
    asyncio.run(main())
