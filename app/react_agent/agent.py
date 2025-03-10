"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""
import time
from datetime import datetime, timezone
from typing import Dict, List, Literal, cast
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
from datetime import date
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI as LangchainChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor
from langgraph.prebuilt import ToolNode
from typing import Dict, List, Literal, Any
from IPython.display import display
from app.react_agent.state import OverallState
import os 
import re
import json
from datetime import date
from pydantic import BaseModel, Field
import asyncio

from langchain.tools import BaseTool, Tool
from langchain_core.runnables import Runnable
from app.react_agent.configuration import Configuration
from app.react_agent.state import InputState, OverallState, OutputState
from app.react_agent.prompts import SYSTEM_PROMPT, ACTIVITY_PLANNER_PROMPT, FLIGHT_FINDER_PROMPT, RECOMMENDATION_PROMPT, RECOMMENDATION_PROMPT_2

from app.react_agent.tools import (TOOLS, weather_tool, 
                                   flight_tool, booking_tool,
                                   google_places_tool,tavily_search_tool,
                                   flight_tools_condition, accomodation_tools_condition, activity_planner_tools_condition, 
                                   FlightSearchInput, BookingSearchInput, GoogleMapsPlacesInput,
                                   TicketmasterEventSearchInput, ticketmaster_tool, AirbnbSearchInput, airbnb_tool,
                                   google_flights_tool, FlightSearchInput_2, google_flights_tool_sync)

from app.react_agent.utils import load_chat_model
from langchain_core.tools import tool
from openai import OpenAI  # Ensure you're using the correct OpenAI client

# Load environment variables from the .env file
load_dotenv()
# Define the function that calls the model

#-----------------------------------------------LLM------------------------------------------------
# Initialize the LLM
# llm = LangchainChatDeepSeek(
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     model= "deepseek-chat",
#     base_url="https://api.deepseek.com",
# )


# llm = LangchainChatDeepSeek(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     model= "gpt-4o"
# )


# Initialize the LLM
async def initialize_llm():
    llm_deepseek = LangchainChatDeepSeek(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
    )

    llm_openai = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    return llm_deepseek, llm_openai
#-----------------------------------------------------------------------------------------------
# Nodes and Agents
#-----------------------------------------------------------------------------------------------

#----------------------------------------------- First Node--------------------------------------------
class TravelItinerary(BaseModel):
    location: Optional[str] = Field(description="The user's current location or starting point.")
    loc_code: Optional[str] = Field(description="The airport code of the user's current location.")
    destination: Optional[str] = Field(description="The destination the user wants to travel to.")
    dest_code: Optional[str] = Field(description="The airport code of the user's destination.")
    travel_class: Optional[Literal[0, 1, 2, 3, 4]] = Field(description="The travel class specified by the user.")
    start_date: Optional[str] = Field(description="The start date of the trip in YYYY-MM-DD format.")
    end_date: Optional[str] = Field(description="The end date of the trip in YYYY-MM-DD format.")
    num_adults: Optional[int] = Field(description="The number of adults traveling.")
    num_children: Optional[int] = Field(description="The number of children traveling.")
    user_preferences: Optional[Dict[str, Any]] = Field(description="User preferences and requirements.")
    accommodation_options: Optional[Literal["Hotel", "Airbnb"]] = Field(description="The type of accommodation chosen by the user.")
    sort_by: Optional[str] = Field(description="The sorting criteria of flight chosen by the user (e.g., price, duration, departure, arrival).")
    
    
# async def travel_itinerary_planner(state: OverallState) -> OverallState:
#     """
#     Extracts travel itinerary details from user input.
#     Uses DeepSeek LLM first, and switches to GPT-4o if DeepSeek fails.
#     If both fail, retries once more before returning a fallback response.
#     """

#     print("Initializing LLMs...")
#     llm_deepseek, llm_openai = await initialize_llm()
    
#     # async def create_chain(llm):
#     #     """Creates a prompt processing chain for the given LLM."""
#     #     return PromptTemplate(
#     #         template="""You are a travel itinerary planner. Your task is to extract relevant information from the user's query to plan a trip.
#     #                     Here is the user's query: {query}
#     #                     Extract the following information:
#     #                     - Location (starting point)
#     #                     - loc_code (an uppercase 3-letter airport code of the starting point, use the IATA airport codes, and if not available, use the city name. If there are multiple airports, choose the main one. Unless the user specifies a specific airport, use the city name.)
#     #                     - destination
#     #                     - dest_code (an uppercase 3-letter airport code of the destination. use the IATA airport codes, and if not available, use the city name. If there are multiple airports, choose the main one. Unless the user specifies a specific airport, use the city name.)
#     #                     - travel_class (0: Not Specified, 1: Economy, 2: Premium Economy, 3: Business, 4: First). the travel class specified by the user, else 0 if not specified. This should be numeric values mapped to the corresponding travel class names.
#     #                     - Start date
#     #                     - End date
#     #                     - Number of adults
#     #                     - Number of children
#     #                     - User preferences
#     #                     - Accommodation options (Hotel or Airbnb). If the user does not specify, use the default value "Hotel".
#     #                     - sort_by - Sorting criteria for flights. Default is "price". Determine the sorting criteria based on the user's query:
#     #                                 - If the user is looking for the cheapest flights, set sort_by to "price".
#     #                                 - If the user is looking for the shortest flights, set sort_by to "duration".
#     #                                 - If the user is looking for the earliest flight that leaves the airport, set sort_by to "departure".
#     #                                 - If the user is looking for the earliest flight that arrives at the destination, set sort_by to "arrival".
#     #                                 - If the user does not specify any preference, or if the query does not indicate urgency, set sort_by to "price".
                                    
#     #                     If any information is missing, leave it as None. The year will always be 2025, unless specified otherwise by the user query.
#     #                     The default number of adults is 1, and the default number of children is 0. If the user does not specify the number of adults or children, use the default values.
                        
#     #                     For example, if the user query is "I want to travel from New York to Los Angeles on July 1st, 2022, with a budget of $5000 for 2 adults and 1 child, and return on July 20th, 2022. I plan to stay in a hotel." you should extract the following information:
#     #                     - Location: New York
#     #                     - loc_code: JFK
#     #                     - Destination: Los Angeles
#     #                     - dest_code: LAX
#     #                     - travel_class: 0
#     #                     - Start date: 2022-07-01
#     #                     - End date: 2022-07-20
#     #                     - Number of adults: 2
#     #                     - Number of children: 1
#     #                     - User preferences: {{ "budget": "$5000"}}
#     #                     - Accommodation options: Hotel
#     #                     - sort_by: price

#     #                     Example 2:
#     #                     User query: "I'm planning a luxury honeymoon trip from London to Tokyo in December 12, 2025 via Gatwick Its a five day trip with my husband and We'd like to fly first class with a budget of $15,000, staying in a high-end hotel. We want private airport transfers and dietary accommodations for a vegetarian diet, and we would like our flights to leave early. Activities should include cultural tours, fine dining, and shopping. There will be 2 adults, no children, and we need 1 suite."
#     #                     Extracted information:
#     #                     - Location: London
#     #                     - loc_code: LGW
#     #                     - Destination: Tokyo
#     #                     - dest_code: HND
#     #                     - travel_class: 4
#     #                     - Start date: 2025-12-12
#     #                     - End date: 2025-12-17
#     #                     - Number of adults: 2
#     #                     - Number of children: 0
#     #                     - User preferences: {{ "trip_type": "Luxury", "budget": "$15,000", "transportation": "Private transfer", "diet": "Vegetarian", "activities": ["Cultural tours", "Fine dining", "Shopping"] }}
#     #                     - Accommodation options: Hotel
#     #                     - sort_by: departure
#     #                     """,
#     #         input_variables=["query"]
#     #     ) | llm.with_structured_output(TravelItinerary)

#     def create_chain(llm):
#         """Creates an asynchronous processing chain for the given LLM."""
        # return ChatPromptTemplate.from_messages(
        #     [
        #         ("system", """You are a travel itinerary planner. Your task is to extract relevant information from the user's query to plan a trip.
        #                 Extract the following information:
        #                 - Location (starting point)
        #                 - loc_code (an uppercase 3-letter airport code of the starting point, use the IATA airport codes, and if not available, use the city name. If there are multiple airports, choose the main one. Unless the user specifies a specific airport, use the city name.)
        #                 - destination
        #                 - dest_code (an uppercase 3-letter airport code of the destination. use the IATA airport codes, and if not available, use the city name. If there are multiple airports, choose the main one. Unless the user specifies a specific airport, use the city name.)
        #                 - travel_class (0: Not Specified, 1: Economy, 2: Premium Economy, 3: Business, 4: First). the travel class specified by the user, else 0 if not specified. This should be numeric values mapped to the corresponding travel class names.
        #                 - Start date
        #                 - End date
        #                 - Number of adults
        #                 - Number of children
        #                 - User preferences
        #                 - Accommodation options (Hotel or Airbnb). If the user does not specify, use the default value "Hotel".
        #                 - sort_by - Sorting criteria for flights. Default is "price". Determine the sorting criteria based on the user's query:
        #                             - If the user is looking for the cheapest flights, set sort_by to "price".
        #                             - If the user is looking for the shortest flights, set sort_by to "duration".
        #                             - If the user is looking for the earliest flight that leaves the airport, set sort_by to "departure".
        #                             - If the user is looking for the earliest flight that arrives at the destination, set sort_by to "arrival".
        #                             - If the user does not specify any preference, or if the query does not indicate urgency, set sort_by to "price".
                                    
        #                 If any information is missing, leave it as None. The year will always be 2025, unless specified otherwise by the user query.
        #                 The default number of adults is 1, and the default number of children is 0. If the user does not specify the number of adults or children, use the default values.
                        
        #                 For example, if the user query is "I want to travel from New York to Los Angeles on July 1st, 2022, with a budget of $5000 for 2 adults and 1 child, and return on July 20th, 2022. I plan to stay in a hotel." you should extract the following information:
        #                 - Location: New York
        #                 - loc_code: JFK
        #                 - Destination: Los Angeles
        #                 - dest_code: LAX
        #                 - travel_class: 0
        #                 - Start date: 2022-07-01
        #                 - End date: 2022-07-20
        #                 - Number of adults: 2
        #                 - Number of children: 1
        #                 - User preferences: {{ "budget": "$5000"}}
        #                 - Accommodation options: Hotel
        #                 - sort_by: price

        #                 Example 2:
        #                 User query: "I'm planning a luxury honeymoon trip from London to Tokyo in December 12, 2025 via Gatwick Its a five day trip with my husband and We'd like to fly first class with a budget of $15,000, staying in a high-end hotel. We want private airport transfers and dietary accommodations for a vegetarian diet, and we would like our flights to leave early. Activities should include cultural tours, fine dining, and shopping. There will be 2 adults, no children, and we need 1 suite."
        #                 Extracted information:
        #                 - Location: London
        #                 - loc_code: LGW
        #                 - Destination: Tokyo
        #                 - dest_code: HND
        #                 - travel_class: 4
        #                 - Start date: 2025-12-12
        #                 - End date: 2025-12-17
        #                 - Number of adults: 2
        #                 - Number of children: 0
        #                 - User preferences: {{ "trip_type": "Luxury", "budget": "$15,000", "transportation": "Private transfer", "diet": "Vegetarian", "activities": ["Cultural tours", "Fine dining", "Shopping"] }}
        #                 - Accommodation options: Hotel
        #                 - sort_by: departure
        #                 """),
        #         ("user", "{query}"),
        #     ]
        # ) | llm.with_structured_output(TravelItinerary)
        
        
#     llm = LangchainChatDeepSeek(
#         api_key=os.getenv("OPENAI_API_KEY"),
#         model="gpt-4o"
#     )

#     print("Creating chain...")
#     # Start with DeepSeek
#     chain = create_chain(llm)
    
#     messages = state.messages
#     if not state.messages:
#         raise ValueError("Error: No messages found in state.")
    
#     last_message = messages[-1].content if messages else "No query provided"
#     print("Last message", last_message)
    
#     # print(f"result: {chain.invoke({'query': last_message})}")
#     async def invoke_chain(chain):
#         """Runs the chain and handles errors gracefully."""
#         try:
#             # structured_output = await chain.ainvoke({"query": last_message})
#             structured_output = chain.invoke({"query": last_message})
#             if structured_output is None:
#                 raise ValueError("LLM returned None instead of a valid response.")
#             return structured_output
#         except Exception as e:
#             # print(f"Error occurred with LLM: {e}")
#             return None

#     # **First Attempt (DeepSeek)**
#     structured_output = await invoke_chain(chain)
#     print("Structured output", structured_output)
#     # **Switch to GPT-4o if DeepSeek Fails**
#     if structured_output is None:
#         chain = create_chain(llm_openai)
#         structured_output = await invoke_chain(chain)

#     # **Retry Once More if Both Fail**
#     if structured_output is None:
#         await asyncio.sleep(2)
#         structured_output = await invoke_chain(chain)

#     # Update the state with structured output
#     updated_state = {
#         "location": structured_output.location,
#         "loc_code": structured_output.loc_code,
#         "destination": structured_output.destination,
#         "dest_code": structured_output.dest_code,
#         "travel_class": structured_output.travel_class,
#         "start_date": structured_output.start_date,
#         "end_date": structured_output.end_date,
#         "num_adults": structured_output.num_adults,
#         "num_children": structured_output.num_children,
#         "user_preferences": structured_output.user_preferences,
#         "accommodation_options": structured_output.accommodation_options,
#         "sort_by": structured_output.sort_by
#     }

#     return updated_state


# Function to create the LLM processing chain
def create_chain(llm):
    """Creates an LLM chain for structured output."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", """You are a travel itinerary planner. Your task is to extract relevant information from the user's query to plan a trip.
                    Extract the following information:
                    - Location (starting point)
                    - loc_code (an uppercase 3-letter airport code of the starting point, use the IATA airport codes, and if not available, use the city name. If there are multiple airports, choose the main one. Unless the user specifies a specific airport, use the city name.)
                    - destination
                    - dest_code (an uppercase 3-letter airport code of the destination. use the IATA airport codes, and if not available, use the city name. If there are multiple airports, choose the main one. Unless the user specifies a specific airport, use the city name.)
                    - travel_class (0: Not Specified, 1: Economy, 2: Premium Economy, 3: Business, 4: First). the travel class specified by the user, else 0 if not specified. This should be numeric values mapped to the corresponding travel class names.
                    - Start date
                    - End date
                    - Number of adults
                    - Number of children
                    - User preferences
                    - Accommodation options (Hotel or Airbnb). If the user does not specify, use the default value "Hotel".
                    - sort_by - Sorting criteria for flights. Default is "price". Determine the sorting criteria based on the user's query:
                                - If the user is looking for the cheapest flights, set sort_by to "price".
                                - If the user is looking for the shortest flights, set sort_by to "duration".
                                - If the user is looking for the earliest flight that leaves the airport, set sort_by to "departure".
                                - If the user is looking for the earliest flight that arrives at the destination, set sort_by to "arrival".
                                - If the user does not specify any preference, or if the query does not indicate urgency, set sort_by to "price".
                                
                    If any information is missing, leave it as None. The year will always be 2025, unless specified otherwise by the user query.
                    The default number of adults is 1, and the default number of children is 0. If the user does not specify the number of adults or children, use the default values.
                    
                    For example, if the user query is "I want to travel from New York to Los Angeles on July 1st, 2022, with a budget of $5000 for 2 adults and 1 child, and return on July 20th, 2022. I plan to stay in a hotel." you should extract the following information:
                    - Location: New York
                    - loc_code: JFK
                    - Destination: Los Angeles
                    - dest_code: LAX
                    - travel_class: 0
                    - Start date: 2022-07-01
                    - End date: 2022-07-20
                    - Number of adults: 2
                    - Number of children: 1
                    - User preferences: {{ "budget": "$5000"}}
                    - Accommodation options: Hotel
                    - sort_by: price

                    Example 2:
                    User query: "I'm planning a luxury honeymoon trip from London to Tokyo in December 12, 2025 via Gatwick Its a five day trip with my husband and We'd like to fly first class with a budget of $15,000, staying in a high-end hotel. We want private airport transfers and dietary accommodations for a vegetarian diet, and we would like our flights to leave early. Activities should include cultural tours, fine dining, and shopping. There will be 2 adults, no children, and we need 1 suite."
                    Extracted information:
                    - Location: London
                    - loc_code: LGW
                    - Destination: Tokyo
                    - dest_code: HND
                    - travel_class: 4
                    - Start date: 2025-12-12
                    - End date: 2025-12-17
                    - Number of adults: 2
                    - Number of children: 0
                    - User preferences: {{ "trip_type": "Luxury", "budget": "$15,000", "transportation": "Private transfer", "diet": "Vegetarian", "activities": ["Cultural tours", "Fine dining", "Shopping"] }}
                    - Accommodation options: Hotel
                    - sort_by: departure
                    """),
            ("user", "{query}"),
        ]
    ) | llm.with_structured_output(TravelItinerary)


# Async function to process the user input
async def travel_itinerary_planner(state: OverallState) -> OverallState:
    """
    Extracts travel itinerary details from user input.
    Uses DeepSeek LLM first, and switches to GPT-4o if DeepSeek fails.
    If both fail, retries once more before returning a fallback response.
    """

    # print("Initializing LLMs...")
    # llm_deepseek, llm_openai = await initialize_llm()

    llm_openai = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )
    
    # Validate state messages
    if not state.messages:
        raise ValueError("Error: No messages found in state.")

    last_message = state.messages[-1].content if state.messages else "No query provided"
    # print(f"DEBUG: Last message received -> {last_message}")

    # Create chain
    chain = create_chain(llm_openai)
    # structured_output = chain.invoke({"query": last_message})
    # if structured_output is not None:
    #     print("Structured output 1:", structured_output)
    # else:
    #     print("Structured output 1 is None")
        
    # Function to invoke chain asynchronously
    async def invoke_chain(chain):
        """Runs the chain asynchronously and ensures it's truly async-compatible."""
        try:
            # print("started")
            # structured_output = await chain.ainvoke({"query": last_message})  # Async invocation
            structured_output = await asyncio.to_thread(chain.invoke, {"query": last_message})  # Async invocation
            # print("started structured output")
            if structured_output is None:
                raise ValueError("LLM returned None instead of a valid response.")
            return structured_output
        except Exception as e:
            # print(f"DEBUG: Error invoking async LLM: {e}")
            return None

    # def invoke_chain(chain):
    #     """Runs the chain asynchronously and ensures it's truly async-compatible."""
    #     try:
    #         print("started")
    #         # structured_output = await chain.ainvoke({"query": last_message})  # Async invocation
    #         structured_output = chain.invoke({"query": last_message})  # Async invocation
    #         print("started structured output")
    #         if structured_output is None:
    #             raise ValueError("LLM returned None instead of a valid response.")
    #         return structured_output
    #     except Exception as e:
    #         # print(f"DEBUG: Error invoking async LLM: {e}")
    #         return None
        
    # **First Attempt (DeepSeek)**
    structured_output = await invoke_chain(chain)
    # structured_output = invoke_chain(chain)

    # **Switch to GPT-4o if DeepSeek Fails**
    if structured_output is None:
        # print("DEBUG: Switching to GPT-4o...")
        chain = create_chain(llm_openai)
        structured_output = await invoke_chain(chain)

    # **Retry Once More if Both Fail**
    if structured_output is None:
        # print("DEBUG: Final Retry with GPT-4o...")
        await asyncio.sleep(2)
        structured_output = await invoke_chain(chain)

    # print(f"DEBUG: LLM Extracted -> {structured_output}")

    # **Update State and Return**
    updated_state = {
        "location": structured_output.location,
        "loc_code": structured_output.loc_code,
        "destination": structured_output.destination,
        "dest_code": structured_output.dest_code,
        "travel_class": structured_output.travel_class,
        "start_date": structured_output.start_date,
        "end_date": structured_output.end_date,
        "num_adults": structured_output.num_adults,
        "num_children": structured_output.num_children,
        "user_preferences": structured_output.user_preferences,
        "accommodation_options": structured_output.accommodation_options,
        "sort_by": structured_output.sort_by
    }

    return updated_state



#--------------------------------------------Flight Finder Node--------------------------------------------

# async def flight_finder_node(state: OverallState) -> OverallState:
#     """
#     A Node that calls the Google Flights tool to find flights based on the state inputs.
#     The results are stored in the `state.flights` list.
#     """
#     # print("Node Started Flight Node")
#     # Extract inputs from the state
#     departure_airport = state.loc_code
#     arrival_airport = state.dest_code
#     departure_date = state.start_date if state.start_date else None
#     return_date = state.end_date if state.end_date else None
#     adults = state.num_adults or 1
#     children = state.num_children or 0
#     travel_class = state.travel_class
#     sort_by = state.sort_by or "price"
   
#     # Define travel class mapping
#     travel_class_mapping = {
#         1: "economy",
#         2: "economy",  # Map premium economy to economy since it's not supported
#         3: "business",
#         4: "first",
#     }

#     async def search_flights():
#         """
#         Calls the Google Flights tool and returns results.
#         If an error occurs, it logs it and returns None.
#         """
#         try:
#             flights_list = []
#             if travel_class == 0:
#                 input_data = FlightSearchInput_2(
#                     departure_airport=departure_airport,
#                     arrival_airport=arrival_airport,
#                     departure_date=departure_date,
#                     return_date=return_date,
#                     adults=adults,
#                     children=children,
#                     travel_class="all",
#                     sort_by=sort_by,
#                 )
#             else:
#                 class_name = travel_class_mapping.get(travel_class, "economy")
#                 input_data = FlightSearchInput_2(
#                     departure_airport=departure_airport,
#                     arrival_airport=arrival_airport,
#                     departure_date=departure_date,
#                     return_date=return_date,
#                     adults=adults,
#                     children=children,
#                     travel_class=class_name,
#                     sort_by=sort_by,
#                 )

#             # Call the Google Flights tool
#             result = await google_flights_tool.coroutine(input_data)
#             # result = await asyncio.to_thread(google_flights_tool.func, input_data)

#             # Check if the response contains an error message
#             if isinstance(result, list) and len(result) > 0 and "error" in result[0]:
#                 # print(f"Flight API error detected: {result[0]['error']}")
#                 return result  # Return the error message instead of treating it as None
            
#             if not result:
#                 raise ValueError("No flights found.")

#             flights_list.extend(result)
            
#             return flights_list

#         except Exception as e:
#             # print(f"Flight search error: {e}")
#             return [{"error": f"Flight search failed: {str(e)}"}]
        
#     # **First Attempt**
#     flights = await search_flights()

#     # **Retry if an error message is present**
#     attempts = 0
#     while isinstance(flights, list) and len(flights) > 0 and "error" in flights[0] and attempts < 4:
#         # print(f"Retrying flight search (attempt {attempts + 1})...")
#         await asyncio.sleep(3)  # Short delay before retrying
#         flights = await search_flights()
#         attempts += 1
        
#     # **If all retries fail, assign the last error message as fallback**
#     if isinstance(flights, list) and len(flights) > 0 and "error" in flights[0]:
#         state.flights = flights
#     else:
#         state.flights = flights

#     # Return the updated state
#     return {
#         "flights": state.flights
#     }




async def flight_finder_node(state: OverallState) -> OverallState:
    """
    A Node that calls the Google Flights tool to find flights based on the state inputs.
    The results are stored in the state.flights list.
    """
    departure_airport = state.loc_code
    arrival_airport = state.dest_code
    departure_date = state.start_date if state.start_date else None
    return_date = state.end_date if state.end_date else None
    adults = state.num_adults or 1
    children = state.num_children or 0
    travel_class = state.travel_class
    sort_by = state.sort_by or "price"

    # Define travel class mapping
    travel_class_mapping = {
        1: "economy",
        2: "economy",
        3: "business",
        4: "first",
    }

    def create_input_data():
        """Helper function to create input data to avoid code duplication"""
        class_name = "all" if travel_class == 0 else travel_class_mapping.get(travel_class, "economy")
        return FlightSearchInput_2(
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            children=children,
            travel_class=class_name,
            sort_by=sort_by,
        )

    async def search_flights():
        """
        Calls the Google Flights tool and returns results.
        If an error occurs, it logs it and returns None.
        """
        try:
            input_data = create_input_data()
            result = await google_flights_tool.coroutine(input_data)

            if isinstance(result, list) and result and "error" in result[0]:
                return result

            if not result:
                raise ValueError("No flights found.")

            return result

        except Exception as e:
            return [{"error": f"Flight search failed: {str(e)}"}]

    async def search_flights_sync():
        """
        Synchronous fallback for flight search.
        """
        try:
            input_data = create_input_data()
            result = await asyncio.to_thread(google_flights_tool_sync.func, input_data)

            if isinstance(result, list) and result and "error" in result[0]:
                return result

            if not result:
                raise ValueError("No flights found.")

            return result

        except Exception as e:
            return [{"error": f"Flight search failed: {str(e)}"}]

    # Main search logic with retries
    flights = await search_flights()
    attempts = 0
    
    while (
        isinstance(flights, list) 
        and flights 
        and "error" in flights[0] 
        and attempts < 4
    ):
        await asyncio.sleep(3)
        flights = await search_flights()
        attempts += 1

    # Fallback to sync search if all retries fail
    if isinstance(flights, list) and flights and "error" in flights[0]:
        flights = await search_flights_sync()

    return {"flights": flights}


def flights_router(
    state: OverallState, messages_key: str = "flights"
) -> Literal["flight_node_1", "airbnb_node", "booking_com_node"]:
    """
    Determines the next step in the workflow based on the accommodation list.

    Args:
        state (OverallState): The state to evaluate.
        messages_key (str): The key to check for accommodation information.

    Returns:
        Literal["booking_com_node", "activities"]: The next node to route to.
    """
    flights = getattr(state, messages_key, None)
    accommodation_options = getattr(state, messages_key, None)
    
    if flights is not None:
        if not flights:  # If the flights list is empty
            return "flight_node_1"

        # Check if flights contain an error message (e.g., API limit exceeded)
        if isinstance(flights, list) and any(
            isinstance(entry, dict) and any(
                "error" in class_info and "429" in class_info["error"]
                for class_info in entry.values()
            )
            for entry in flights
        ):
            return "flight_node_1"  # Route to an alternative method for retrieving flights

    if accommodation_options:
        if accommodation_options == "Hotel":
            return "booking_com_node"
        else:
            return "airbnb_node"

    else:
        raise ValueError(f"Invalid state or missing key '{messages_key}': {state}")
   

async def flight_finder_tool_node(state: OverallState) -> OverallState:
    """
    A Tool Node that calls Google Flights tools in parallel
    and stores the results in the `flights` state variable.
    """
    # print("Node Started Flight Finder Tool Node")
    # Extract inputs from the state
    location = state.location
    loc_code = state.loc_code
    destination = state.destination
    dest_code = state.dest_code
    start_date = state.start_date if state.start_date else None
    end_date = state.end_date if state.end_date else None
    num_adults = state.num_adults or 1
    num_children = state.num_children or 0
    travel_class = state.travel_class
    user_preferences = state.user_preferences or {}  # Ensure it's always a dictionary

    # Initialize a temporary list to store flight results
    flights_dict = {}

    # Define travel class mapping
    travel_class_mapping = {
        1: "Economy",
        2: "Premium Economy",
        3: "Business",
        4: "First",
    }
    
    # Parallel flight search using asyncio.gather
    async def search_flights_for_class(flight_class, i):
        flight_search_input = FlightSearchInput(
            departure_id=loc_code,
            arrival_id=dest_code,
            outbound_date=start_date,
            return_date=end_date,
            adults=num_adults,
            children=num_children,
            currency=user_preferences.get("currency", "USD"),
            travel_class=i,
            sort_by=user_preferences.get("sort_by", 1)
        )

        return await flight_tool.coroutine(flight_search_input)

    if location and destination and start_date:
        tasks = [
            search_flights_for_class(flight_class, i) for i, flight_class in travel_class_mapping.items()
        ]
        flight_results = await asyncio.gather(*tasks)

        for i, flight_class in enumerate(travel_class_mapping.values(), 1):
            flights_dict[flight_class] = flight_results[i-1]
    else:
        flights_dict["error"] = "Incomplete travel details. Missing location, destination, or start date."

    return {"flights": [flights_dict]}

#-------------------------------------------- Accommodation Finder --------------------------------------------

def accomodation_router(
    state: OverallState, messages_key: str = "accommodation_options"
) -> Literal["booking_com_node", "airbnb_node"]:
    """
    Determines the next step in the workflow based on the accommodation options.

    Args:
        state (OverallState): The state to evaluate.
        messages_key (str): The key to check for accommodation options.

    Returns:
        Literal["booking_com_node", "airbnb_node"]: The next node to route to.
    """
    accommodation_options = getattr(state, messages_key, None)
    if accommodation_options:
        if accommodation_options == "Hotel":
            return "booking_com_node"
        else:
            return "airbnb_node"
    else:
        raise ValueError(f"Invalid state or missing key '{messages_key}': {state}")


def accomodation_router_2(
    state: OverallState, messages_key: str = "accommodation"
) -> Literal["booking_com_node", "activities_node"]:
    """
    Determines the next step in the workflow based on the accommodation list.

    Args:
        state (OverallState): The state to evaluate.
        messages_key (str): The key to check for accommodation information.

    Returns:
        Literal["booking_com_node", "activities"]: The next node to route to.
    """
    accommodation = getattr(state, messages_key, None)
    if accommodation is not None:
        if not accommodation:  # If the accommodation list is empty
            return "booking_com_node"
        else:
            return "activities_node"
    else:
        raise ValueError(f"Invalid state or missing key '{messages_key}': {state}")


class AccommodationOutput(BaseModel):
    location: str = Field(..., description="The exact location or neighborhood where the traveler wants to stay (e.g., 'Brooklyn').")
    checkin_date: str = Field(..., description="The check-in date in YYYY-MM-DD format.")
    checkout_date: str = Field(..., description="The check-out date in YYYY-MM-DD format.")
    adults: int = Field(..., description="The number of adult guests.")
    rooms: int = Field(..., description="The number of rooms.")
    currency: str = Field(..., description="The currency for the prices.")


async def airbnb_node(state: OverallState) -> OverallState:
    """
    This node extracts accommodation details from the user's query in state.messages
    and returns a structured output that can be passed to the booking tool.
    """
    # print("Node Started Airbnb Node")
    llm = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    llm_with_structure = llm.with_structured_output(AccommodationOutput)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are an advanced travel planner assistant. Your task is to extract accommodation details
        from the traveler's query. Use the following information to generate a structured output for
        booking accommodations:

        ### Traveler Query:
        {query}

        ### Instructions:
        1. Extract the exact location or neighborhood where the traveler wants to stay (e.g., "Brooklyn").
           - If the traveler does not specify a location, use the city or city code provided in the state.
        2. Extract the check-in and check-out dates from the query.
           - If the dates are not explicitly mentioned, use the default dates from the state.
        3. Extract the number of adults and rooms from the query.
           - If not specified, use the default values: 1 adult and 1 room.
        4. Use the default currency 'USD' unless specified otherwise.
        5. Return the structured output in the following format:
           - location: The exact location or neighborhood.
           - checkin_date: The check-in date in YYYY-MM-DD format.
           - checkout_date: The check-out date in YYYY-MM-DD format.
           - adults: The number of adult guests.
           - rooms: The number of rooms.
           - currency: The currency for the prices.

        ### Example Output:
        - location: "Brooklyn"
        - checkin_date: "2023-12-01"
        - checkout_date: "2023-12-10"
        - adults: 2
        - rooms: 1
        - currency: "USD"
        """,
        input_variables=["query"]
    )

    # Create the chain
    chain = prompt | llm_with_structure

    # Extract the user's query from state.messages
    query = state.messages[-1].content  # Assuming the last message is the user's query

    # Invoke the chain to generate the structured output
    structured_output = await chain.ainvoke({"query": query})

    # Call Google Flights Search Tool        
    booking_search_input = AirbnbSearchInput(
        location=structured_output.location,
        checkin_date=structured_output.checkin_date,
        checkout_date=structured_output.checkout_date,
        currency=structured_output.currency,
        margin_km=5.0
    )

    airbnb_results = await airbnb_tool.func(booking_search_input)
    
    # Update the state with the structured output
    # state.accommodation = airbnb_results

    # Return the updated state
    return {
        "accommodation": airbnb_results
    }


# Define the structured output for the accommodation finder

async def accommodation_finder_node(state: OverallState) -> OverallState:
    """
    This node extracts accommodation details from the user's query in state.messages
    and returns a structured output that can be passed to the booking tool.
    """
    # print("Node Started Accommodation Node")
    # llm_deepseek, llm = await initialize_llm()
    
    llm = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
        )
    
    llm_with_structure = llm.with_structured_output(AccommodationOutput)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are an advanced travel planner assistant. Your task is to extract accommodation details
        from the traveler's query. Use the following information to generate a structured output for
        booking accommodations:

        ### Traveler Query:
        {query}

        ### Instructions:
        1. Extract the exact location or neighborhood where the traveler wants to stay (e.g., "Brooklyn").
           - If the traveler does not specify a location, use the city or city code provided in the state.
        2. Extract the check-in and check-out dates from the query.
           - If the dates are not explicitly mentioned, use the default dates from the state.
        3. Extract the number of adults and rooms from the query.
           - If not specified, use the default values: 1 adult and 1 room.
        4. Use the default currency 'USD' unless specified otherwise.
        5. Return the structured output in the following format:
           - location: The exact location or neighborhood.
           - checkin_date: The check-in date in YYYY-MM-DD format.
           - checkout_date: The check-out date in YYYY-MM-DD format.
           - adults: The number of adult guests.
           - rooms: The number of rooms.
           - currency: The currency for the prices.

        ### Example Output:
        - location: "Brooklyn"
        - checkin_date: "2023-12-01"
        - checkout_date: "2023-12-10"
        - adults: 2
        - rooms: 1
        - currency: "USD"
        """,
        input_variables=["query"]
    )

    # Create the chain
    chain = prompt | llm_with_structure

    # Extract the user's query from state.messages
    query = state.messages[-1].content  # Assuming the last message is the user's query

    # Invoke the chain to generate the structured output
    structured_output = await chain.ainvoke({"query": query})

    # Call Google Flights Search Tool        
    booking_search_input = BookingSearchInput(
        location=structured_output.location,
        checkin_date=structured_output.checkin_date,
        checkout_date=structured_output.checkout_date,
        adults=structured_output.adults,
        rooms=structured_output.rooms,
        currency=structured_output.currency,
    )

    booking_results = await booking_tool.func(booking_search_input)
    
    # Update the state with the structured output
    # state.accommodation = booking_results

    # Return the updated state
    return {
        "accommodation": booking_results
    }



#-------------------------------------------- Activity Planner Node --------------------------------------------


async def activities_node(state: OverallState) -> OverallState:
    """
    This node uses a React agent to find exciting activities and places for the user.
    If an error occurs (e.g., "No generation chunks were returned"), the function retries up to 3 times.
    """
    # print("Node Started Activities Node")
    def parse_activities_output(activities_output: str) -> List[Dict[str, Any]]:
        """
        Parses the raw string output of activities into a list of dictionaries.
        """
        activities = re.split(r"\n\d+\.\s+", activities_output)
        activities = [act.strip() for act in activities if act.strip()]

        parsed_activities = []
        for activity in activities:
            title_match = re.match(r"^\*\*(.*?)\*\*", activity)
            if title_match:
                title = title_match.group(1).strip()
                description_match = re.search(r":\s*(.*?)\s*(?=Type:|$)", activity, re.DOTALL)
                description = description_match.group(1).strip() if description_match else "No description provided."

                type_match = re.search(r"Type:\s*\[(.*?)\]", activity)
                activity_type = [t.strip().strip('"') for t in type_match.group(1).split(",")] if type_match else []

                parsed_activities.append({
                    "title": title,
                    "description": description,
                    "type": activity_type
                })

        return parsed_activities
    
    # print("Node Started Activities Node")
    llm = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
        )
    
    # llm_deepseek, llm = await initialize_llm()
    preferences = state.user_preferences
    query = state.messages[-1].content if state.messages else "No query provided"
    destination = state.dest_code  

    preferences_str = "\n".join([f"{key}: {value}" for key, value in preferences.items()]) if preferences else "{}"

    prompt = PromptTemplate.from_template(ACTIVITY_PLANNER_PROMPT)
    
    search_agent = create_react_agent(
        llm=llm,
        tools=[tavily_search_tool],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=search_agent,
        tools=[tavily_search_tool],
        verbose=False,  # Enable for debugging
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )

    MAX_RETRIES = 3
    success = False  # Flag to track if execution succeeds

    for attempt in range(MAX_RETRIES):
        try:
            result = agent_executor.invoke({
                "input": f"Find exciting activities and places for the user in {query}.",
                "preferences": preferences_str,
                "query": query,
                "agent_scratchpad": ""  
            })
            # print(f"Attempt {attempt + 1}: Agent output - {result.get('output', '')}")
            
            activities_output = result.get("output", "").strip()
            # print(f'Activities: {activities_output}')
            # Explicit check for invalid responses
            if not activities_output or activities_output in ["No generation chunks were returned", ""]:
                raise ValueError("Invalid or empty response from agent.")

            success = True  # Mark success and break out of retry loop
            break  

        except ValueError as e:
            # print(f"Attempt {attempt + 1}: Error - {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(3)  
            else:
                # print("Max retries reached. Using fallback response.")
                activities_output = "No activities found due to an error."

        except Exception as e:
            # print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(3)
            else:
                # print("Max retries reached. Using fallback response.")
                activities_output = "Error processing activities request."

    if not success:
        activities_output = "No activities found due to an error."

    state.messages.append(AIMessage(content=activities_output))
    activities_list = parse_activities_output(activities_output)

    detailed_places_list = []
    
    for activity in activities_list:
        places_input = GoogleMapsPlacesInput(
            query=activity["title"],
            location=destination,
            radius=5000,
            type=activity["type"],
            language="en",
            min_price=0,
            open_now=False
        )

        try:
            results = await google_places_tool.func(places_input)
        except Exception as e:
            # print(f"Error calling Google Maps Places API: {e}")
            results = {"places_search_result": {"status": "ZERO_RESULTS"}}

        places_list = []
        if "places_search_result" in results:
            if results["places_search_result"]["status"] == "ZERO_RESULTS":
                places_list.append({
                    "name": activity["title"],
                    "description": activity["description"],
                    "address": None,
                    "rating": None,
                    "photo": None
                })
            else:
                places = results["places_search_result"]["results"]
                for place in places[:3]:
                    photo_reference = place.get("photos", [{}])[0].get("photo_reference") if place.get("photos") else None
                    places_list.append({
                        "name": place.get("name"),
                        "address": place.get("formatted_address"),
                        "rating": place.get("rating"),
                        "photo": photo_reference
                    })

        detailed_places_list.extend(places_list)

    # state.activities = detailed_places_list
    return {
        "activities": detailed_places_list
    }


#--------------------------------------------TicketMaster Node --------------------------------------------

# Define the structured output class for the LLM
class TicketmasterOutput(BaseModel):
    location: str = Field(..., description="The city or region where the traveler is going (e.g., 'New York').")
    start_date_time: str = Field(..., description="The start date and time for event search in ISO 8601 format (e.g., '2025-02-01T00:00:00Z').")
    end_date_time: str = Field(..., description="The end date and time for event search in ISO 8601 format (e.g., '2025-02-28T23:59:59Z').")
    keywords: List[str] = Field(..., description="A list of keywords representing exciting activities or events for the location (e.g., ['music', 'theater', 'tech']).")
    country_code: str = Field(..., description="The country code for the location (e.g., 'US').")
    size: int = Field(..., description="The number of events to retrieve per keyword.")
    page: int = Field(..., description="The page number for pagination.")
    sort: str = Field(..., description="The sorting criteria for events.")

# Define the Ticketmaster node
async def ticketmaster_node(state: OverallState) -> OverallState:
    """
    This node extracts event details from the user's query in state.messages,
    generates a list of keywords based on the location and preferences,
    and searches for events using the Ticketmaster API.
    """
    # llm_deepseek, llm = await initialize_llm()
    # print("Node Started TicketMaster Node")
    llm = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
        )
    llm_with_structure = llm.with_structured_output(TicketmasterOutput)

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are an advanced event assistant for TicketMaster, a company that sells and distributes tickets for live events. 
        It's the world's largest ticket marketplace, offering tickets for concerts, sports games, theater shows, and more.
        Your task is to extract event details from the traveler's destination in the traveler's query and generate a list of keywords 
        representing exciting live events specifically tailored to the location they are visiting. The focus is solely on live events that 
        can be sold via tickets, such as concerts, comedy, shows, theater, movies, Broadway, club, and similar. 
        DO NOT include user preferences like museums, parks, or sightseeing. Use the following information to generate
        a structured output for searching events:
        
        ### Traveler Query:
        {query}
        
        ### Instructions:
        1. Extract the city or region where the traveler is going (e.g., "New York").
           - If the traveler does not specify a location, use the city or city code provided in the state.
        2. Extract the start and end dates for event search from the query.
           - If the dates are not explicitly mentioned, use the default dates from the state.
        3. Generate a list of **exciting** keywords representing live events for the location.
           - Keywords should be specific to the destination's live event culture. 
           - For example:
                - New York: ["Broadway", "theater", "music", "comedy shows", "movies"]
                - Los Angeles: ["music", "concerts", "movies", "comedy"]
                - Nashville: ["country", "music", "concerts", "live", "shows", "music, "festivals"]
           - Keywords must focus on ticketable live events and exclude non-ticketed activities or generic places.
           - I would recommend from only 3 to 5 keywords, from the following categories:
                - ["Broadway", "theater", "music", "comedy, shows", "movies", "concerts", "live", "festivals", "country"]
        4. Use the default country code 'US' unless specified otherwise.
        5. Return the structured output in the following format:
           - location: The city or region.
           - start_date_time: The start date and time in ISO 8601 format.
           - end_date_time: The end date and time in ISO 8601 format.
           - keywords: A list of keywords.
           - country_code: The country code.
           - size: The number of events to retrieve per keyword. If not specified, use the default value of 15.
           - page: The page number for pagination. If not specified, use the default value of 1.
           - sort: The sorting criteria for events. If not specified, use the default value of "relevance,desc".
        ### Example Output:
        - location: "New York"
        - start_date_time: "2025-02-01T00:00:00Z"
        - end_date_time: "2025-02-28T23:59:59Z"
        - keywords: ["music", "theater", "movies"]
        - country_code: "US"
        - size: 15
        - page: 1
        - sort: "relevance,desc"
        """,
        input_variables=["query"]
    )

    # Create the chain
    chain = prompt | llm_with_structure

    # Extract the user's query from state.messages
    query = state.messages[-1].content  # Assuming the last message is the user's query

    # Invoke the chain to generate the structured output
    structured_output = await chain.ainvoke({"query": query})

    # Initialize an empty list to store all event results
    all_event_results = []

    # Loop through each keyword and call the Ticketmaster API
    for keyword in structured_output.keywords:
        # Prepare the input for the Ticketmaster API
        ticketmaster_input = TicketmasterEventSearchInput(
            keyword=keyword,
            city=structured_output.location,
            country_code=structured_output.country_code,
            start_date_time=structured_output.start_date_time,
            end_date_time=structured_output.end_date_time,
            size=structured_output.size if structured_output.size else 15,
            page=structured_output.page if structured_output.page else 1,
            sort=structured_output.sort if structured_output.sort else "relevance,desc"
        )

        # Call the Ticketmaster API
        event_results = await ticketmaster_tool.func(ticketmaster_input)
        # Extend the all_event_results list with the results
        all_event_results.extend(event_results)

    # Update the state with the event results
    # state.live_events = all_event_results

    # Return the updated state
    return {
        "live_events": all_event_results
    }


#---------------------------------------------------------- Recommendations Node --------------------------------------------
# use weather_tool to get the weather forecast for the location
# the use LLM to interpret the weather forecast,
# and return the interpretation as a string



class Recommendations(BaseModel):
    recommendations: Optional[List[Dict[str, str]]] = Field(description="The user's current location or starting point.")

async def recommendations_node(state):
    # print("Node Started Recommendations Node")
    # Ensure you have OpenAI API key set up
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    client = OpenAI(
        api_key = os.getenv("OPENAI_API_KEY")
        )
    
    all_messages = "\n".join([message.content for message in state.messages])
    preferences_text = "\n".join([f"{key}: {value}" for key, value in (state.user_preferences or {}).items()])

    query = f"{all_messages}\n\nUser Preferences:\n{preferences_text}"

    try:
        # Remove `await` from the `.create()` call
        completion = client.chat.completions.create(
            model="gpt-4o",  # Ensure this is a valid model
            messages=[
                {"role": "system", "content": RECOMMENDATION_PROMPT_2},
                {"role": "user", "content": query},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "recommendation_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "key": {
                                            "type": "string",
                                            "description": "Short label for the recommendation"
                                        },
                                        "value": {
                                            "type": "string",
                                            "description": "Concise recommendation content"
                                        }
                                    },
                                    "required": ["key", "value"],
                                    "additionalProperties": False
                                },
                                "description": "A list of travel recommendations."
                            }
                        },
                        "required": ["recommendations"],
                        "additionalProperties": False
                    }
                },
            },
        )

        structured_output = completion.choices[0].message.content
        parsed_output = json.loads(structured_output)
        recommendation_list = parsed_output["recommendations"]
        transformed_list = [{item["key"]: item["value"]} for item in recommendation_list]

        state.recommendations = transformed_list
        return state

    except Exception as e:
        # print(f"Error occurred: {e}")
        return {"error": "Failed to generate recommendations."}
    
    
    
async def recommendations_node_2(state: OverallState) -> OverallState:
    """
    This node uses a React agent to find crucial travel advice and insights for the user.
    """
    # print("Node Started Recommendations Node 2")
    async def parse_json_output(output: str):
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []
    
    async def extract_recommendations_3(output: str):
        """
        Extracts a list of dictionaries from the provided string output.

        Args:
            output (str): The string containing travel recommendations.

        Returns:
            list[dict]: A list of dictionaries with the extracted recommendations.
        """
        # Define a regex pattern to capture the key-value pairs in the recommendations
        pattern = r'\*\*\{"(.*?)": "(.*?)"\}\*\*'
        
        # Find all matches using regex
        matches = re.findall(pattern, output)
        
        # Convert matches to a list of dictionaries
        recommendations = [{key: value} for key, value in matches]
        
        return recommendations


    async def extract_recommendations_1(output: str):
        """
        Extracts a list of dictionaries from the provided string output.

        Args:
            output (str): The string containing travel recommendations.

        Returns:
            list[dict]: A list of dictionaries with the extracted recommendations.
        """
        # Split the output into lines and look for the numbered recommendations
        recommendations = []
        lines = output.split("\n")

        for line in lines:
            # Match lines that start with a number followed by a period and a space
            match = re.match(r"^(\d+)\.\s*\*\*(.*?)\*\*:\s*(.*)$", line)
            if match:
                number = match.group(1)  # The recommendation number (optional if needed)
                key = match.group(2).strip()  # The key (e.g., "Crime Rate")
                value = match.group(3).strip()  # The value (e.g., "New York City is generally safe...")
                recommendations.append({key: value})

        return recommendations


    async def extract_recommendations_2(output: str):
        """
        Extracts a list of dictionaries from the provided string output.

        Args:
            output (str): The string containing travel recommendations.

        Returns:
            list[dict]: A list of dictionaries with the extracted recommendations.
        """
        # Match JSON-like structure for recommendations in the output
        recommendations = []

        try:
            # Attempt to load the output as JSON if it's already formatted that way
            recommendations = json.loads(output)
        except json.JSONDecodeError:
            # Fallback to regex-based extraction for non-JSON outputs
            lines = output.split("\n")

            for line in lines:
                # Match lines that start with a number followed by a period and a space
                match = re.match(r"^\s*\{\s*\"(.*?)\"\s*:\s*\"(.*?)\"\s*\}\s*$", line)
                if match:
                    key = match.group(1).strip()  # Extract the key
                    value = match.group(2).strip()  # Extract the value
                    recommendations.append({key: value})

        return recommendations

    # Extract user preferences and query from the state
    if not state.messages:
        state.messages.append(AIMessage(content="Please provide a destination or query."))
        return state

    # llm_deepseek, llm = await initialize_llm()
    # print("Node Started Recommendations Node")
    llm = LangchainChatDeepSeek(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
        )
    
    query = state.messages[0].content  
    
    # Create the React agent prompt
    prompt = PromptTemplate.from_template(RECOMMENDATION_PROMPT)

    # Create the React agent
    search_agent = create_react_agent(
        llm=llm,
        tools=[tavily_search_tool, weather_tool],
        prompt=prompt,
        # max_execution_time=60
    )

    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=search_agent,
        tools=[tavily_search_tool, weather_tool],
        verbose=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_execution_time=60
    )

    # Invoke the agent
    result = await asyncio.to_thread(agent_executor.invoke, {
        "input": f"Find exciting activities and places for the user in {query}.",
        "query": query,
        "agent_scratchpad": ""  # Initialize with an empty scratchpad
    })

    activities_output = result.get("output", "")
    
    activities = await parse_json_output(activities_output)
    
    # Try extract_recommendations_1 first
    if not activities:
        activities = await extract_recommendations_1(activities_output)

    # If no result, try extract_recommendations_2
    if not activities:
        activities = await extract_recommendations_2(activities_output)

    # If still no result, try extract_recommendations_3
    if not activities:
        activities = await extract_recommendations_3(activities_output)

    # state.recommendations = activities
    state.messages.append(AIMessage(content=activities_output))

    return {
        "recommendations": activities,
        
    }



def recommendation_router(
    state: OverallState, messages_key: str = "recommendations"
) -> Literal["recommendation_node_2", "__end__"]:
    """
    Determines the next step in the workflow based on the accommodation list.

    Args:
        state (OverallState): The state to evaluate.
        messages_key (str): The key to check for accommodation information.

    Returns:
        Literal["booking_com_node", "activities"]: The next node to route to.
    """
    recommendation = getattr(state, messages_key, None)
    if recommendation is not None:
        if not recommendation: # If the accommodation list is empty
            return "recommendation_node_2"
        else:
            return "__end__"
    else:
        raise ValueError(f"Invalid state or missing key '{messages_key}': {state}")
