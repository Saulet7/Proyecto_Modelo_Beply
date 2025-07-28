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
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
async def call_agent_async(query: str) -> str:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text.lower()
    return "sin respuesta"

async def test_listar_almacenes():
    response = await call_agent_async("Quiero ver todos los almacenes.")
    api_response = make_fs_request("GET", "/almacenes")

    if api_response["status"] != "success":
        print("❌ test_listar_almacenes: ERROR API")
        return
    
    print(response)

    almacenes = api_response["data"]
    if almacenes and any(str(a["codalmacen"]).lower() in response for a in almacenes):
        print("✅ test_listar_almacenes: PASA")
    else:
        print("❌ test_listar_almacenes: FALLA")

async def test_crear_fabricante():
    make_fs_request("DELETE", "/fabricantes/8")  # Asegura limpieza previa

    response = await call_agent_async("Agrega un nuevo fabricante con nombre MMMM y código 8.")
    consulta = make_fs_request("GET", "/fabricantes", params={"codfabricante": "8"})
    fabricantes = consulta.get("data", [])

    for f in fabricantes: print(f["nombre"])

    if any(f["nombre"] == "MMMM" for f in fabricantes):
        print("✅ test_crear_fabricante: PASA")
    else:
        print("❌ test_crear_fabricante: FALLA")

async def test_actualizar_fabricante():
    # Asegura existencia previa
    make_fs_request("POST", "/fabricantes", data={"nombre": "MMMM", "codigo": "8"})

    response = await call_agent_async("Actualiza el nombre del fabricante con código 8 a WWWW.")
    consulta = make_fs_request("GET", "/fabricantes", params={"codfabricante": "8"})
    fabricantes = consulta.get("data", [])

    if any(f["nombre"].lower() == "WWWW" for f in fabricantes):
        print("✅ test_actualizar_fabricante: PASA")
    else:
        print("❌ test_actualizar_fabricante: FALLA")

async def test_eliminar_fabricante():
    response = await call_agent_async("Elimina el fabricante WWW.")
    consulta = make_fs_request("GET", "/fabricantes")
    fabricantes = consulta.get("data", [])

    existe = False
    for f in fabricantes:
        existe = (f["nombre"] == "WWW")

    if existe:
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
    #await test_crear_fabricante()
    #await test_actualizar_fabricante()
    #await test_eliminar_fabricante()

if __name__ == "__main__":
    asyncio.run(main())
