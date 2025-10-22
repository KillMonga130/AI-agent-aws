"""
Enhanced Architecture Diagram for Ocean Forecasting Agent
AWS AI Agent Global Hackathon Submission
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.ml import Sagemaker
from diagrams.onprem.client import User
from diagrams.programming.language import Python
from diagrams.onprem.network import Internet

def create_diagram():
    """Generate comprehensive architecture diagram"""
    
    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "dpi": "300"
    }
    
    with Diagram("\n\nAutonomous Ocean Forecasting Agent\nAWS AI Agent Architecture\n\n", 
                 filename="architecture_diagram",
                 show=False,
                 direction="TB",
                 graph_attr=graph_attr,
                 outformat="png"):
        
        # Top Layer - Users
        user = User("Maritime Operators\nFleet Managers\nPort Authorities")
        
        # UI Layer
        with Cluster("Frontend Layer"):
            streamlit = Python("Streamlit Web App\nDemo & Production Modes")
        
        # Core AI Agent Layer
        with Cluster("Amazon Bedrock AgentCore Runtime", graph_attr={"bgcolor": "lightblue"}):
            with Cluster("Strands Multi-Agent System"):
                agent_core = Sagemaker("Main Agent\n(Amazon Nova Pro LLM)")
                
                with Cluster("Agent Tools (Python @tool decorators)"):
                    tool1 = Python("Tool 1:\nfetch_current_ocean_data()")
                    tool2 = Python("Tool 2:\nanalyze_maritime_risks()")
                    tool3 = Python("Tool 3:\ngenerate_forecast_alert()")
        
        # AWS Services Layer
        with Cluster("AWS Backend Services", graph_attr={"bgcolor": "lightyellow"}):
            lambda_fn = Lambda("Data Ingestion Lambda\nPython 3.9 | 512MB | 60s timeout")
            s3_bucket = S3("S3 Bucket\nocean-forecast-data-911167913661\nJSON Data Storage")
        
        # External APIs
        with Cluster("External Ocean Data Sources", graph_attr={"bgcolor": "lightgreen"}):
            api1 = Internet("Copernicus Marine Service\nOcean Currents | SSH | Temperature")
            api2 = Internet("Open-Meteo Marine API\nWave Heights | 5-Day Forecasts")
        
        # === Data Flow Connections ===
        
        # User to UI
        user >> Edge(label="1. Submit Query\n(location + question)", color="blue", style="bold") >> streamlit
        
        # UI to Agent
        streamlit >> Edge(label="2. Invoke Agent", color="blue", style="bold") >> agent_core
        
        # Agent uses tools
        agent_core >> Edge(label="3a. Call Tool 1", color="green") >> tool1
        agent_core >> Edge(label="3b. Call Tool 2", color="green") >> tool2
        agent_core >> Edge(label="3c. Call Tool 3", color="green") >> tool3
        
        # Tool 1 triggers Lambda
        tool1 >> Edge(label="4. Trigger Lambda", color="orange") >> lambda_fn
        
        # Lambda fetches from APIs
        lambda_fn >> Edge(label="5a. Fetch Real-Time Data", color="red") >> api1
        lambda_fn >> Edge(label="5b. Fetch Weather Data", color="red") >> api2
        
        # Lambda stores in S3
        lambda_fn >> Edge(label="6. Store JSON", color="orange") >> s3_bucket
        
        # Tool retrieves from S3
        s3_bucket >> Edge(label="7. Retrieve Historical Data", color="orange") >> tool1
        
        # Tools pass data
        tool1 >> Edge(label="8. Ocean Data", color="green") >> tool2
        tool2 >> Edge(label="9. Risk Analysis", color="green") >> tool3
        
        # Results back to agent
        tool3 >> Edge(label="10. Alert Response", color="green") >> agent_core
        
        # Response to UI
        agent_core >> Edge(label="11. AI Response", color="blue", style="bold") >> streamlit
        
        # Display to user
        streamlit >> Edge(label="12. Display Results", color="blue", style="bold") >> user

if __name__ == "__main__":
    print("🎨 Generating architecture diagram...")
    print("=" * 60)
    
    try:
        create_diagram()
        print("\n✅ SUCCESS! Diagram saved as: architecture_diagram.png")
        print("📍 Location: ./architecture_diagram.png")
        print("\n📊 Diagram shows:")
        print("  • User interaction flow")
        print("  • Amazon Bedrock AgentCore with Nova Pro")
        print("  • 3 Agent Tools with @tool decorators")
        print("  • AWS Lambda data ingestion")
        print("  • S3 storage for historical data")
        print("  • External API integrations")
        print("  • Complete 12-step data flow")
        
    except FileNotFoundError as e:
        print("\n❌ ERROR: Graphviz not found!")
        print("\n🔧 SOLUTION:")
        print("  1. Download Graphviz from: https://graphviz.org/download/")
        print("  2. For Windows: Download 'stable_windows_10_cmake_Release' ZIP")
        print("  3. Extract and add 'bin' folder to PATH")
        print("  4. Restart terminal and run script again")
        print(f"\n   Original error: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n💡 Alternative: Use online tool (Excalidraw.com) to create diagram manually")

    print("=" * 60)
