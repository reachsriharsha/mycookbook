import requests
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, SelectInput, ButtonInput
from langflow.schema import Data

class KBListComponent(Component):
    display_name = "KB List Fetcher"
    description = "Fetches a list of KBs from a URL using an API key and populates a dropdown."
    documentation: str = "http://docs.langflow.org/components/custom"
    icon = "code"
    name = "KBListComponent"

    inputs = [
        MessageTextInput(
            name="url",
            display_name="URL",
            info="Endpoint to fetch KB list from.",
            value="",
            tool_mode=True,
        ),
        MessageTextInput(
            name="api_key",
            display_name="API Key",
            info="API Key for authentication.",
            value="",
            tool_mode=True,
        ),
        SelectInput(
            name="kb_dropdown",
            display_name="Knowledge Base",
            options=[],
            info="Select a KB from the list.",
        ),
        ButtonInput(
            name="refresh",
            display_name="Refresh KB List",
            info="Click to refresh the KB list from the URL.",
        ),
    ]

    outputs = [
        Output(display_name="Selected KB", name="selected_kb", method="build_output"),
    ]

    def fetch_kb_list(self, url, api_key):
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            kb_list = data.get("kb_list", [])
            return kb_list
        except Exception as e:
            return []

    def build_output(self) -> Data:
        url = getattr(self, "url", "")
        api_key = getattr(self, "api_key", "")
        refresh = getattr(self, "refresh", False)
        kb_dropdown = getattr(self, "kb_dropdown", "")

        # Only fetch if refresh is clicked or dropdown is empty
        if refresh or not kb_dropdown:
            kb_list = self.fetch_kb_list(url, api_key)
            # Update dropdown options
            self.set_input_options("kb_dropdown", kb_list)
            # Select first if none selected
            selected = kb_list[0] if kb_list else ""
        else:
            selected = kb_dropdown

        data = Data(value=selected)
        self.status = data
        return data
