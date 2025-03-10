"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Sequence, Annotated
from langchain.schema import BaseMessage
import operator
from datetime import date


@dataclass  
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[list[BaseMessage], add_messages] = field(default_factory=list)
    "Stores the sequence of messages exchanged between the user and the agent."
    
    """
    Messages tracking the primary execution state of the agent.

    Typically accumulates a pattern of:
    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    4. AIMessage without .tool_calls - agent responding in unstructured format to the user
    5. HumanMessage - user responds with the next conversational turn

    Steps 2-5 may repeat as needed.

    The `add_messages` annotation ensures that new messages are merged with existing ones,
    updating by ID to maintain an "append-only" state unless a message with the same ID is provided.
    """



@dataclass
class OverallState:
    
    # Agent Workflow Tracking
    messages: Annotated[list[BaseMessage], add_messages] = field(default_factory=list)
    "Stores the sequence of messages exchanged between the user and the agent."
    location: Optional[str] = field(default=None)
    "The user's current location or starting point."
    loc_code: Optional[str] = field(default=None)
    "The airport code of the user's current location."
    destination: Optional[str] = field(default=None)
    "The destination the user wants to travel to."
    dest_code: Optional[str] = field(default=None)
    "The airport code of the user's destination."
    budget: Optional[float] = field(default=None)
    "The user's travel budget in their chosen currency."
    travel_class: Optional[int] = field(default=None)  # Add this line
    "The travel class chosen by the user (0: None, 1: Economy, 2: Premium Economy, 3: Business, 4: First)."
    start_date: Optional[date] = field(default=None)
    "The start date of the trip."
    end_date: Optional[date] = field(default=None)
    "The end date of the trip."
    num_adults: Optional[int] = field(default=None)
    "The number of adults traveling."
    num_children: Optional[int] = field(default=None)
    "The number of children traveling."
    sort_by: Optional[str] = field(default=None)
    "The sorting criteria of flight chosen by the user (e.g., price, duration, departure, arrival)."
    
    # User Preferences
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    "Stores the user's input (e.g., destination, budget, dates)."
    accommodation_options: Literal["Hotel", "Airbnb"] = "Hotel"
    "The type of accommodation chosen by the user."
    
    # Agent Outputs
    flights: Optional[List[Dict[str, Any]]] = field(default=None)
    "Stores the flight options found by the Flight Finder agent."
    accommodation: Optional[List[Dict[str, Any]]] = field(default=None)
    "Stores the accommodation options found by the Accommodation Finder agent (hotels, Airbnb, hostels, etc.)."
    activities: Optional[List[Dict[str, Any]]] = field(default=None)
    "Stores the activity options found by the Activity Planner agent."
    live_events: Optional[List[Dict[str, Any]]] = field(default=None)
    "Stores live events found by the Real-Time Data Provider agent."
    recommendations: Optional[List[Dict[str, Any]]] = field(default=None)
    "Stores recommendations from the Real-Time Data Provider agent (e.g., car rental, weather, crime rates)."
     
    
@dataclass
class OutputState:
    """Represents the final output state to be returned to the user or system."""
    messages: Annotated[list[BaseMessage], add_messages] = field(default_factory=list)
    "Stores the sequence of messages exchanged between the user and the agent."
