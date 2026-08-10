# Multi-Agent Enterprise ERP Assistant

A modular system based on a multi-agent architecture with Large Language Models (LLMs), designed to automate and manage complex operations within an Enterprise Resource Planning (ERP) system.

The project implements a central orchestrator (Dispatcher) that classifies natural language requests and delegates task execution to specialized agents equipped with domain-specific tools (function calling).

---

## System Architecture

The system utilizes a **Router/Dispatcher + Specialized Sub-Agents** pattern, ensuring context isolation, high scalability, and precise tool call management.

┌─────────────────────────────────────────────────────────────────────────┐
│                               USER INPUT                                │
└────────────────────────────────────┬────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            DISPATCHER AGENT                             │
│                          (Central Orchestrator)                         │
└────────────────────────────────────┬────────────────────────────────────┘
│
┌──────────────┬─────────────┼──────────────┬──────────────┐
│              │             │              │              │
▼              ▼             ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Client   │  │  Product  │  │  Invoice  │  │   Stock   │  │ Supplier  │
│   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │
└───────────┘  └───────────┘  └───────────┘  └───────────┘  └───────────┘  


---

## Modules and Specialized Agents

Each ERP domain has a dedicated agent with its own prompting logic, context, and set of tools:

* **Dispatcher (`dispatcher/`)**: Evaluates incoming prompts, determines user intent, and routes execution to the appropriate domain agent.
* **Customer Management (`cliente/`)**: Search, creation, and querying of customer records.
* **Product and Category Management (`producto/`, `familia/`, `fabricante/`)**: Catalog management, hierarchical categorization, and manufacturer metadata.
* **Invoicing and Invoice Items (`creador_factura/`, `linea_factura/`)**: Invoice generation, amount calculations, line item breakdown, and tax association.
* **Quotes and Estimates (`presupuesto/`)**: Drafting and tracking of commercial offers and proposals.
* **Stock and Warehouse Control (`stock/`)**: Inventory lookup, movement traceability, and restocking operations.
* **Supplier Management (`proveedor/`)**: Administration of vendor profiles and purchase orders.
* **Reduced Loop (`reduced_loop/`)**: An optimized sub-loop tailored for fast interactions and low-latency queries.

---

## Project Structure

* **Core Scripts**: `main.py` (system entry point), `api.py` (API integration), `config.py` (global settings), `data.py` (mock database), `components.py`, and `utils.py`.
* **Central Orchestration**: `dispatcher/` containing the routing agent logic, tools, and prompts.
* **Specialized Sub-Agents**: Separate domain modules for `cliente`, `producto`, `creador_factura`, `linea_factura`, `presupuesto`, `stock`, `proveedor`, `fabricante`, and `familia`.
* **Execution Optimization**: `reduced_loop/` for fast-path, low-latency inference queries.

---

## Tech Stack and Key Concepts

* **Language**: Python 3.10+
* **Design Patterns**: Multi-Agent System (MAS), Function Calling / Tool Use, Modular Prompt Engineering.
* **API Integration**: Endpoints for asynchronous communication and external orchestration.

---

## Installation and Setup

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

2. Create a virtual environment and install dependencies
Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Configure environment variables

Create a .env file in the root directory containing the required keys:
Fragmento de código

API_KEY=your_api_key_here
ENVIRONMENT=development

4. Running the application

To start the agent system via the main entry point:
Bash

python main.py

To run the API service:
Bash

python api.py

Author

Saúl Conejo Mínguez - Software Engineer
