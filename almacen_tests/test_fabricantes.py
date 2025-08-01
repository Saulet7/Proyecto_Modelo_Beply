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

async def test_listar_fabricantes():
    try:
        response = await call_agent_async("Quiero ver todos los fabricantes.")
        api_response = make_fs_request("GET", "/fabricantes")

        if api_response["status"] != "success":
            print("❌ test_listar_fabricantes: ERROR API")
            return

        fabricantes = api_response["data"]
    
        if fabricantes and any(str(a["codfabricante"]).lower() in response for a in fabricantes):
            print("✅ test_listar_fabricantes: PASA")
        else:
            print("❌ test_listar_fabricantes: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_listar_fabricantes: EXCEPCION")

async def test_crear_fabricante():
    try:
        make_fs_request("DELETE", "/fabricantes/8")  # Asegura limpieza previa

        response = await call_agent_async("Agrega un nuevo fabricante con nombre MMMM, solo uno")
        consulta = make_fs_request("GET", "/fabricantes")
        fabricantes = consulta.get("data", [])

        print(response)

        if any(f["nombre"] == "MMMM" for f in fabricantes):
            print("✅ test_crear_fabricante: PASA")
        else:
            print("❌ test_crear_fabricante: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_crear_fabricante: EXCEPCION")

async def test_actualizar_fabricante():
    try:
        # Asegura existencia previa
        response = await call_agent_async("Actualiza el nombre del fabricante MMMM a WWWW, no crees uno nuevo")
        consulta = make_fs_request("GET", "/fabricantes")
        fabricantes = consulta.get("data", [])

        print(response)

        if any(f["nombre"].lower() == "wwww" for f in fabricantes):
            print("✅ test_actualizar_fabricante: PASA")
        else:
            print("❌ test_actualizar_fabricante: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_actualizar_fabricante: EXCEPCION")

async def test_eliminar_fabricante():
    try:
        response = await call_agent_async("Elimina el fabricante WWWW, si no lo encuentras elimina el MMMM el primero que encuentres.")
        consulta = make_fs_request("GET", "/fabricantes")
        fabricantes = consulta.get("data", [])

        existe = False
        for f in fabricantes:
            existe = (f["nombre"] == "WWWW" or f["nombre"] == "MMMM")

        if not existe:
            print("✅ test_eliminar_fabricante: PASA")
        else:
            print("❌ test_eliminar_fabricante: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_eliminar_fabricante: EXCEPCION")

async def main():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    await test_listar_fabricantes()
    await test_crear_fabricante()
    await test_actualizar_fabricante()
    await test_eliminar_fabricante()

if __name__ == "__main__":
    asyncio.run(main())
