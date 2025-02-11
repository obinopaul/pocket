import datetime

def pretty_print_output(output):
    """
    Pretty-print the travel output dictionary and return formatted components.
    Returns tuple of (overview_table, flights_table, accommodations_table, 
    activities_table, events_table, recommendations_table)
    """
    # Keep all the utility functions unchanged
    def ascii_table(headers, rows, title=None):
        if not headers:
            return ""
            
        str_rows = []
        for r in rows:
            str_rows.append([str(item) if item is not None else "" for item in r])
            
        col_widths = [len(h) for h in headers]
        for r in str_rows:
            for i, cell in enumerate(r):
                col_widths[i] = max(col_widths[i], len(cell))
                
        def build_divider(col_widths):
            line_elems = ["+" + "-"*(w+2) for w in col_widths]
            return "".join(line_elems) + "+"
            
        divider = build_divider(col_widths)
        
        def build_header(headers, col_widths):
            line = ""
            for h, w in zip(headers, col_widths):
                line += "| " + h + " "*(w - len(h)) + " "
            line += "|"
            return line
            
        header_line = build_header(headers, col_widths)
        
        def build_row(row, col_widths):
            line = ""
            for cell, w in zip(row, col_widths):
                line += "| " + cell + " "*(w - len(cell)) + " "
            line += "|"
            return line
            
        lines = []
        if title:
            lines.append(title)
        lines.append(divider)
        lines.append(header_line)
        lines.append(divider)
        for r in str_rows:
            lines.append(build_row(r, col_widths))
        lines.append(divider)
        return "\n".join(lines)

    def format_duration(minutes):
        if not isinstance(minutes, int):
            return str(minutes)
        hrs = minutes // 60
        mins = minutes % 60
        return f"{hrs}h {mins}m"

    def embed_link(text, url):
        if url:
            return f"[{text}]({url})"
        return text

    def extract_numeric_price(p):
        if not p:
            return 9999999
        try:
            return float(p.replace('$', '').strip())
        except:
            return 9999999

    def parse_event_datetime(evt):
        date_str = evt.get('Date', '')
        time_str = evt.get('Time', '00:00:00')
        if not date_str:
            return datetime.datetime.max
        dt_str = f"{date_str} {time_str}"
        try:
            return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.datetime.max

    # Generate Overview Table
    trip_headers = ["Field", "Value"]
    trip_rows = []
    
    location_val = output.get('location', "")
    destination_val = output.get('destination', "")
    start_date_val = output.get('start_date', "")
    end_date_val = output.get('end_date', "")
    
    if isinstance(start_date_val, datetime.date):
        start_date_val = start_date_val.isoformat()
    if isinstance(end_date_val, datetime.date):
        end_date_val = end_date_val.isoformat()
        
    budget_val = output.get('budget', "")
    adults_val = output.get('num_adults', "")
    children_val = output.get('num_children', "")
    
    trip_rows.extend([
        ["Location", location_val],
        ["Destination", destination_val],
        ["Start Date", start_date_val],
        ["End Date", end_date_val],
        ["Budget", budget_val],
        ["Adults", adults_val],
        ["Children", children_val]
    ])
    
    overview_table = ascii_table(trip_headers, trip_rows, title="TRIP OVERVIEW")

    # Generate Flights Table
    flights_table = ""
    if 'flights' in output and output['flights']:
        is_new_node = isinstance(output['flights'], list) and len(output['flights']) > 0 and 'departure flights' in output['flights'][0]
        max_flights_per_class = 10
        
        if is_new_node:
            flight_tables = []
            for flight_set in output['flights']:
                if 'departure flights' in flight_set:
                    flight_tables.append(
                        format_flight_table("DEPARTURE FLIGHTS", flight_set['departure flights'], ascii_table)
                    )
                if 'arrival flights' in flight_set:
                    flight_tables.append(
                        format_flight_table("ARRIVAL FLIGHTS", flight_set['arrival flights'], ascii_table)
                    )
            flights_table = "\n\n".join([t for t in flight_tables if t])
        else:
            # Handle old node structure (code remains the same, just return string instead of printing)
            flight_tables = []
            for idx, flight_set in enumerate(output['flights']):
                flight_tables.append(f"Flight Option #{idx+1}")
                for tclass in ["Economy", "Premium Economy", "Business", "First"]:
                    if tclass not in flight_set:
                        continue
                    class_data = flight_set[tclass]
                    best = class_data.get('best_flights', [])
                    other = class_data.get('other_flights', [])
                    relevant_flights = best if best else other
                    if not relevant_flights:
                        continue
                    relevant_flights.sort(key=lambda f: f.get('price', 9999999))
                    relevant_flights = relevant_flights[:5]
                    rows = []
                    for i, fdata in enumerate(relevant_flights, start=1):
                        airlines_str = ", ".join(fdata.get('airlines', []))
                        price_str = f"${fdata.get('price','')}"
                        route_str = f"{fdata.get('departure_airport','')} -> {fdata.get('arrival_airport','')}"
                        times_str = f"{fdata.get('departure_time','')} -> {fdata.get('arrival_time','')}"
                        duration_str = format_duration(fdata.get('total_duration', ''))
                        layovers = fdata.get('layovers', [])
                        layover_count = len(layovers)
                        token = fdata.get('booking_token', None)
                        booking_str = embed_link("Book Here", f"{token}") if token else "N/A"
                        
                        rows.append([
                            str(i), airlines_str, price_str, route_str, times_str,
                            duration_str, str(layover_count), tclass, booking_str
                        ])
                        
                    headers = ["#", "Airlines", "Price", "Route", "Times", "Duration", "Layovers", "Class", "Booking"]
                    flight_tables.append(ascii_table(headers, rows, title=f"--- {tclass.upper()} ---"))
            flights_table = "\n\n".join(flight_tables)

    # Generate Accommodations Table
    accommodations_table = ""
    if 'accommodation' in output and output['accommodation']:
        accommodations = sorted(output['accommodation'], 
                              key=lambda x: extract_numeric_price(x.get('price')))[:12]
        rows = []
        for i, ac in enumerate(accommodations, start=1):
            name = ac.get('name', '')
            price = ac.get('price', '')
            rating = ac.get('rating', '')
            link = ac.get('link', None)
            link_str = embed_link("Click Here", link) if link else "N/A"
            rows.append([str(i), name, price, rating, link_str])
        
        headers = ["#", "Name", "Price", "Rating", "Booking Link"]
        accommodations_table = ascii_table(headers, rows, title="ACCOMMODATION OPTIONS")

    # Generate Activities Table
    activities_table = ""
    if 'activities' in output and output['activities']:
        rows = []
        for i, act in enumerate(output['activities'], start=1):
            name = act.get('name', '')
            address = act.get('address', '')
            description = act.get('description', '')
            address_or_desc = address if address else description
            rows.append([str(i), name, address_or_desc])
            
        headers = ["#", "Activity Name", "Address/Description"]
        activities_table = ascii_table(headers, rows, title="THINGS TO DO")

    # Generate Events Table
    events_table = ""
    if 'live_events' in output and output['live_events']:
        live_events = sorted(output['live_events'], key=parse_event_datetime)
        
        def truncate_event_name(name, word_limit=7):
            words = name.split()
            if len(words) > word_limit:
                return " ".join(words[:word_limit]) + "..."
            return name
            
        rows = []
        for i, evt in enumerate(live_events, start=1):
            event_name = evt.get('Event', '')
            truncated_event_name = truncate_event_name(event_name)
            date = evt.get('Date', '')
            time = evt.get('Time', '')
            venue = evt.get('Venue', '')
            url = evt.get('Url', None)
            link_str = embed_link("View Event", url) if url else "N/A"
            rows.append([str(i), truncated_event_name, date, time, venue, link_str])
            
        headers = ["#", "Event", "Date", "Time", "Venue", "Link"]
        events_table = ascii_table(headers, rows, title="UPCOMING LIVE EVENTS")

    # Generate Recommendations Table
    recommendations_table = ""
    if 'recommendations' in output and output['recommendations']:
        rows = []
        row_count = 0
        for rec_dict in output['recommendations']:
            for key, val in rec_dict.items():
                row_count += 1
                rows.append([str(row_count), str(key), str(val)])
                
        headers = ["#", "Category", "Information"]
        recommendations_table = ascii_table(headers, rows, title="ADDITIONAL RECOMMENDATIONS")

    return (
        overview_table,
        flights_table,
        accommodations_table,
        activities_table,
        events_table,
        recommendations_table
    )


def format_flight_table(title, flights, ascii_table_func):
    """Helper function to format flight tables for the new node structure"""
    if not flights:
        return ""
        
    categorized_flights = {"Economy": [], "Business": [], "First": []}
    for flight in flights:
        travel_class = flight.get('travel_class', 'Economy')
        categorized_flights.setdefault(travel_class, []).append(flight)
        
    class_tables = []
    for class_name, class_flights in categorized_flights.items():
        if class_flights:
            rows = []
            for i, flight in enumerate(class_flights[:10], start=1):
                airline = flight.get('airline', '')
                departure_time = flight.get('departure_time', '')
                arrival_time = flight.get('arrival_time', '')
                departure_airport = flight.get('departure_airport', '')
                arrival_airport = flight.get('arrival_airport', '')
                duration = flight.get('duration', '')
                stops = flight.get('stops', '')
                price = flight.get('price', '')
                booking_link = embed_link("Book", flight.get('booking_url', '')) if flight.get('booking_url') else "N/A"
                
                rows.append([
                    str(i), airline, departure_time, arrival_time,
                    f"{departure_airport} -> {arrival_airport}",
                    duration, str(stops), price, booking_link
                ])
                
            headers = ["#", "Airline", "Departure", "Arrival", "Route", "Duration", "Stops", "Price", "Booking"]
            class_tables.append(ascii_table_func(headers, rows, title=f"--- {title} ({class_name} Class) ---"))
            
    return "\n\n".join(class_tables)


