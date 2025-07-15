from google.genai.types import GenerationConfig

# Definir el modelo a utilizar
MODEL_GEMINI_2_0_FLASH = "gemini-2.5-flash"

# Configuración estándar para generación de contenido
DEFAULT_GENERATION_CONFIG = GenerationConfig(
    temperature=0.2,
    top_p=0.8,
    top_k=40,
    max_output_tokens=1024,
)