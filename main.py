from fastmcp import FastMCP
import logging
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import threading
import time

# Tool Registrations
from tools.base import base_tools_registration
from tools.locator_tools import locator_tools_registration
from tools.tsu_tools import tsu_tools_registration
from tools.testcase_tools import testcase_tools_registration
from core.prompts import generation_agent_prompts

# API Tools
from tools.api_execution_tool import init_execution_tool
from tools.api_intelligence_tool import init_intelligence_tool
from tools.api_discovery_tool import init_discovery_tool

# FastMCP Provider imports (NEW)
from fastmcp.server.providers import FastMCPProvider
from fastmcp.server.transforms import Namespace

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("PhaseBasedMCP")

# REGISTER CORE TOOLS
base_tools_registration(mcp)
generation_agent_prompts(mcp)
tsu_tools_registration(mcp)
testcase_tools_registration(mcp)
locator_tools_registration(mcp)

# REGISTER API TOOLS

# 1. Execution Tool (needs instance)
execution_tool = init_execution_tool("C:/Projects/Agentic/Artefacts")

@mcp.tool()
def execute_api(
    endpoint: dict,
    dataset: dict,
    base_url: str = None,
    auto_heal: bool = False,
    capture_response: bool = False,
):
    return execution_tool.execute_api(
        endpoint,
        dataset,
        base_url,
        auto_heal,
        capture_response
    )

intelligence_tool = init_intelligence_tool("C:/Projects/Agentic/Artefacts")
@mcp.tool()
def analyze_api(input_data: dict):
    return intelligence_tool.analyze(input_data)

discovery_tool = init_discovery_tool("C:/Projects/Agentic/Artefacts")
@mcp.tool()
def discover_api(project_name: str):
    return discovery_tool.discover(project_name)

sub_server = FastMCP("SubMCP")

@sub_server.tool
def greet(name: str) -> str:
    return f"Hello, {name} from SubMCP!"

# Wrap child server in provider
provider = FastMCPProvider(sub_server)

# Optional namespace to avoid conflicts
provider.add_transform(Namespace("sub"))

# Mount provider onto main MCP
mcp.add_provider(provider)


if __name__ == "__main__":
    logger.info("Starting MCP server with CORS proxy...")

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Run MCP server internally
    def run_mcp_server():
        mcp.run(
            transport="http",
            host="127.0.0.1",
            port=3334
        )

    mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
    mcp_thread.start()

    time.sleep(2)

    @app.api_route("/mcp", methods=["GET", "POST", "OPTIONS"])
    @app.api_route("/mcp/{path:path}", methods=["GET", "POST", "OPTIONS"])
    async def proxy_mcp(request: Request, path: str = ""):
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        url = f"http://127.0.0.1:3334/mcp"
        if path:
            url += f"/{path}"

        timeout = httpx.Timeout(300.0, connect=60.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = dict(request.headers)
            headers.pop("host", None)

            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

    logger.info("CORS proxy running on http://127.0.0.1:3333")
    logger.info("Connect MCP Inspector to: http://127.0.0.1:3333/mcp")

    uvicorn.run(app, host="127.0.0.1", port=3333)