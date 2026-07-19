from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that wraps all errors in a standardized
    {"success": false, "message": "...", "errors": {...}} response format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Determine the primary error message
        message = "Validation Error"
        if "detail" in response.data:
            message = response.data["detail"]
        elif isinstance(response.data, list) and len(response.data) > 0:
            message = str(response.data[0])
        elif isinstance(response.data, dict):
            # Pick the first error value as the main message if it's a dict
            first_key = list(response.data.keys())[0]
            val = response.data[first_key]
            if isinstance(val, list) and len(val) > 0:
                message = f"{first_key}: {val[0]}"
            else:
                message = str(val)

        custom_response_data = {
            "success": False,
            "message": message,
            "errors": response.data
        }
        
        response.data = custom_response_data

    return response
