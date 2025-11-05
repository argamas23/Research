
import os
import spacy
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Set correct file path
input_text_file = "/home/samagra/Desktop/Research/corpus/Simla_1910.txt"

# Check if file exists
if not os.path.exists(input_text_file):
    print(f"Error: File '{input_text_file}' not found. Check the path and try again.")
    exit(1)

# Load SpaCy model and increase max_length
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 2_000_000  # Allow processing of large texts

# Function to extract place names in chunks
def extract_places(text, chunk_size=100_000):
    places = set()
    for i in range(0, len(text), chunk_size):
        doc = nlp(text[i:i+chunk_size])  # Process smaller chunks
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Extract only place names
                places.add(ent.text)
    return list(places)

# Function to get coordinates using Geopy
def get_coordinates(place_names):
    geolocator = Nominatim(user_agent="geo_locator")
    coordinates = {}

    for place in place_names:
        try:
            location = geolocator.geocode(place, timeout=10)
            if location:
                coordinates[place] = (location.latitude, location.longitude)
        except GeocoderTimedOut:
            print(f"Timeout for {place}")
    
    return coordinates

# Function to save coordinates to a CSV file
def save_to_csv(coordinates, filename="places_coordinates.csv"):
    df = pd.DataFrame(coordinates.items(), columns=["Place", "Coordinates"])
    df[["Latitude", "Longitude"]] = df["Coordinates"].apply(pd.Series)
    df.drop(columns=["Coordinates"], inplace=True)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")

# Function to plot places on a map using Folium
def plot_places_on_map(coordinates, map_filename="places_map.html"):
    if not coordinates:
        print("No coordinates to plot.")
        return
    
    # Compute average location for centering the map
    avg_lat = sum(lat for lat, lon in coordinates.values()) / len(coordinates)
    avg_lon = sum(lon for lat, lon in coordinates.values()) / len(coordinates)
    place_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)

    # Add markers for each place
    for place, (lat, lon) in coordinates.items():
        folium.Marker([lat, lon], popup=place).add_to(place_map)

    place_map.save(map_filename)
    print(f"Map saved as {map_filename}")

# Main Execution
if __name__ == "__main__":
    # Load text in chunks
    with open(input_text_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Extract places
    place_names = extract_places(text)
    print(f"Extracted Places: {place_names}")

    # Get coordinates
    place_coordinates = get_coordinates(place_names)
    print(f"Coordinates: {place_coordinates}")

    # Save to CSV
    save_to_csv(place_coordinates)

    # Plot on map
    plot_places_on_map(place_coordinates)
