# Simple Architecture Diagram (Fallback for Mermaid compatibility)

```mermaid
graph TD
    User[👤 User] --> Streamlit[🌐 Streamlit Web UI]
    Streamlit --> APIGateway[🚪 API Gateway]
    APIGateway --> AgentCore[🤖 Amazon Bedrock AgentCore]
    
    AgentCore --> NovaLLM[🧠 Amazon Nova Pro LLM]
    AgentCore --> RiskAgent[📊 Risk Analysis Agent]
    AgentCore --> AlertAgent[⚠️ Alert Generation Agent]
    
    AgentCore --> Lambda[⚙️ AWS Lambda]
    Lambda --> Copernicus[🌊 Copernicus Marine API]
    Lambda --> OpenMeteo[🌤️ Open-Meteo Marine API]
    Lambda --> S3[💾 Amazon S3]
    
    S3 --> RiskAgent
    RiskAgent --> AlertAgent
    AlertAgent --> AgentCore
    
    AgentCore --> CloudWatch[📈 CloudWatch & X-Ray]
    
    AgentCore --> APIGateway
    APIGateway --> Streamlit
    Streamlit --> User
    
    style User fill:#e1f5ff,stroke:#01579b
    style Streamlit fill:#e1f5ff,stroke:#01579b
    style AgentCore fill:#9c27b0,stroke:#6a1b9a
    style NovaLLM fill:#9c27b0,stroke:#6a1b9a
    style RiskAgent fill:#9c27b0,stroke:#6a1b9a
    style AlertAgent fill:#9c27b0,stroke:#6a1b9a
    style Lambda fill:#ff9900,stroke:#ff6600
    style S3 fill:#ff5722,stroke:#d84315
    style Copernicus fill:#4caf50,stroke:#2e7d32
    style OpenMeteo fill:#4caf50,stroke:#2e7d32
    style CloudWatch fill:#607d8b,stroke:#455a64
```

**Legend:**
- 🔵 Blue = User Interface Layer
- 🟣 Purple = AI Agent Layer (Bedrock AgentCore)
- 🟠 Orange = AWS Services (Lambda, API Gateway)
- 🔴 Red = Storage (S3)
- 🟢 Green = External APIs
- ⚫ Gray = Observability (CloudWatch/X-Ray)
