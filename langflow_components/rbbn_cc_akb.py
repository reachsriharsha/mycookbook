# from langflow.field_typing import Data
import httpx
from typing import Any
from langflow.custom import Component
#from langflow.io import MessageTextInput, Output, DropdownInput
from langflow.io import Output
from langflow.inputs.inputs import BoolInput, DictInput, DropdownInput, IntInput, SecretStrInput, SliderInput, StrInput
from langflow.schema import Data


class AcumenKnowledgeBase(Component):
    display_name = "AAI Knowledge Base"
    description = "The Acumen Knowledge Base component."
    documentation: str = "http://docs.langflow.org/components/custom"
    icon = "code"
    name = "AcumenKnowledgeBase"

    inputs = [
        
        StrInput(
            name="base_url",
            display_name="Base URL",
            info="Endpoint of the Acumen AI Services.",
            value="",
            real_time_refresh=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="Acumen AI API Key",
            info="The Acumen AI API Key to use for the Acumen AI Services.",
            advanced=False,
            value="AAIS_API_KEY",
            required=True,
            real_time_refresh=True,
        ),
        DropdownInput(
            name="kb_name",
            display_name="Knowledge Base Name",
            options=[],
            info="Refer to Acumen AI Services.",
            refresh_button=True,
            real_time_refresh=True,
            dynamic=True,
        ),
        StrInput(
            name="search_query",
            display_name="Search Query",
            info="Query to be Searched.",
            value="",
            real_time_refresh=True,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Data:
        self.update_build_config
        data = Data(value=self.base_url)
        self.status = data
        return data

    async def is_valid_aai_url(self, url: str) -> bool:
        '''
        try:
            async with httpx.AsyncClient() as client:
                return (await client.get(urljoin(url, "api/tags"))).status_code == HTTP_STATUS_OK
        except httpx.RequestError:
            return False
        '''
        return True
        
    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        self.log(f'update_build_config called')
        if field_name == "kb_name":
            build_config["kb_name"]["options"] = await self.get_kblist(self.base_url)
        
        return build_config
    
    async def get_kblist(self, base_url_value: str) -> list[str]:
        try:
            self.log(f'get_kblist called')
            url = base_url_value
            async with httpx.AsyncClient() as client:
                headers = {
                       "Authorization": f"Bearer {self.api_key}",
                        # Add other headers if needed
                    }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                self.log(data)

            kb_list_ids = data.get("kb_list", [])
            

        except (ImportError, ValueError, httpx.RequestError, Exception) as e:
            msg = "Could not get knowledge base list from Acumen."
            raise ValueError(msg) from e
        return kb_list_ids