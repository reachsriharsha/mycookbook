import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat
from phonenumbers.phonenumberutil import number_type, PhoneNumberType

def validate_phone_number_with_country(phone_input, country_code):
    """
    Validates phone numbers for any country in multiple formats and returns international format.
    
    Supports the following input formats:
    - 9880122928 (digits without country code)
    - +919880122928 (full international format)  
    - 09880122928 (with leading zero - for applicable countries)
    
    Args:
        phone_input (str): Phone number in any of the supported formats
        country_code (str): Country code with + prefix (e.g., "+91" for India, "+1" for US)
    
    Returns:
        tuple: (valid_status: bool, international_format: str)
               - valid_status: True if valid mobile number for the specified country, False otherwise
               - international_format: Country code + number if valid, empty string if invalid
    """
    
    if not phone_input or not isinstance(phone_input, str):
        return (False, "")
    
    if not country_code or not isinstance(country_code, str):
        return (False, "")
    
    # Clean inputs - remove spaces, dashes, parentheses
    cleaned_phone = phone_input.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    cleaned_country_code = country_code.strip()
    
    # Ensure country code starts with +
    if not cleaned_country_code.startswith("+"):
        cleaned_country_code = "+" + cleaned_country_code.lstrip("+")
    
    # Extract numeric country code for validation
    numeric_country_code = cleaned_country_code[1:]  # Remove +
    
    try:
        parsed_number = None
        
        # Case 1: Phone already has country code
        if cleaned_phone.startswith("+"):
            parsed_number = phonenumbers.parse(cleaned_phone, None)
        
        # Case 2: Phone starts with numeric country code (without +)
        elif cleaned_phone.startswith(numeric_country_code):
            parsed_number = phonenumbers.parse("+" + cleaned_phone, None)
        
        # Case 3: Phone has leading zero (remove it and add country code)
        elif cleaned_phone.startswith("0") and len(cleaned_phone) > 1 and cleaned_phone[1:].isdigit():
            parsed_number = phonenumbers.parse(cleaned_country_code + cleaned_phone[1:], None)
        
        # Case 4: Phone is just the local number (add country code)
        elif cleaned_phone.isdigit():
            parsed_number = phonenumbers.parse(cleaned_country_code + cleaned_phone, None)
        
        else:
            # Try parsing with country as default region
            # Extract country ISO code from country code (approximate mapping)
            country_iso_map = {
                "1": "US", "91": "IN", "44": "GB", "49": "DE", "33": "FR", 
                "39": "IT", "34": "ES", "61": "AU", "81": "JP", "86": "CN"
            }
            default_region = country_iso_map.get(numeric_country_code, "ZZ")
            parsed_number = phonenumbers.parse(cleaned_phone, default_region)
        
        # Validate the parsed number
        if parsed_number:
            # Check if it's a valid number
            is_valid = phonenumbers.is_valid_number(parsed_number)
            
            # Check if it matches the expected country code
            expected_country_code = int(numeric_country_code)
            is_correct_country = parsed_number.country_code == expected_country_code
            
            # Check if it's a mobile number (optional - remove if you want all valid numbers)
            num_type = number_type(parsed_number)
            is_mobile = num_type in [PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE]
            
            if is_valid and is_correct_country and is_mobile:
                international_format = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
                return (True, international_format)
            else:
                return (False, "")
        else:
            return (False, "")
            
    except NumberParseException:
        return (False, "")
    except (ValueError, Exception):
        return (False, "")

def validate_phone_number_any_type_with_country(phone_input, country_code):
    """
    Validates phone numbers (mobile + landline) for any country in multiple formats.
    
    Args:
        phone_input (str): Phone number in any of the supported formats
        country_code (str): Country code with + prefix (e.g., "+91" for India, "+1" for US)
    
    Returns:
        tuple: (valid_status: bool, international_format: str)
               - valid_status: True if valid number for the specified country, False otherwise
               - international_format: Country code + number if valid, empty string if invalid
    """
    
    if not phone_input or not isinstance(phone_input, str):
        return (False, "")
    
    if not country_code or not isinstance(country_code, str):
        return (False, "")
    
    # Clean inputs
    cleaned_phone = phone_input.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    cleaned_country_code = country_code.strip()
    
    # Ensure country code starts with +
    if not cleaned_country_code.startswith("+"):
        cleaned_country_code = "+" + cleaned_country_code.lstrip("+")
    
    # Extract numeric country code for validation
    numeric_country_code = cleaned_country_code[1:]  # Remove +
    
    try:
        parsed_number = None
        
        # Case 1: Phone already has country code
        if cleaned_phone.startswith("+"):
            parsed_number = phonenumbers.parse(cleaned_phone, None)
        
        # Case 2: Phone starts with numeric country code (without +)
        elif cleaned_phone.startswith(numeric_country_code):
            parsed_number = phonenumbers.parse("+" + cleaned_phone, None)
        
        # Case 3: Phone has leading zero (remove it and add country code)
        elif cleaned_phone.startswith("0") and len(cleaned_phone) > 1 and cleaned_phone[1:].isdigit():
            parsed_number = phonenumbers.parse(cleaned_country_code + cleaned_phone[1:], None)
        
        # Case 4: Phone is just the local number (add country code)
        elif cleaned_phone.isdigit():
            parsed_number = phonenumbers.parse(cleaned_country_code + cleaned_phone, None)
        
        else:
            # Try parsing with country as default region
            country_iso_map = {
                "1": "US", "91": "IN", "44": "GB", "49": "DE", "33": "FR", 
                "39": "IT", "34": "ES", "61": "AU", "81": "JP", "86": "CN"
            }
            default_region = country_iso_map.get(numeric_country_code, "ZZ")
            parsed_number = phonenumbers.parse(cleaned_phone, default_region)
        
        # Validate the parsed number
        if parsed_number:
            is_valid = phonenumbers.is_valid_number(parsed_number)
            expected_country_code = int(numeric_country_code)
            is_correct_country = parsed_number.country_code == expected_country_code
            
            if is_valid and is_correct_country:
                international_format = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
                return (True, international_format)
            else:
                return (False, "")
        else:
            return (False, "")
            
    except NumberParseException:
        return (False, "")
    except (ValueError, Exception):
        return (False, "")

# Example usage and testing
if __name__ == "__main__":
    # Test cases for the number 9880122928
    test_cases = [
        ("9880122928", "+91"),      # Format 1: 10 digits with country code
        ("+919880122928", "+91"),   # Format 2: Full international
        ("09880122928", "+91"),     # Format 3: With leading zero
        ("919880122928", "+91"),    # Variation: without +
        ("+91 9880122928", "+91"),  # With space
        ("+91-988-012-2928", "+91"), # With dashes
        ("invalid", "+91"),         # Invalid input
        ("1234567890", "+91"),      # Invalid Indian mobile
        ("+1234567890", "+91"),     # Non-Indian number with Indian country code
        ("", "+91"),                # Empty string
        ("9880122928", "91"),       # Country code without +
        ("9880122928", "+1"),       # Indian number with US country code (should fail)
    ]
    
    # Test with different countries
    international_test_cases = [
        ("2125551234", "+1"),       # US number
        ("2075551234", "+1"),       # US number
        ("9880122928", "+91"),      # Indian number
        ("7911123456", "+44"),      # UK mobile
        ("1771234567", "+49"),      # German number
    ]
    
    print("=== Testing Phone Number Validator with Country Code (Mobile Only) ===")
    for i, (phone, country) in enumerate(test_cases, 1):
        valid, international = validate_phone_number_with_country(phone, country)
        print(f"Test {i}: '{phone}' + '{country}' -> Valid: {valid}, International: '{international}'")
    
    print("\n=== Testing Phone Number Validator with Country Code (All Types) ===")
    for i, (phone, country) in enumerate(test_cases, 1):
        valid, international = validate_phone_number_any_type_with_country(phone, country)
        print(f"Test {i}: '{phone}' + '{country}' -> Valid: {valid}, International: '{international}'")
    
    print("\n=== Testing with Different Countries ===")
    for phone, country in international_test_cases:
        valid_mobile, international_mobile = validate_phone_number_with_country(phone, country)
        valid_any, international_any = validate_phone_number_any_type_with_country(phone, country)
        print(f"Phone: '{phone}' + '{country}'")
        print(f"  Mobile only: Valid: {valid_mobile}, International: '{international_mobile}'")
        print(f"  Any type: Valid: {valid_any}, International: '{international_any}'")
        print()
    
    # Additional test with landline numbers
    print("=== Testing with Landline Numbers ===")
    landline_tests = [
        ("02261234567", "+91"),     # Mumbai landline with 0
        ("2261234567", "+91"),      # Mumbai landline without 0
        ("2125551234", "+1"),       # US landline
    ]
    
    for phone, country in landline_tests:
        valid, international = validate_phone_number_any_type_with_country(phone, country)
        print(f"Landline test: '{phone}' + '{country}' -> Valid: {valid}, International: '{international}'")