import os
import yaml # You might need to install this: pip install PyYAML
import json

class PromptBank:
    """
    A singleton class to store and manage pre-canned prompts.
    Prompts are loaded from an external configuration file (YAML or JSON).
    """
    _instance = None
    _prompts = {} # Class variable to store the prompts

    def __new__(cls, config_file_path=None):
        """
        Ensures only one instance of PromptBank exists.
        Initializes prompts if it's the first instance.
        """
        if not cls._instance:
            cls._instance = super(PromptBank, cls).__new__(cls)
            # Initialize prompts only when the first instance is created
            cls._instance._load_prompts(config_file_path)
        return cls._instance

    def _load_prompts(self, config_file_path):
        """
        Loads prompts from the specified configuration file.
        Supports YAML and JSON formats.
        """
        if not config_file_path:
            print("Warning: No config file path provided. Prompt bank will be empty.")
            return

        if not os.path.exists(config_file_path):
            print(f"Error: Config file not found at '{config_file_path}'. Prompt bank will be empty.")
            return

        file_extension = os.path.splitext(config_file_path)[1].lower()

        try:
            if file_extension == '.yaml' or file_extension == '.yml':
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    PromptBank._prompts = yaml.safe_load(f)
                print(f"Prompts loaded from YAML: {config_file_path}")
            elif file_extension == '.json':
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    PromptBank._prompts = json.load(f)
                print(f"Prompts loaded from JSON: {config_file_path}")
            else:
                print(f"Error: Unsupported file format '{file_extension}'. Please use .yaml, .yml, or .json.")
                PromptBank._prompts = {}

            if not isinstance(PromptBank._prompts, dict):
                print("Error: Loaded content is not a dictionary. Ensure your config file is a key-value map.")
                PromptBank._prompts = {}

        except Exception as e:
            print(f"Error loading prompts from {config_file_path}: {e}")
            PromptBank._prompts = {}

    def get_prompt(self, product_name: str) -> str:
        """
        Retrieves a prompt by its product name.
        """
        return self._prompts.get(product_name, f"Error: Prompt for '{product_name}' not found.")

    def add_prompt(self, product_name: str, prompt_string: str):
        """
        Adds or updates a prompt in the bank.
        Note: This change is runtime only and won't persist to the file.
        """
        self._prompts[product_name] = prompt_string
        print(f"Prompt for '{product_name}' added/updated.")

    def list_all_prompts(self):
        """
        Lists all product names and their associated prompts.
        """
        return self._prompts.items()

# --- Example Usage ---

# 1. Create a YAML config file for prompts (e.g., prompts.yaml)
#    Content for prompts.yaml:
#    product_A_summary: "Summarize the key features of Product A, focusing on its benefits for small businesses."
#    product_B_marketing: "Write a compelling marketing copy for Product B, highlighting its innovative technology and ease of use."
#    product_C_faq: "Generate 5 frequently asked questions about Product C and provide concise answers."
#    general_greeting: "Hello! How can I assist you today?"

# 2. Create a JSON config file for prompts (e.g., prompts.json)
#    Content for prompts.json:
#    {
#        "product_D_review": "Analyze customer reviews for Product D and identify common pain points and praises.",
#        "product_E_tutorial": "Create a step-by-step tutorial for setting up Product E for the first time.",
#        "general_farewell": "Thank you for using our service. Goodbye!"
#    }

# Create dummy config files for demonstration
# You would typically have these files pre-existing
with open("prompts.yaml", "w", encoding="utf-8") as f:
    f.write("""
product_A_summary: "Summarize the key features of Product A, focusing on its benefits for small businesses."
product_B_marketing: "Write a compelling marketing copy for Product B, highlighting its innovative technology and ease of use."
product_C_faq: "Generate 5 frequently asked questions about Product C and provide concise answers."
general_greeting: "Hello! How can I assist you today?"
""")

with open("prompts.json", "w", encoding="utf-8") as f:
    f.write("""
{
    "product_D_review": "Analyze customer reviews for Product D and identify common pain points and praises.",
    "product_E_tutorial": "Create a step-by-step tutorial for setting up Product E for the first time.",
    "general_farewell": "Thank you for using our service. Goodbye!"
}
""")


# --- Demonstrate Singleton behavior and prompt retrieval ---

# First time creating the instance (prompts.yaml will be loaded)
print("\n--- First instance creation (loading prompts.yaml) ---")
prompt_bank_yaml = PromptBank("prompts.yaml")
print(f"Prompt for 'product_A_summary': {prompt_bank_yaml.get_prompt('product_A_summary')}")
print(f"Prompt for 'general_greeting': {prompt_bank_yaml.get_prompt('general_greeting')}")
print(f"Prompt for 'non_existent_prompt': {prompt_bank_yaml.get_prompt('non_existent_prompt')}")

# Attempt to create another instance with a different file path
# It will return the *same* instance and *not* reload/change prompts
print("\n--- Second instance creation (attempting to load prompts.json) ---")
prompt_bank_json = PromptBank("prompts.json") # This will return the same instance as prompt_bank_yaml
print(f"Are instances the same? {prompt_bank_yaml is prompt_bank_json}")
# The prompts loaded from prompts.yaml will still be present
print(f"Prompt for 'product_B_marketing' (from original load): {prompt_bank_json.get_prompt('product_B_marketing')}")
# The prompts from prompts.json were NOT loaded because it's the same instance
print(f"Prompt for 'product_D_review' (should be not found): {prompt_bank_json.get_prompt('product_D_review')}")


# If you want to load from a different file, you'd need a method to explicitly reload
# Or, design your singleton to take a *list* of config files on first init.
# For simplicity, this example assumes one primary config file for initial load.

# Demonstrate adding a prompt at runtime
print("\n--- Adding a prompt at runtime ---")
prompt_bank_yaml.add_prompt("new_product_feature", "Describe the new AI-powered feature of Product X.")
print(f"New prompt: {prompt_bank_yaml.get_prompt('new_product_feature')}")

# Demonstrate listing all prompts
print("\n--- Listing all prompts ---")
for key, value in prompt_bank_yaml.list_all_prompts():
    print(f"- {key}: {value[:50]}...") # Print first 50 chars for brevity

# Clean up dummy files
os.remove("prompts.yaml")
os.remove("prompts.json")
