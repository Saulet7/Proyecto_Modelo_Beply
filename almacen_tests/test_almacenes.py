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
SESSION_ID = "session_almacenes"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
async def call_agent_async(query: str) -> str:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text.lower()
    return "sin respuesta"

async def test_listar_almacenes():
    try:
        response = await call_agent_async("Enséñame todos los almacenes disponibles.")
        api_response = make_fs_request("GET", "/almacenes")

        if api_response["status"] != "success":
            print("❌ test_listar_almacenes: ERROR API")
            return

        almacenes = api_response["data"]
        if almacenes and any(str(a["codalmacen"]).lower() in response for a in almacenes):
            print("✅ test_listar_almacenes: PASA")
        else:
            print("❌ test_listar_almacenes: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_listar_almacenes: EXCEPCION")

async def test_crear_almacen():
    try:
        cod = "ZZZZ"
        make_fs_request("DELETE", f"/almacenes/{cod}")  # Asegura limpieza previa

        query = (
            f"Crea un almacén nuevo con código {cod}, nombre TestAlmacen, dirección Calle Falsa 123, "
            "ciudad PruebaCity, provincia Ejemplo, código postal 12345, país ES, teléfono 600123123, "
            "idempresa 1 y apartado AL01"
        )
        response = await call_agent_async(query)

        consulta = make_fs_request("GET", "/almacenes")
        almacenes = consulta.get("data", [])

        if any(a["codalmacen"] == cod for a in almacenes):
            print("✅ test_crear_almacen: PASA")
        else:
            print("❌ test_crear_almacen: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_crear_almacen: EXCEPCION")

async def test_actualizar_almacen():
    try:
        cod = "ZZZZ"
        nuevo_nombre = "AlmacenActualizado"

        query = f"Cambia el nombre del almacén con código {cod} a {nuevo_nombre}"
        response = await call_agent_async(query)

        consulta = make_fs_request("GET", "/almacenes")
        almacenes = consulta.get("data", [])

        if any(a["codalmacen"] == cod and a["nombre"] == nuevo_nombre for a in almacenes):
            print("✅ test_actualizar_almacen: PASA")
        else:
            print("❌ test_actualizar_almacen: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_actualizar_almacen: EXCEPCION")

async def test_eliminar_almacen():
    try:
        cod = "ZZZZ"
        query = f"Elimina el almacén con código {cod}, si existe"
        response = await call_agent_async(query)

        consulta = make_fs_request("GET", "/almacenes")
        almacenes = consulta.get("data", [])

        if not any(a["codalmacen"] == cod for a in almacenes):
            print("✅ test_eliminar_almacen: PASA")
        else:
            print("❌ test_eliminar_almacen: FALLA")
            print(f"\033[91mRespuesta del agente: {response}\033[0m")
    except:
        print("❌ test_eliminar_almacen: EXCEPCION")

async def main():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    await test_listar_almacenes()
    await test_crear_almacen()
    await test_actualizar_almacen()
    await test_eliminar_almacen()

if __name__ == "__main__":
    asyncio.run(main())
