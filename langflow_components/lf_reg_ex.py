from langflow.io import DropdownInput, StrInput
from langflow.custom import Component

class RegexRouter(Component):
    display_name = "My Regex Router"
    description = "Demonstrates dynamic fields for regex input."

    inputs = [
        DropdownInput(
            name="operator",
            display_name="Operator",
            options=["equals", "contains", "regex"],
            value="equals",
            real_time_refresh=True,
        ),
        StrInput(
            name="regex_pattern",
            display_name="Regex Pattern",
            info="Used if operator='regex'",
            dynamic=True,
            show=False,
        ),
    ]
    
    def update_build_config(self, build_config: dict, field_value: str, field_name: str | None = None) -> dict:
        if field_name == "operator":
            if field_value == "regex":
                build_config["regex_pattern"]["show"] = True
            else:
                build_config["regex_pattern"]["show"] = False
        return build_config

