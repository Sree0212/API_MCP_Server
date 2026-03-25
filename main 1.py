from fastmcp import FastMCP
import logging

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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# MCP INIT
# =========================================================
mcp = FastMCP("PhaseBasedMCP")

# =========================================================
# REGISTER CORE TOOLS
# =========================================================
base_tools_registration(mcp)
generation_agent_prompts(mcp)
tsu_tools_registration(mcp)
testcase_tools_registration(mcp)
locator_tools_registration(mcp)

# =========================================================
# REGISTER API TOOLS
# =========================================================
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
        capture_response,
    )

intelligence_tool = init_intelligence_tool("C:/Projects/Agentic/Artefacts")

@mcp.tool()
def analyze_api(input_data: dict):
    return intelligence_tool.analyze(input_data)

discovery_tool = init_discovery_tool("C:/Projects/Agentic/Artefacts")

@mcp.tool()
def discover_api(project_name: str):
    return discovery_tool.discover(project_name)

# =========================================================
# SUB-SERVER
# =========================================================
sub_server = FastMCP("SubMCP")

@sub_server.tool()
def greet(name: str) -> str:
    return f"Hello, {name} from SubMCP!"

mcp.mount("sub", sub_server)

# =========================================================
# SERVER START
# =========================================================
if __name__ == "__main__":
    logger.info("Starting MCP server on http://127.0.0.1:3333/mcp")
    mcp.run(transport="http", host="127.0.0.1", port=3333)
