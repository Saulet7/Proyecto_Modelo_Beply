# Multi-Agent Enterprise ERP Assistant

A modular **multi-agent ERP assistant** powered by Large Language Models (LLMs), designed to automate and manage complex operations within an Enterprise Resource Planning (ERP) system.

The system implements a central **Dispatcher Agent** that classifies natural-language requests and delegates execution to specialized domain agents equipped with domain-specific tools through **function calling**.

---

## System Architecture

The system follows a **Router/Dispatcher + Specialized Sub-Agents** architecture, providing:

* Centralized request routing
* Context isolation between agents
* Modular domain-specific agents
* Specialized tool/function calling
* High scalability and maintainability
* Optimized execution for low-latency interactions

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DISPATCHER AGENT                              │
│                         (Central Orchestrator)                           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
              ┌──────────────┬───────┼────────┬──────────────┐
              │              │       │        │              │
              ▼              ▼       ▼        ▼              ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
        │  Client   │  │  Product  │  │  Invoice  │  │   Stock   │  │ Supplier  │
        │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │
        └───────────┘  └───────────┘  └───────────┘  └───────────┘  └───────────┘
              │              │              │              │              │
              └──────────────┴──────────────┴──────────────┴──────────────┘
                                     │
                                     ▼
                              Specialized Tools
                              & ERP Operations
```

---

## Modules & Specialized Agents

Each ERP domain is handled by a dedicated agent with its own prompting logic, context, and specialized tools.

| Agent / Module          | Directory          | Responsibilities                                                                                         |
| ----------------------- | ------------------ | -------------------------------------------------------------------------------------------------------- |
| **Dispatcher**          | `dispatcher/`      | Evaluates incoming prompts, determines user intent, and routes requests to the appropriate domain agent. |
| **Customer Management** | `cliente/`         | Customer search, creation, and record management.                                                        |
| **Product Management**  | `producto/`        | Product catalog management and product queries.                                                          |
| **Categories**          | `familia/`         | Hierarchical product categorization and family management.                                               |
| **Manufacturers**       | `fabricante/`      | Manufacturer metadata and management.                                                                    |
| **Invoicing**           | `creador_factura/` | Invoice generation, calculations, and tax association.                                                   |
| **Invoice Lines**       | `linea_factura/`   | Line-item management and invoice breakdown.                                                              |
| **Quotes & Estimates**  | `presupuesto/`     | Creation and tracking of commercial offers and proposals.                                                |
| **Stock Management**    | `stock/`           | Inventory lookup, stock movements, traceability, and restocking operations.                              |
| **Supplier Management** | `proveedor/`       | Supplier profiles and purchase order management.                                                         |
| **Reduced Loop**        | `reduced_loop/`    | Optimized execution path for fast, low-latency interactions.                                             |

---

## Project Structure

The project is organized around a central orchestration layer and multiple specialized domain agents.

```text
.
├── main.py                  # Application entry point
├── api.py                   # API integration
├── config.py                # Global configuration
├── data.py                  # Mock database / test data
├── components.py            # Shared components
├── utils.py                 # Utility functions
│
├── dispatcher/              # Central routing agent
│   ├── prompts/
│   ├── tools/
│   └── ...
│
├── cliente/                 # Customer management agent
├── producto/                # Product management agent
├── familia/                 # Product category agent
├── fabricante/              # Manufacturer agent
├── creador_factura/         # Invoice creation agent
├── linea_factura/           # Invoice line management agent
├── presupuesto/             # Quotes and estimates agent
├── stock/                   # Inventory management agent
├── proveedor/               # Supplier management agent
│
├── reduced_loop/            # Optimized execution loop
│
├── requirements.txt         # Python dependencies
└── .env                     # Environment configuration
```

---

## Architecture & Key Concepts

### Multi-Agent System

The application uses a **Multi-Agent System (MAS)** architecture where each agent is responsible for a specific ERP domain.

Instead of relying on a single large agent, responsibilities are distributed across specialized agents, making the system easier to maintain, test, and extend.

### Function Calling / Tool Use

Agents interact with the ERP through specialized tools exposed as callable functions.

This allows the LLM to:

* Query ERP data
* Create and update records
* Perform calculations
* Execute domain-specific operations
* Interact with external APIs

### Dispatcher-Based Routing

The **Dispatcher Agent** acts as the central orchestrator.

It analyzes the user's natural-language request, identifies the intended ERP domain, and delegates execution to the appropriate specialized agent.

For example:

```text
User:
"Show me the current stock of product X"

             │
             ▼
       Dispatcher
             │
             ▼
        Stock Agent
             │
             ▼
      Stock Tool Call
             │
             ▼
        ERP Response
```

### Context Isolation

Each specialized agent operates within its own domain context.

This reduces unnecessary prompt complexity and prevents unrelated domain logic from interfering with the execution of a task.

---

## Tech Stack

| Technology                       | Usage                                        |
| -------------------------------- | -------------------------------------------- |
| **Python 3.10+**                 | Core application language                    |
| **Large Language Models (LLMs)** | Natural-language understanding and reasoning |
| **Function Calling / Tool Use**  | ERP operations and external integrations     |
| **Multi-Agent Architecture**     | Domain specialization and orchestration      |
| **Modular Prompt Engineering**   | Agent-specific behavior and instructions     |
| **REST / API Integration**       | Communication with external services         |

---

## Example Workflow

A typical request follows this execution flow:

```text
Natural Language Request
          │
          ▼
   Dispatcher Agent
          │
          │  Intent classification
          ▼
 Specialized Agent
          │
          │  Tool selection
          ▼
    Function Call
          │
          ▼
      ERP System
          │
          ▼
   Tool Result / Data
          │
          ▼
 Specialized Agent
          │
          ▼
    User Response
```

This architecture makes it possible to add new ERP capabilities without significantly modifying the existing agents.

---

## Extensibility

The system is designed to make new ERP domains easy to integrate.

Adding a new specialized agent generally involves:

1. Creating a new domain module.
2. Defining its prompts and context.
3. Implementing the required tools/function calls.
4. Registering the agent with the Dispatcher.
5. Defining the routing rules for the new domain.

This approach allows the system to evolve incrementally as new ERP requirements are introduced.
