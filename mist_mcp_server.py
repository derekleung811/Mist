import os
import requests
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Juniper Mist Automation Server")

# Fetch environment variables for Authentication
# It is highly recommended to pass these via environment variables instead of hardcoding.
MIST_API_TOKEN = os.getenv("MIST_API_TOKEN")
MIST_ORG_ID = os.getenv("MIST_ORG_ID")
MIST_HOST = os.getenv("MIST_HOST", "api.mist.com")  # e.g., api.eu.mist.com for EU region

@mcp.tool()
def create_org_psk(
    name: str,
    passphrase: str,
    ssid: str,
    usage: str = "multi",
    vlan_id: int = None
) -> str:
    """
    Creates a new Pre-Shared Key (PSK) at the Organization level on the Juniper Mist platform.
    
    Args:
        name: A descriptive name for the PSK (e.g., identity vector).
        passphrase: The security passphrase (8-63 characters, or 64 hex characters).
        ssid: The SSID this PSK should be applicable to.
        usage: The type of PSK. Options: 'multi' (default for MPSK) or 'single'.
        vlan_id: Optional VLAN ID to bind dynamically to traffic authenticated by this PSK.
    """
    if not MIST_API_TOKEN or not MIST_ORG_ID:
        return "Error: MIST_API_TOKEN and MIST_ORG_ID environment variables must be configured."

    url = f"https://{MIST_HOST}/api/v1/orgs/{MIST_ORG_ID}/psks"
    
    headers = {
        "Authorization": f"Token {MIST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Build Payload based on Juniper Mist Documentation
    payload = {
        "name": name,
        "passphrase": passphrase,
        "ssid": ssid,
        "usage": usage
    }
    
    if vlan_id is not None:
        payload["vlan_id"] = vlan_id

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code in [200, 201]:
            data = response.json()
            return (
                f"Success! Org PSK created effectively.\n"
                f"ID: {data.get('id')}\n"
                f"Name: {data.get('name')}\n"
                f"SSID: {data.get('ssid')}\n"
                f"Passphrase: {data.get('passphrase')}"
            )
        else:
            return f"Failed to create PSK. Mist API returned status {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"An error occurred while connecting to the Mist API: {str(e)}"

if __name__ == "__main__":
    # Run the server using Stdio transport (required for Copilot / GitHub MCP integrations)
    mcp.run(transport="stdio")