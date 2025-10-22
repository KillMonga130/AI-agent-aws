"""
Create Architecture Diagram using Python diagrams library
For AWS AI Agent Global Hackathon submission
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.onprem.network import Internet

# Note: This requires graphviz installed
# Windows: choco install graphviz
# Mac: brew install graphviz
# Linux: sudo apt-get install graphviz

with Diagram("Autonomous Ocean Forecasting Agent Architecture", 
             filename="architecture_diagram",
             show=False,
             direction="TB"):
    
    # User Interface
    user = User("Maritime Operators")
    
    with Cluster("Streamlit Web Interface"):
        ui = Custom("Web Dashboard", "./streamlit_icon.png") if False else User("Web UI")
    
    # AgentCore Cluster
    with Cluster("Amazon Bedrock AgentCore Runtime"):
        with Cluster("Strands Multi-Agent System"):
            agent = Bedrock("Amazon Nova Pro\nReasoning LLM")
            
            with Cluster("Agent Tools"):
                tool1 = Lambda("fetch_ocean_data")
                tool2 = Lambda("analyze_risks")
                tool3 = Lambda("generate_alert")
    
    # Data Layer
    with Cluster("Data Ingestion Layer"):
        lambda_fn = Lambda("Data Ingestion\nLambda")
        s3 = S3("Historical\nOcean Data")
    
    # External APIs
    with Cluster("External Data Sources"):
        copernicus = Internet("Copernicus\nMarine Service")
        openmeteo = Internet("Open-Meteo\nMarine API")
    
    # Data Flow
    user >> Edge(label="query") >> ui
    ui >> Edge(label="invoke") >> agent
    
    agent >> Edge(label="call tools") >> tool1
    tool1 >> Edge(label="trigger") >> lambda_fn
    
    lambda_fn >> Edge(label="fetch") >> copernicus
    lambda_fn >> Edge(label="fetch") >> openmeteo
    lambda_fn >> Edge(label="store") >> s3
    
    s3 >> Edge(label="retrieve") >> tool1
    tool1 >> Edge(label="data") >> tool2
    tool2 >> Edge(label="risks") >> tool3
    tool3 >> Edge(label="alert") >> agent
    
    agent >> Edge(label="response") >> ui
    ui >> Edge(label="display") >> user

print("✅ Architecture diagram created: architecture_diagram.png")
