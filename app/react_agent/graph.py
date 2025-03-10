"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import datetime, timezone
from typing import Dict, List, Literal, cast
import os 
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI as LangchainChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.react_agent.configuration import Configuration
from app.react_agent.state import InputState, OverallState, OutputState
from app.react_agent.utils import load_chat_model
from langgraph.prebuilt import tools_condition
from app.react_agent.prompts import SYSTEM_PROMPT, FLIGHT_FINDER_PROMPT, ACTIVITY_PLANNER_PROMPT

from app.react_agent.agent import ( travel_itinerary_planner, flight_finder_tool_node,airbnb_node,
                                accommodation_finder_node, activities_node, ticketmaster_node, recommendations_node, flight_finder_node,
                                accomodation_router, accomodation_router_2, flights_router, recommendations_node_2, recommendation_router)

from app.react_agent.tools import (TOOLS, weather_tool,
                                   FlightSearchInput,
                                   flight_tool, booking_tool, tavily_search_tool,
                                   flight_tools_condition, accomodation_tools_condition, activity_planner_tools_condition,
                                   GoogleMapsPlacesInput, google_places_tool,
                                   TicketmasterEventSearchInput, ticketmaster_tool,)

from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
from datetime import date
import logging
import datetime
import asyncio

# Suppress debug messages from ipywidgets
logging.getLogger('ipywidgets').setLevel(logging.WARNING)
logging.getLogger('comm').setLevel(logging.WARNING)
logging.getLogger('tornado').setLevel(logging.WARNING)
logging.getLogger('traitlets').setLevel(logging.WARNING)

# Disable all logging globally
logging.disable(logging.CRITICAL)  # Disable all logging below CRITICAL level

# Redirect all logging output to os.devnull
logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])

# Suppress warnings as well (optional)
import warnings
warnings.filterwarnings("ignore")

# Define a new graph
class PocketTraveller:
    def __init__(self):
        self.builder = StateGraph(OverallState)
        self._build_graph()
        self.graph = self.builder.compile()
        self.graph.name = "Travel Itinerary Planner"
    
    def _build_graph(self):
        # ----------------------------------------- Nodes ---------------------------------------------------
        self.builder.add_node("interface", travel_itinerary_planner)
        self.builder.add_node("flight_node", flight_finder_tool_node)
        self.builder.add_node("flight_node_1", flight_finder_node)
        self.builder.add_node("booking_com_node", accommodation_finder_node)
        self.builder.add_node("airbnb_node", airbnb_node)
        self.builder.add_node("activities_node", activities_node)
        self.builder.add_node("live_events_node", ticketmaster_node)
        self.builder.add_node("recommendation_node", recommendations_node)
        self.builder.add_node("recommendation_node_2", recommendations_node_2)

        # ----------------------------------------- Edges ---------------------------------------------------
        self.builder.add_edge(START, "interface")
        self.builder.add_edge("interface", "flight_node")

        self.builder.add_conditional_edges("flight_node", flights_router)
        self.builder.add_conditional_edges("flight_node_1", accomodation_router)
        self.builder.add_conditional_edges("airbnb_node", accomodation_router_2)
        self.builder.add_conditional_edges("recommendation_node", recommendation_router)

        self.builder.add_edge("booking_com_node", "activities_node")
        self.builder.add_edge("activities_node", "live_events_node")
        self.builder.add_edge("live_events_node", "recommendation_node")
        self.builder.add_edge("recommendation_node_2", END)
    
    async def invoke_graph(self, user_input):
        # input_state = {"messages": [HumanMessage(content=user_input)]}
        # input_state = OverallState(messages=[HumanMessage(content=user_input)])  # Let the graph initialize OverallState
        
        # Initialize the state with placeholder values that can be overwritten
        input_state = OverallState(
            messages=[HumanMessage(content=user_input)],  # Appends new messages
            location="",  # Placeholder, can be updated later
            loc_code="",  # Placeholder for airport code
            destination="",  # Placeholder for destination
            dest_code="",  # Placeholder for destination airport code
            budget=0.0,  # Placeholder for budget, can be updated
            travel_class=0,  # Default as 'None' (0), overwritable
            start_date=None,  # Initially None, gets updated when available
            end_date=None,  # Initially None, gets updated when available
            num_adults=1,  # Default to 1 adult if not specified
            num_children=0,  # Default to 0 children if not specified
            sort_by="price",  # Default sorting criteria
            user_preferences={},  # Empty dictionary, will be populated dynamically
            accommodation_options="Hotel",  # Default to "Hotel"
            flights=[],  # Placeholder list, will be populated later
            accommodation=[],  # Placeholder list, will be populated later
            activities=[],  # Placeholder list, will be populated later
            live_events=[],  # Placeholder list, will be populated later
            recommendations=[],  # Placeholder list, will be populated later
        )

        return await self.graph.ainvoke(input_state, {"recursion_limit": 3000})

# Example usage:
# planner = PocketTraveller()
# output = asyncio.run(planner.invoke_graph("User input here"))





# # Define a new graph
# # ----------------------------------------- Nodes ---------------------------------------------------
# builder = StateGraph(OverallState, input = InputState, config_schema=Configuration)
# builder.add_node("interface", travel_itinerary_planner)
# builder.add_node("flight_node", flight_finder_tool_node)
# builder.add_node("flight_node_1", flight_finder_node)
# builder.add_node("booking_com_node", accommodation_finder_node)
# builder.add_node("airbnb_node", airbnb_node)
# builder.add_node("activities_node", activities_node)
# builder.add_node("live_events_node", ticketmaster_node)
# builder.add_node("recommendation_node", recommendations_node)
# builder.add_node("recommendation_node_2", recommendations_node_2)


# # ----------------------------------------- Edges ---------------------------------------------------
# builder.add_edge(START, "interface")
# builder.add_edge("interface", "flight_node")

# builder.add_conditional_edges(
#     "flight_node",
#     flights_router,
# )

# builder.add_conditional_edges(
#     "flight_node_1",
#     accomodation_router,
# )
# builder.add_conditional_edges(
#     "airbnb_node",
#     accomodation_router_2,
# )

# builder.add_conditional_edges(
#     "recommendation_node",
#     recommendation_router,
# )

# builder.add_edge("booking_com_node", "activities_node")
# builder.add_edge("activities_node", "live_events_node")
# builder.add_edge("live_events_node", "recommendation_node")
# builder.add_edge("recommendation_node_2", END)

# # ---------------------------------------- Graph ---------------------------------------------------
# graph = builder.compile()
# graph.name = "Travel Itinerary Planner"



# # ----------------------------------------- Invoke the Graph ---------------------------------------------------
# # # **Input Collection**
# # user_input = """ I want to travel from Los Angeles to New York on 2025-2-15 and return on 2025-2-22 via La Guardia Airport. 
# # There is 1 adult. My budget is $5000. I need 1 room in The Bronx for 5 days. I prefer an AirBnB with free breakfast and a 
# # swimming pool. I also want to visit the museums and enjoy local cuisine, and go to the club at night. I might also want a massage.
# # """    


# # # **Input State**
# # input_state = {"messages": [HumanMessage(content=user_input)]}

# # # **Graph Invocation**
# # output = graph.invoke(input_state, {"recursion_limit": 3000})