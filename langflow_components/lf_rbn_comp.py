# from langflow.field_typing import Data
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, DropdownInput
from langflow.schema import Data


class AcumenKnowledgeBase(Component):
    display_name = "Acumen Knowledge Base"
    description = "The Acumen Knowledge Base component."
    documentation: str = "http://docs.langflow.org/components/custom"
    icon = "code"
    name = "AcumenKnowledgeBase"

    inputs = [
        
        MessageTextInput(
            name="base_url",
            display_name="Base URL",
            info="Endpoint of the Acumen AI Services.",
            value="",
        ),
        DropdownInput(
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
