# from langflow.field_typing import Data
from langflow.custom import Component
#from langflow.io import MessageTextInput, Output, DropdownInput
from langflow.io import Output
from langflow.inputs.inputs import BoolInput, DictInput, DropdownInput, IntInput, SecretStrInput, SliderInput, StrInput
from langflow.schema import Data


class AcumenKnowledgeBase(Component):
    display_name = "Acumen Knowledge Base"
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
        ),
        SecretStrInput(
            name="api_key",
            display_name="Acumen AI API Key",
            info="The Acumen AI API Key to use for the Acumen AI Services.",
            advanced=False,
            value="AAIS_API_KEY",
            required=True,
        ),
        StrInput(
            name="kb_name",
            display_name="Knowledge Base Name",
            options=[],
            info="Refer to Acumen AI Services.",
            refresh_button=True,
            real_time_refresh=True,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Data:
        data = Data(value=self.base_url)
        self.status = data
        return data
