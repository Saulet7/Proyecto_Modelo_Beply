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

async def test_listar_productos():
    try:
        response = await call_agent_async("Quiero ver todos los productos.")
        api_response = make_fs_request("GET", "/productos")

        if api_response["status"] != "success":
            print("❌ test_listar_productos: ERROR API")
            return

        productos = api_response["data"]
    
        if productos and any(str(a["idproducto"]) in response for a in productos):
            print("✅ test_listar_productos: PASA")
        else:
            print("❌ test_listar_productos: FALLA")
    except:
        print("❌ test_listar_productos: FALLA")

async def test_crear_producto():
    try:
        make_fs_request("DELETE", "/productos/5")  # Asegura limpieza previa

        query = ( f"Agrega un nuevo producto con descripcion productoTEST, solo uno,"
                 "Con precio 5432 euros y referencia TES-111"
        )

        response = await call_agent_async(query)
        consulta = make_fs_request("GET", "/productos")
        productos = consulta.get("data", [])

        print(response)

        if any(f["descripcion"] == "productoTEST" for f in productos):
            print("✅ test_crear_producto: PASA")
        else:
            print("❌ test_crear_producto: FALLA")
    except:
        print("❌ test_crear_producto: FALLA")

async def test_actualizar_producto():
    try:
        # Asegura existencia previa
        response = await call_agent_async("Actualiza la descripcion de la producto productoTEST a PRODUCTO, no crees uno nuevo")
        consulta = make_fs_request("GET", "/productos")
        productos = consulta.get("data", [])

        if any(f["descripcion"].lower() == "producto" for f in productos):
            print("✅ test_actualizar_producto: PASA")
        else:
            print("❌ test_actualizar_producto: FALLA")
    except:
        print("❌ test_actualizar_producto: FALLA")

async def test_eliminar_producto():
    try:
        response = await call_agent_async("Elimina el producto PRODUCTO, si no lo encuentras elimina productoTEST el primero que encuentres.")
        consulta = make_fs_request("GET", "/productos")
        productos = consulta.get("data", [])

        if not any(f["descripcion"].lower() == "producto" for f in productos):
            print("✅ test_eliminar_producto: PASA")
        else:
            print("❌ test_eliminar_producto: FALLA")
    except:
        print("❌ test_eliminar_producto: FALLA")

async def main():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    await test_listar_productos()
    await test_crear_producto()
    await test_actualizar_producto()
    await test_eliminar_producto()

if __name__ == "__main__":
    asyncio.run(main())
