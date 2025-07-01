import google.adk
import sys

print("--- Verificación del Entorno ADK ---")
print(f"Versión de google-adk: {google.adk.__version__}")
print(f"Ubicación de google-adk: {google.adk.__file__}")
print(f"Ejecutable de Python: {sys.executable}")
print("-------------------------------------")