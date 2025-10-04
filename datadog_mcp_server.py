import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

import requests
from mcp import McpServer, NotificationOptions, types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import uvicorn
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('datadog_mcp_server.log')
    ]
)
logger = logging.getLogger("datadog-mcp-server")

class DatadogScraperMcpServer:
    """MCP Server for Datadog Documentation Scraper integration"""

    def __init__(self):
        self.scraper_url = os.getenv("SCRAPER_URL", "http://localhost:8000")
        self.server = Server("datadog-scraper-mcp")

        # FastAPI app for HTTP interface
        self.app = FastAPI(title="Datadog MCP Server", version="1.0.0")

    def _setup_http_routes(self):
        """Setup FastAPI routes for HTTP interface"""

        @self.app.get("/")
        async def root():
            return {
                "name": "Datadog MCP Server",
                "version": "1.0.0",
                "mcp_enabled": True,
                "scraper_url": self.scraper_url
            }

        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "datadog-mcp-server",
                "scraper_connected": self._check_scraper_health()
            }

        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools"""
            return {
                "tools": [
                    "scrape_datadog_docs",
                    "get_scraping_status",
                    "get_scraping_results",
                    "search_documentation",
                    "get_documentation_tree",
                    "export_scraping_data"
                ]
            }

    def _check_scraper_health(self) -> bool:
        """Check if scraper service is accessible"""
        try:
            response = requests.get(f"{self.scraper_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
        """Execute scraping operation via HTTP API"""
        try:
            response = requests.post(
                f"{self.scraper_url}/scrape",
                json={
                    "max_depth": max_depth,
                    "delay": delay,
                    "save_results": save_results
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start scraping: {e}")
            raise Exception(f"Scraping request failed: {e}")

    async def get_scraping_status(self) -> Dict[str, Any]:
        """Get current scraping status"""
        try:
            response = requests.get(f"{self.scraper_url}/status", timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get status: {e}")
            raise Exception(f"Status request failed: {e}")

    async def get_scraping_results(self, format_type: str = "json") -> Dict[str, Any]:
        """Get scraping results in specified format"""
        try:
            response = requests.get(f"{self.scraper_url}/results", timeout=10)
            response.raise_for_status()
            data = response.json()

            if format_type == "summary":
                return {
                    "total_links": data.get("total_links", 0),
                    "scraping_time": data.get("scraping_time", 0),
                    "timestamp": data.get("timestamp"),
                    "sample_links": data.get("links", [])[:5]
                }

            elif format_type == "links":
                return {
                    "links": data.get("links", []),
                    "total_count": len(data.get("links", []))
                }

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get results: {e}")
            raise Exception(f"Results request failed: {e}")

    async def search_documentation(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search through scraped documentation"""
        try:
            # Get all results first
            results = await self.get_scraping_results("links")
            links = results.get("links", [])

            # Simple text search through URLs and cached content
            matches = []
            query_lower = query.lower()

            for link in links[:max_results * 2]:  # Get more to filter
                if (query_lower in link.lower()):
                    matches.append({
                        "url": link,
                        "relevance_score": 1.0,  # Simple scoring
                        "matched_by": "url_contains"
                    })

            # Sort by relevance and limit results
            matches.sort(key=lambda x: x["relevance_score"], reverse=True)
            return matches[:max_results]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise Exception(f"Documentation search failed: {e}")

    async def get_documentation_tree(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get hierarchical tree structure"""
        try:
            results = await self.get_scraping_results("json")
            tree = results.get("tree", {})

            # Limit tree depth if specified
            if max_depth > 0:
                tree = self._limit_tree_depth(tree, max_depth)

            return {
                "tree": tree,
                "max_depth": max_depth,
                "total_nodes": self._count_tree_nodes(tree)
            }

        except Exception as e:
            logger.error(f"Tree retrieval failed: {e}")
            raise Exception(f"Documentation tree retrieval failed: {e}")

    def _limit_tree_depth(self, tree: Dict, max_depth: int, current_depth: int = 0) -> Dict:
        """Recursively limit tree depth"""
        if current_depth >= max_depth:
            return {}

        limited_tree = {}
        for key, value in tree.items():
            if isinstance(value, list):
                limited_tree[key] = [
                    {k: v for k, v in item.items() if k != 'children'}
                    for item in value
                ]
            elif isinstance(value, dict):
                limited_tree[key] = self._limit_tree_depth(value, max_depth, current_depth + 1)

        return limited_tree

    def _count_tree_nodes(self, tree: Dict) -> int:
        """Count total nodes in tree"""
        count = 0
        for key, value in tree.items():
            count += 1  # Count the key itself
            if isinstance(value, (dict, list)):
                # Recursively count nested items
                if isinstance(value, dict):
                    count += self._count_tree_nodes(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            count += len(item)
        return count

    async def export_scraping_data(self, format_type: str = "json", include_metadata: bool = True) -> str:
        """Export scraping data in various formats"""
        try:
            results = await self.get_scraping_results("json")

            if format_type == "json":
                return json.dumps(results, indent=2)

            elif format_type == "csv":
                # Convert links to CSV format
                links = results.get("links", [])
                csv_data = "URL,Index\n"
                for i, link in enumerate(links, 1):
                    csv_data += f'"{link}",{i}\n'
                return csv_data

            elif format_type == "markdown":
                # Generate markdown report
                total_links = results.get("total_links", 0)
                scraping_time = results.get("scraping_time", 0)
                links = results.get("links", [])

                md = f"""# Datadog Documentation Scraping Report

## Summary
- **Total Links Found:** {total_links}
- **Scraping Time:** {scraping_time:.2f} seconds
- **Timestamp:** {results.get('timestamp', 'Unknown')}

## Links ({min(50, len(links))} of {len(links)} shown)

"""

                for i, link in enumerate(links[:50], 1):
                    md += f"{i}. {link}\n"

                if len(links) > 50:
                    md += f"\n... and {len(links) - 50} more links"

                return md

            elif format_type == "html":
                # Generate HTML report
                total_links = results.get("total_links", 0)
                links = results.get("links", [])

                html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Datadog Documentation Scraping Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .links {{ max-height: 600px; overflow-y: auto; }}
        .link {{ margin: 5px 0; padding: 8px; background: #f9f9f9; border-left: 3px solid #007acc; }}
    </style>
</head>
<body>
    <h1>Datadog Documentation Scraping Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Links Found:</strong> {total_links}</p>
        <p><strong>Scraping Time:</strong> {results.get('scraping_time', 0):.2f} seconds</p>
        <p><strong>Timestamp:</strong> {results.get('timestamp', 'Unknown')}</p>
    </div>

    <div class="links">
        <h2>Links ({min(100, len(links))} of {len(links)} shown)</h2>
"""

                for i, link in enumerate(links[:100], 1):
                    html += f'        <div class="link">{i}. <a href="{link}" target="_blank">{link}</a></div>\n'

                if len(links) > 100:
                    html += f'        <p>... and {len(links) - 100} more links</p>\n'

                html += """    </div>
</body>
</html>"""

                return html

            else:
                raise ValueError(f"Unsupported format: {format_type}")

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise Exception(f"Data export failed: {e}")

async def main():
    """Main MCP server function"""
    server = DatadogScraperMcpServer()

    # Register tools
    @server.server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="scrape_datadog_docs",
                description="Scrape Datadog documentation and return structured data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_depth": {"type": "integer", "description": "Maximum scraping depth (1-3)", "default": 2},
                        "delay": {"type": "number", "description": "Delay between requests in seconds", "default": 0.5},
                        "save_results": {"type": "boolean", "description": "Whether to save results to files", "default": True}
                    },
                    "required": ["max_depth"]
                }
            ),
            types.Tool(
                name="get_scraping_status",
                description="Get current scraping status and progress",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="get_scraping_results",
                description="Retrieve the latest scraping results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["json", "summary", "links"], "description": "Output format", "default": "json"}
                    }
                }
            ),
            types.Tool(
                name="search_documentation",
                description="Search scraped documentation for specific content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "description": "Maximum number of results", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_documentation_tree",
                description="Get hierarchical tree structure of scraped documentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_depth": {"type": "integer", "description": "Maximum tree depth to return", "default": 3}
                    }
                }
            ),
            types.Tool(
                name="export_scraping_data",
                description="Export scraping data in various formats",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["json", "csv", "markdown", "html"], "description": "Export format", "default": "json"},
                        "include_metadata": {"type": "boolean", "description": "Include scraping metadata", "default": True}
                    },
                    "required": ["format"]
                }
            )
        ]

    @server.server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool execution"""
        try:
            if name == "scrape_datadog_docs":
                result = await server.run_scraping_operation(
                    max_depth=arguments.get("max_depth", 2),
                    delay=arguments.get("delay", 0.5),
                    save_results=arguments.get("save_results", True)
                )
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_scraping_status":
                result = await server.get_scraping_status()
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_scraping_results":
                result = await server.get_scraping_results(arguments.get("format", "json"))
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "search_documentation":
                result = await server.search_documentation(
                    arguments["query"],
                    arguments.get("max_results", 10)
                )
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_documentation_tree":
                result = await server.get_documentation_tree(arguments.get("max_depth", 3))
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "export_scraping_data":
                result = await server.export_scraping_data(
                    arguments["format"],
                    arguments.get("include_metadata", True)
                )
                return [types.TextContent(type="text", text=result)]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Register resources
    @server.server.read_resource()
    async def handle_read_resource(uri: str) -> str:
        """Handle resource reading"""
        if uri == "datadog://scraping-status":
            status = await server.get_scraping_status()
            return json.dumps(status, indent=2)

        elif uri == "datadog://latest-results":
            results = await server.get_scraping_results("summary")
            return json.dumps(results, indent=2)

        elif uri == "datadog://documentation-tree":
            tree = await server.get_documentation_tree(2)
            return json.dumps(tree, indent=2)

        else:
            raise ValueError(f"Unknown resource: {uri}")

    @server.server.list_resources()
    async def handle_list_resources() -> List[types.Resource]:
        """List available resources"""
        return [
            types.Resource(
                uri="datadog://scraping-status",
                name="Current Scraping Status",
                description="Real-time scraping status and progress",
                mimeType="application/json"
            ),
            types.Resource(
                uri="datadog://latest-results",
                name="Latest Scraping Results",
                description="Most recent scraping results and statistics",
                mimeType="application/json"
            ),
            types.Resource(
                uri="datadog://documentation-tree",
                name="Documentation Tree Structure",
                description="Hierarchical structure of scraped documentation",
                mimeType="application/json"
            )
        ]

    # Run the server
    port = int(os.getenv("MCP_SERVER_PORT", "8001"))
    logger.info(f"Starting Datadog MCP Server on port {port}")

    try:
        await server.server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
