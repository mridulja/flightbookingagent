"""
Flight Booking Assistant using OpenAI's GPT-4 with function calling capabilities.
This module implements a conversational AI agent that helps users book flights
through a chat interface.
"""

import os
import json
import logging
from typing import List, Tuple, Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize environment and OpenAI client
load_dotenv()
openai = OpenAI()
MODEL = "gpt-4o-mini"

# Constants
TICKET_PRICES = {
    "london": "$799",
    "paris": "$899",
    "tokyo": "$1400",
    "rome": "$929",
}

class BookingState:
    """
    Maintains the state of a booking conversation.
    
    Attributes:
        destination (Optional[str]): Target city for the flight
        name (Optional[str]): Passenger's full name
        email (Optional[str]): Contact email for booking confirmation
        price (Optional[str]): Price of the flight
        booking_stage (str): Current stage in the booking process
        conversation_id (str): Unique identifier for the conversation
    """
    def __init__(self):
        self.destination: Optional[str] = None
        self.name: Optional[str] = None
        self.email: Optional[str] = None
        self.price: Optional[str] = None
        self.booking_stage: str = "initial"
        self.conversation_id: str = str(uuid.uuid4())

    def reset(self):
        self.__init__()

# Tool Function Definitions
price_function = {
    "name": "get_ticket_price",
    "description": """
    Retrieves the price for a flight ticket to a specific destination.
    Used when users inquire about flight prices or during booking confirmation.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The destination city for the flight (case-insensitive)"
            }
        },
        "required": ["destination_city"]
    }
}

booking_function = {
    "name": "book_flight",
    "description": """
    Process a flight booking with validated passenger details.
    Called after collecting and validating all required information.
    Creates a simulation booking with a unique reference number.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The destination city for the flight booking"
            },
            "passenger_name": {
                "type": "string",
                "description": "Full name of the passenger (first and last name required)"
            },
            "email": {
                "type": "string",
                "description": "Valid email address for booking confirmation"
            }
        },
        "required": ["destination_city", "passenger_name", "email"]
    }
}

validation_function = {
    "name": "validate_info",
    "description": """
    Validates passenger information before proceeding with booking.
    Checks if the name contains at least two parts and if the email is properly formatted.
    Called before finalizing a booking to ensure data quality.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "passenger_name": {
                "type": "string",
                "description": "Full name to validate (must contain at least first and last name)"
            },
            "email": {
                "type": "string",
                "description": "Email address to validate (must contain @ and domain)"
            }
        },
        "required": ["passenger_name", "email"]
    }
}

# Tool definitions list for OpenAI API
tools = [
    {"type": "function", "function": price_function},
    {"type": "function", "function": booking_function},
    {"type": "function", "function": validation_function}
]

system_message = """
You are Sonya, a helpful flight booking assistant. Guide users through the booking process naturally.
Follow these steps in order:
1. For price inquiries, use get_ticket_price to provide accurate pricing
2. For validating user info, use validate_info to ensure data quality
3. For booking flights, use book_flight after all validations pass
Maintain a friendly and helpful tone throughout the conversation.
Handle user frustration professionally and offer clear solutions.
"""

def get_ticket_price(city: str) -> str:
    """
    Retrieve the ticket price for a given destination.
    
    Args:
        city (str): The destination city name
        
    Returns:
        str: The price for the flight or "Price not available" if not found
        
    Example:
        >>> get_ticket_price("london")
        "$799"
    """
    return TICKET_PRICES.get(city.lower(), "Price not available")

def validate_info(name: str, email: str) -> Dict[str, bool]:
    """
    Validate passenger name and email format.
    
    Args:
        name (str): Full name of the passenger
        email (str): Email address for booking confirmation
        
    Returns:
        Dict[str, bool]: Validation results containing:
            - name_valid: True if name has at least two parts
            - email_valid: True if email contains @ and domain
            - all_valid: True if both validations pass
            
    Example:
        >>> validate_info("John Doe", "john@example.com")
        {"name_valid": True, "email_valid": True, "all_valid": True}
    """
    name_valid = len(name.strip().split()) >= 2
    email_valid = '@' in email and '.' in email
    return {
        "name_valid": name_valid,
        "email_valid": email_valid,
        "all_valid": name_valid and email_valid
    }

def handle_tool_call(message) -> Tuple[Dict, Optional[str]]:
    """
    Process tool calls from OpenAI's API and execute corresponding functions.
    
    Args:
        message: OpenAI's message object containing tool calls
        
    Returns:
        Tuple[Dict, Optional[str]]: 
            - Dict: Response data for the tool call
            - Optional[str]: Destination city if relevant, None otherwise
            
    The function handles three types of tool calls:
    1. get_ticket_price: Retrieves flight prices
    2. validate_info: Validates passenger information
    3. book_flight: Processes the final booking
    
    Each tool call returns a properly formatted response that includes:
    - role: "tool"
    - content: JSON string of the result
    - tool_call_id: Original call ID from OpenAI
    - name: Function name that was called
    """
    logger.info(f"Handling tool call: {message.tool_calls[0]}")
    
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    if function_name == "get_ticket_price":
        city = arguments.get('destination_city')
        price = get_ticket_price(city)
        response = {
            "role": "tool",
            "content": json.dumps({"destination_city": city, "price": price}),
            "tool_call_id": tool_call.id,
            "name": function_name
        }
        return response, city
    
    elif function_name == "validate_info":
        name = arguments.get('passenger_name')
        email = arguments.get('email')
        validation_result = validate_info(name, email)
        response = {
            "role": "tool",
            "content": json.dumps(validation_result),
            "tool_call_id": tool_call.id,
            "name": function_name
        }
        return response, None
    
    elif function_name == "book_flight":
        city = arguments.get('destination_city')
        name = arguments.get('passenger_name')
        email = arguments.get('email')
        
        # Generate booking reference
        booking_ref = f"SIM-{abs(hash(f'{city}{name}{email}')) % 100000:05d}"
        
        response = {
            "role": "tool",
            "content": json.dumps({
                "success": True,
                "booking_reference": booking_ref,
                "message": f"SIMULATION - Booking Confirmed!\nDestination: {city.title()}\nPassenger: {name}\nEmail: {email}\nPrice: {get_ticket_price(city)}\nBooking Reference: {booking_ref}"
            }),
            "tool_call_id": tool_call.id,
            "name": function_name
        }
        return response, city

    return None, None

def chat(message: str, history: List[Tuple[str, str]]) -> str:
    """
    Process chat messages and handle tool calling sequence.
    
    Args:
        message (str): Current user message
        history (List[Tuple[str, str]]): Conversation history as (user, assistant) pairs
        
    Returns:
        str: Assistant's response
        
    Flow:
    1. Formats conversation history for OpenAI
    2. Makes initial API call with tool definitions
    3. If tool calls are present:
       - Adds assistant's message to conversation
       - Processes each tool call
       - Gets final response after tool execution
    4. Formats and returns the final response
    
    Error Handling:
    - Catches and logs all exceptions
    - Returns apologetic message on errors
    """
    try:
        # Convert history to OpenAI message format
        messages = [{"role": "system", "content": system_message}]
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": message})

        # Get initial response
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Handle tool calls if any
        if response.choices[0].message.tool_calls:
            # Add the assistant's message with the tool calls
            assistant_message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls
            })
            
            # Handle each tool call
            for tool_call in assistant_message.tool_calls:
                response_data, city = handle_tool_call(assistant_message)
                if response_data:
                    messages.append(response_data)
            
            # Get final response after tool execution
            final_response = openai.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = response.choices[0].message.content

        if not final_content.startswith("Sonya:"):
            final_content = f"Sonya: {final_content}"
        
        return final_content

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return "Sonya: I apologize, but I encountered an error. Please try again."

# Launch Gradio interface
def main():
    """
    Initialize and launch the Gradio chat interface.
    
    Features:
    - Dark mode enforcement
    - Custom title and description
    - Disabled flagging
    - Continuous chat session
    """
    force_dark_mode = """
    function refresh() {
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """
    gr.ChatInterface(
        fn=chat,
        title="CrewAIR Booking Assistant - Sonya",
        description="This is a simulation. No real bookings are made.", flagging_mode="never", js=force_dark_mode
    ).launch()

if __name__ == "__main__":
    main()
