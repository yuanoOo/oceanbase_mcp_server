import logging
import os
from mysql.connector import connect, Error
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("oceanbase_mcp_server")


def get_db_config():
    """Get database configuration from environment variables."""
    config_in = {
        "host": os.getenv("OB_HOST", "localhost"),
        "port": int(os.getenv("OB_PORT", "2881")),
        "user": os.getenv("OB_USER"),
        "password": os.getenv("OB_PASSWORD"),
        "database": os.getenv("OB_DATABASE")
    }

    if not all([config_in["user"], config_in["password"], config_in["database"]]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("OB_USER, OB_PASSWORD, and OB_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config_in


# Initialize server
mcp = FastMCP("oceanbase_mcp_server")
config = get_db_config()


@mcp.resource(uri="oceanbase://database/tables", name="List OceanBase tables as resources.", mime_type="text/plain")
def list_tables() -> str:
    """List OceanBase tables as resources."""
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")
                result = [",".join(map(str, table)) for table in tables]
                return str(result)
    except Error as e:
        logger.error(f"Failed to list resources: {str(e)}")
        return ""


@mcp.tool(name="Execute SQL commands")
def call_tool(name: str, arguments: dict) -> str:
    """Execute SQL commands."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        raise ValueError("Query is required")

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Special handling for SHOW TABLES
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = ["Tables_in_" + config["database"]]  # Header
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                elif query.strip().upper().startswith("SHOW COLUMNS"):
                    resp_header = "Columns info of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                elif query.strip().upper().startswith("DESCRIBE"):
                    resp_header = "Description of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                # Regular SELECT queries
                elif query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return "\n".join([",".join(columns)] + result)

                # Non-SELECT queries
                else:
                    conn.commit()
                    return f"Query executed successfully. Rows affected: {cursor.rowcount}"

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return "Error executing query: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting OceanBase MCP server...")
    logger.info(f"Database config: {config['host']}/{config['database']} as {config['user']}")
    mcp.run(transport="stdio")
