# C4 Architectural Specification & Roadmap

This document defines the system architecture using the C4 Model approach (Level 1: System Context, Level 2: Containers) and maps out the implementation steps.

---

## 1. C4 Level 1: System Context
Defines the boundaries of the Smart Procurement Engine and how users and external systems interact with it.

```mermaid
graph LR
    User([Procurement Manager]) --- HTTP ---> System[Smart Procurement Engine Monolith]
    System --- REST/HTTP ---> Retailers[External Retailer Systems / Mock Catalogs]
    System --- API/HTTP ---> LLM[External LLM Service: OpenAI / Ollama]

    style User fill:#08427b,stroke:#052e56,color:#fff
    style System fill:#1168bd,stroke:#0b4c8c,color:#fff
    style Retailers fill:#999999,stroke:#666666,color:#fff
    style LLM fill:#999999,stroke:#666666,color:#fff
```

### Context Elements:
*   **User:** Enters text procurement requests, uploads custom files, and receives optimal purchasing recommendations.
*   **Smart Procurement Engine:** The core system under development. Processes text, queries inventory, and optimizes baskets.
*   **Retailer Systems:** External endpoints providing product catalogs, stock levels, and real-time prices.
*   **LLM Service:** External AI model used for structural NLP parsing and fuzzy catalog matching.

---

## 2. C4 Level 2: Containers
Defines the internal high-level technical blocks of the monolith application and the data schema logic.

```mermaid
graph TB
    subgraph Smart Procurement Engine Monolith
        UI[Streamlit Web App Component] -- Python Calls --> Core[BestPrices Core Engine]
        Core -- SQL/Pandas --> DB[(Mock DB: Pandas DataFrames / CSV)]
        
        subgraph Core Engine Components
            Core -- Internal Call --> RetConn[Retailer Connector]
            Core -- Internal Call --> AIConn[LLM Connector Agent]
        end
    end

    User([User / Manager]) -- HTTP ---> UI
    RetConn -- REST / Local File Read ---> RetailerData[(Vendor Catalog Data)]
    AIConn -- JSON over HTTPS ---> ExternalLLM((OpenAI / Ollama API))

    style User fill:#08427b,stroke:#052e56,color:#fff
    style UI fill:#2b7db3,stroke:#1a5c8a,color:#fff
    style Core fill:#2b7db3,stroke:#1a5c8a,color:#fff
    style DB fill:#339933,stroke:#226622,color:#fff
    style RetConn fill:#4393c3,stroke:#2166ac,color:#fff
    style AIConn fill:#4393c3,stroke:#2166ac,color:#fff
    style RetailerData fill:#999999,stroke:#666666,color:#fff
    style ExternalLLM fill:#999999,stroke:#666666,color:#fff
```

### Container Responsibilities:
1.  **Streamlit Web App:** Presentation layer. Form for user prompt entry, file upload buttons, and tables showing results.
2.  **BestPrices Core Engine:** Orchestration layer. Controls execution flow: receives query -> calls LLM -> searches prices -> matches entities -> optimizes.
3.  **Mock DB (CSV/Pandas):** Storage layer. Holds local tables: `Users`, `User_Requests`, and cache of `Retailer_Prices`.
4.  **Retailer Connector:** Integration block. Reads vendor data formats and normalizes them.
5.  **LLM Connector Agent:** Intelligence block. Manages prompt templates, chat history, and schemas for data structure enforcement.
