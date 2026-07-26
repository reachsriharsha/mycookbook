import requests
import os
from dotenv import load_dotenv
load_dotenv()


url = "https://api.zeptomail.in/v1.1/email"

#let parametersize the to field with the email address and name of the recipient. You can also add multiple recipients by adding more objects to the "to" array.
target_email = os.getenv('TARGET_EMAIL')
from_address = os.getenv('FROM_ADDRESS')
payload = f"{{\n\"from\": {{ \"address\": \"{from_address}\"}},\n\"to\": [{{\"email_address\": {{\"address\": \"{target_email}\",\"name\": \"dev\"}}}}],\n\"subject\":\"This is test Email\",\n\"htmlbody\":\"<div><b> Test email sent successfully. Yes! it works!!!  </b></div>\"\n}}"
headers = {
'accept': "application/json",
'content-type': "application/json",
'authorization': f"Zoho-enczapikey {os.getenv('ZEPTOMAIL_API_KEY')}",
}

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)
