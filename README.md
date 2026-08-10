Multi-Agent Enterprise ERP Assistant

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

.
├── api.py                   # API entry point & endpoints
├── main.py                  # Core system entry point
├── config.py                # Environment & global settings
├── components.py            # Reusable UI & shared logic components
├── data.py                  # Mock database & persistence layer
├── utils.py                 # Utility & helper functions
│
├── dispatcher/              # Central Orchestrator Agent
│   ├── agent.py             # Dispatcher routing logic
│   ├── prompt.py            # Intent classification prompts
│   └── tools.py             # Delegation tools
│
├── cliente/                 # Customer Management Agent
├── producto/                # Product Management Agent
├── creador_factura/         # Invoice Generation Agent
├── linea_factura/           # Invoice Line Items Agent
├── presupuesto/             # Commercial Quotes Agent
├── stock/                   # Inventory & Warehouse Agent
├── proveedor/               # Supplier Management Agent
├── fabricante/              # Manufacturer Metadata Agent
├── familia/                 # Product Category Agent
└── reduced_loop/            # High-speed inference sub-loopMulti-Agent Enterprise ERP Assistant

A modular system based on a multi-agent architecture with Large Language Models (LLMs), designed to automate and manage complex operations within an Enterprise Resource Planning (ERP) system.

The project implements a central orchestrator (Dispatcher) that classifies natural language requests and delegates task execution to specialized agents equipped with domain-specific tools (function calling).
System Architecture

The system utilizes a Router/Dispatcher + Specialized Sub-Agents pattern, ensuring context isolation, high scalability, and precise tool call management.

                      +----------------------+
                      |      User Input      |
                      +----------+-----------+
                                 |
                                 v
                     +------------------------+
                     |    Dispatcher Agent    |
                     |  (Central Orchestrator)|
                     +-----------+------------+
                                 |
    +--------------+-------------+--------------+--------------+
    |              |             |              |              |
    v              v             v              v              v
+--------+    +---------+   +---------+   +----------+   +-----------+
| Client |    | Product |   | Invoice |   |  Stock   |   | Suppliers | ...
| Agent  |    | Agent   |   | Agent   |   |  Agent   |   |   Agent   |
+--------+    +---------+   +---------+   +----------+   +-----------+

Modules and Specialized Agents

Each ERP domain has a dedicated agent with its own prompting logic, context, and set of tools:

    Dispatcher (dispatcher/): Evaluates incoming prompts, determines user intent, and routes execution to the appropriate domain agent.

    Customer Management (cliente/): Search, creation, and querying of customer records.

    Product and Category Management (producto/, familia/, fabricante/): Catalog management, hierarchical categorization, and manufacturer metadata.

    Invoicing and Invoice Items (creador_factura/, linea_factura/): Invoice generation, amount calculations, line item breakdown, and tax association.

    Quotes and Estimates (presupuesto/): Drafting and tracking of commercial offers and proposals.

    Stock and Warehouse Control (stock/): Inventory lookup, movement traceability, and restocking operations.

    Supplier Management (proveedor/): Administration of vendor profiles and purchase orders.

    Reduced Loop (reduced_loop/): An optimized sub-loop tailored for fast interactions and low-latency queries.

Project Structure
Plaintext

.
├── api.py               # Entry point / API interface
├── main.py              # Main application execution
├── config.py            # Global configuration and environment variables
├── components.py        # Reusable UI components / Shared logic
├── data.py              # Data layer / Mock Database
├── utils.py             # Utility functions
│
├── dispatcher/          # Central Orchestrator Agent
│   ├── agent.py
│   ├── prompt.py
│   └── tools.py
│
├── cliente/             # Customer Management Agent
├── producto/            # Product Management Agent
├── creador_factura/     # Invoice Generator Agent
├── linea_factura/       # Invoice Line Items Agent
├── presupuesto/         # Quotes & Estimates Agent
├── stock/               # Inventory & Warehouse Agent
├── proveedor/           # Supplier Management Agent
├── fabricante/          # Manufacturer Management Agent
├── familia/             # Product Family / Category Agent
└── reduced_loop/        # Optimized Inference Loop

Tech Stack and Key Concepts

    Language: Python 3.10+

    Design Patterns: Multi-Agent System (MAS), Function Calling / Tool Use, Modular Prompt Engineering.

    API Integration: Endpoints for asynchronous communication and external orchestration.
