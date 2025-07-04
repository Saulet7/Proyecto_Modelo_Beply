# main.py
from general_flux import agent

# Lista de agentes disponibles en ADK Web
agents = [agent.root_agent]

def main():
    print("💬 Agente de Gestión Financiera Empresarial")
    while True:
        user_input = input("Usuario: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("👋 Finalizando sesión.")
            break

        response = agent.root_agent.run(user_input)
        print(f"Agente: {response}")

if __name__ == "__main__":
    main()
