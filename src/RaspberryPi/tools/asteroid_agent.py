"""
Asteroid AI Agent Integration.
Executes an Asteroid agent to create eBay listings from item details and images.
"""

import os
import time
import base64
import json
from typing import Optional, Dict, Any

try:
    from asteroid_odyssey import Configuration, ApiClient, AgentsApi, ExecutionApi, FilesApi
    from asteroid_odyssey import AgentsAgentExecuteAgentRequest
    ASTEROID_AVAILABLE = True
except ImportError:
    ASTEROID_AVAILABLE = False


class AsteroidAgent:
    """Client for executing Asteroid agents."""

    def __init__(self, api_key: Optional[str] = None, agent_id: Optional[str] = None):
        """
        Initialize the Asteroid agent client.

        Args:
            api_key: Asteroid API key. If None, reads from ASTEROID_API_KEY env var.
            agent_id: Agent ID. If None, reads from ASTEROID_AGENT_ID, AGENT_ID,
                or AGENT_PROFILE_ID env vars.
        """
        if not ASTEROID_AVAILABLE:
            raise ImportError(
                "asteroid-odyssey package not installed. "
                "Install with: pip install asteroid-odyssey"
            )

        self.api_key = api_key or os.getenv("ASTEROID_API_KEY")
        if not self.api_key:
            raise ValueError("Asteroid API key required. Set ASTEROID_API_KEY environment variable.")

        self.agent_id = self._normalize_agent_id(
            agent_id
            or os.getenv("ASTEROID_AGENT_ID")
            or os.getenv("AGENT_ID")
            or os.getenv("AGENT_PROFILE_ID")
        )
        if not self.agent_id:
            raise ValueError(
                "Agent ID required. Set ASTEROID_AGENT_ID, AGENT_ID, or AGENT_PROFILE_ID "
                "environment variable."
            )

        self.fallback_agent_id = None
        for candidate in (os.getenv("AGENT_PROFILE_ID"), os.getenv("AGENT_ID")):
            normalized = self._normalize_agent_id(candidate)
            if normalized and normalized != self.agent_id:
                self.fallback_agent_id = normalized
                break

        # Configure client with correct host and API key header
        self.config = Configuration(
            host="https://odyssey.asteroid.ai/agents/v2",
            api_key={"ApiKeyAuth": self.api_key}
        )
        # Set the API key header name explicitly
        self.config.api_key_prefix = {"ApiKeyAuth": ""}
        self.client = ApiClient(self.config)
        # Add the correct header for authentication
        self.client.default_headers["X-Asteroid-Agents-Api-Key"] = self.api_key
        self.agents_api = AgentsApi(self.client)
        self.execution_api = ExecutionApi(self.client)
        self.files_api = FilesApi(self.client)

    @staticmethod
    def _normalize_agent_id(value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        if " - " in value:
            return value.split(" - ")[-1].strip()
        return value.strip()

    def _execute_agent(self, inputs: Dict[str, Any]):
        request = AgentsAgentExecuteAgentRequest(inputs=inputs)
        try:
            return self.agents_api.agent_execute_post(
                agent_id=self.agent_id,
                agents_agent_execute_agent_request=request
            )
        except Exception as exc:
            status = getattr(exc, "status", None)
            if status is None and "(403)" in str(exc):
                status = 403
            if status == 403 and self.fallback_agent_id:
                print(
                    f"Access denied for agent ID {self.agent_id}, "
                    f"retrying with {self.fallback_agent_id}..."
                )
                response = self.agents_api.agent_execute_post(
                    agent_id=self.fallback_agent_id,
                    agents_agent_execute_agent_request=request
                )
                self.agent_id = self.fallback_agent_id
                self.fallback_agent_id = None
                return response
            raise

    def create_listing(
        self,
        title: str,
        price: str,
        condition: str,
        description: str,
        image_url: Optional[str] = None,
        poll_interval: float = 2.0,
        max_wait: float = 300.0
    ) -> Dict[str, Any]:
        """
        Execute the Asteroid agent to create an eBay listing.

        Args:
            title: Item title for the listing
            price: Item price (e.g., "65.00")
            condition: Item condition (e.g., "Used", "New")
            description: Item description
            image_url: URL of the item image (optional)
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait for completion

        Returns:
            Dict with execution result including status and any outputs
        """
        # Prepare inputs for the agent
        inputs = {
            "title": title,
            "price": price,
            "condition": condition,
            "description": description,
        }

        if image_url:
            inputs["image_url"] = image_url

        print(f"Executing Asteroid agent with inputs: {json.dumps(inputs, indent=2)}")

        # Execute the agent
        response = self._execute_agent(inputs)

        execution_id = response.execution_id
        print(f"Execution started with ID: {execution_id}")

        # Poll for completion
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                return {
                    "status": "timeout",
                    "execution_id": execution_id,
                    "message": f"Execution did not complete within {max_wait} seconds"
                }

            result = self.execution_api.execution_get(execution_id=execution_id)
            status = result.status.value if hasattr(result.status, 'value') else str(result.status)

            print(f"Execution status: {status} (elapsed: {elapsed:.1f}s)")

            if status in ["completed", "failed", "cancelled"]:
                return {
                    "status": status,
                    "execution_id": execution_id,
                    "result": result
                }

            time.sleep(poll_interval)

    def create_listing_async(
        self,
        title: str,
        price: str,
        condition: str,
        description: str,
        image_url: Optional[str] = None
    ) -> str:
        """
        Start the Asteroid agent execution without waiting for completion.

        Args:
            title: Item title for the listing
            price: Item price (e.g., "65.00")
            condition: Item condition (e.g., "Used", "New")
            description: Item description
            image_url: URL of the item image (optional)

        Returns:
            Execution ID that can be used to check status later
        """
        inputs = {
            "title": title,
            "price": price,
            "condition": condition,
            "description": description,
        }

        if image_url:
            inputs["image_url"] = image_url

        response = self._execute_agent(inputs)

        return response.execution_id

    def check_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Check the status of an execution.

        Args:
            execution_id: The execution ID to check

        Returns:
            Dict with status and result information
        """
        result = self.execution_api.execution_get(execution_id=execution_id)
        status = result.status.value if hasattr(result.status, 'value') else str(result.status)

        return {
            "status": status,
            "execution_id": execution_id,
            "result": result
        }


# Global instance for easy access
_agent: Optional[AsteroidAgent] = None


def get_agent() -> AsteroidAgent:
    """Get or create the global Asteroid agent instance."""
    global _agent
    if _agent is None:
        _agent = AsteroidAgent()
    return _agent


def create_ebay_listing(
    title: str,
    price: str,
    condition: str,
    description: str,
    image_url: Optional[str] = None
) -> str:
    """
    Create an eBay listing using the Asteroid agent.

    Args:
        title: Item title
        price: Item price
        condition: Item condition
        description: Item description
        image_url: Optional image URL

    Returns:
        Status message about the listing creation
    """
    try:
        agent = get_agent()
        result = agent.create_listing(
            title=title,
            price=price,
            condition=condition,
            description=description,
            image_url=image_url
        )

        if result["status"] == "completed":
            return f"Successfully created eBay listing for '{title}'"
        elif result["status"] == "failed":
            return f"Failed to create listing: {result.get('result', 'Unknown error')}"
        elif result["status"] == "timeout":
            return f"Listing creation is taking longer than expected. Execution ID: {result['execution_id']}"
        else:
            return f"Listing creation status: {result['status']}"

    except ImportError as e:
        return f"Asteroid SDK not available: {str(e)}"
    except Exception as e:
        return f"Error creating listing: {str(e)}"
