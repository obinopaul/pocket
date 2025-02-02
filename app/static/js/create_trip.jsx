// static/js/create_trip.jsx
import React, { useState } from "react";
import GooglePlacesAutocomplete from "react-google-places-autocomplete";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";

function CreateTrip() {
  const [destination, setDestination] = useState("");
  const [dates, setDates] = useState(null);
  const [travelers, setTravelers] = useState({ adults: 1, children: 0, rooms: 1 });
  const { transcript, listening, startListening, stopListening, isSupported } = useSpeechRecognition();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleSubmit = () => {
    const tripData = {
      destination,
      dates,
      travelers,
      notes: transcript,
    };
    console.log("Trip Data:", tripData);
    setIsDialogOpen(true);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold text-center text-blue-600 mb-6">Plan Your Trip</h2>

      {/* First Row - Main Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-lg font-semibold text-gray-700">Where are you going?</label>
          <GooglePlacesAutocomplete
            apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}
            selectProps={{
              value: destination,
              onChange: setDestination,
              placeholder: "Enter a destination...",
            }}
          />
        </div>
        <div>
          <label className="block text-lg font-semibold text-gray-700">Select Dates</label>
          <Calendar
            onChange={setDates}
            selectRange={true}
            className="border rounded-md p-2 w-full"
          />
        </div>
        <div>
          <label className="block text-lg font-semibold text-gray-700">Travelers</label>
          <div className="flex gap-2">
            <Input
              type="number"
              min="1"
              value={travelers.adults}
              onChange={(e) => setTravelers({ ...travelers, adults: parseInt(e.target.value) })}
              placeholder="Adults"
              className="border rounded-md p-2 w-full"
            />
            <Input
              type="number"
              min="0"
              value={travelers.children}
              onChange={(e) => setTravelers({ ...travelers, children: parseInt(e.target.value) })}
              placeholder="Children"
              className="border rounded-md p-2 w-full"
            />
            <Input
              type="number"
              min="1"
              value={travelers.rooms}
              onChange={(e) => setTravelers({ ...travelers, rooms: parseInt(e.target.value) })}
              placeholder="Rooms"
              className="border rounded-md p-2 w-full"
            />
          </div>
        </div>
      </div>

      {/* Second Row - Microphone Input */}
      <div className="mt-6 text-center">
        <label className="block text-lg font-semibold text-gray-700">
          Tell us more about your trip
        </label>
        {isSupported ? (
          <>
            <Button
              onClick={listening ? stopListening : startListening}
              className="mt-2 px-6 py-2 bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-600"
            >
              {listening ? "Stop Recording" : "Start Recording"}
            </Button>
            <p className="mt-2 text-gray-600 italic">{transcript}</p>
          </>
        ) : (
          <p className="text-red-500 mt-2">
            Speech recognition is not supported in your browser.
          </p>
        )}
      </div>

      {/* Third Row - Submit Button */}
      <div className="mt-6 text-center">
        <Button
          onClick={handleSubmit}
          className="bg-green-500 text-white px-6 py-2 rounded-lg shadow-md hover:bg-green-600"
        >
          Submit
        </Button>
      </div>

      {/* Dialog Modal for Confirmation */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="text-center">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-gray-800">
              Trip Confirmed!
            </DialogTitle>
          </DialogHeader>
          <p className="text-gray-600">
            Your trip details have been submitted successfully.
          </p>
          <Button
            onClick={() => setIsDialogOpen(false)}
            className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg shadow-md hover:bg-blue-600"
          >
            Close
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default CreateTrip;
