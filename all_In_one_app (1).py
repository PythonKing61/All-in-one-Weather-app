import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import http.client
import json

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        
        # Time zone dictionary
        self.time_zone_offsets = {
            "pst": datetime.timedelta(hours=-8),
            "mst": datetime.timedelta(hours=-7),
            "cst": datetime.timedelta(hours=-6),
            "est": datetime.timedelta(hours=-5)
        }
        self.current_time_zone = "est"

        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Style for rounded buttons
        style = ttk.Style()
        style.configure("RoundedButton.TButton", relief="flat", 
                        borderwidth=2, padding=10, 
                        background="#e1e1e1", foreground="black", 
                        font=("Helvetica", 10), 
                        focuscolor="none")
        style.map("RoundedButton.TButton",
                  background=[("active", "#a6a6a6")])

        # ZIP code input
        self.zip_label = ttk.Label(self.root, text="Enter ZIP code:")
        self.zip_label.pack(pady=5)
        self.zip_entry = ttk.Entry(self.root)
        self.zip_entry.pack(pady=5)

        # Buttons
        self.weather_button = ttk.Button(self.root, text="Get Weather", 
                                         command=self.show_weather, 
                                         style="RoundedButton.TButton")
        self.weather_button.pack(pady=5)
        
        self.date_button = ttk.Button(self.root, text="Get Date", 
                                      command=self.show_date, 
                                      style="RoundedButton.TButton")
        self.date_button.pack(pady=5)
        
        self.time_button = ttk.Button(self.root, text="Get Time", 
                                      command=self.show_time, 
                                      style="RoundedButton.TButton")
        self.time_button.pack(pady=5)
        
        self.timezone_button = ttk.Button(self.root, text="Change Timezone", 
                                          command=self.open_timezone_window, 
                                          style="RoundedButton.TButton")
        self.timezone_button.pack(pady=5)
        
        # Output display
        self.output_label = ttk.Label(self.root, text="", wraplength=300)
        self.output_label.pack(pady=10)

    def get_lat_long(self, zip_code):
        conn = http.client.HTTPSConnection("api.zippopotam.us")
        endpoint = f"/us/{zip_code}"
        conn.request("GET", endpoint)
        response = conn.getresponse()
        if response.status == 200:
            data = response.read()
            zip_data = json.loads(data)
            latitude = zip_data['places'][0]['latitude']
            longitude = zip_data['places'][0]['longitude']
            return latitude, longitude
        else:
            messagebox.showerror("Error", f"Error: {response.status} - {response.reason}")
            return None, None

    def get_forecast_url(self, latitude, longitude):
        conn = http.client.HTTPSConnection("api.weather.gov")
        endpoint = f"/points/{latitude},{longitude}"
        headers = {"User-Agent": "MyWeatherApp (example@example.com)"}
        conn.request("GET", endpoint, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            data = response.read()
            grid_data = json.loads(data)
            forecast_url = grid_data['properties'].get('forecast')
            return forecast_url
        else:
            messagebox.showerror("Error", f"Error: {response.status} - {response.reason}")
            return None

    def get_weather(self, forecast_url):
        conn = http.client.HTTPSConnection("api.weather.gov")
        endpoint = forecast_url.replace("https://api.weather.gov", "")
        headers = {"User-Agent": "MyWeatherApp (example@example.com)"}
        conn.request("GET", endpoint, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            data = response.read()
            weather_data = json.loads(data)
            period = weather_data['properties']['periods'][0]
            temperature = period['temperature']
            description = period['shortForecast']
            return f"Weather: {temperature}°F and {description}"
        else:
            return f"Error: {response.status} - {response.reason}"

    def get_current_time_and_date(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        adjusted_time = now + self.time_zone_offsets[self.current_time_zone.lower()]
        return adjusted_time.strftime("%m/%d/%y %I:%M %p")

    def show_weather(self):
        zip_code = self.zip_entry.get()
        latitude, longitude = self.get_lat_long(zip_code)
        if latitude and longitude:
            forecast_url = self.get_forecast_url(latitude, longitude)
            if forecast_url:
                weather = self.get_weather(forecast_url)
                self.output_label.config(text=weather)
            else:
                self.output_label.config(text="Unable to retrieve forecast URL")
        else:
            self.output_label.config(text="Invalid ZIP code")

    def show_date(self):
        current_date = self.get_current_time_and_date()
        self.output_label.config(text=f"Date: {current_date}")

    def show_time(self):
        current_time = self.get_current_time_and_date()
        self.output_label.config(text=f"Time: {current_time}")

    def open_timezone_window(self):
        self.timezone_window = tk.Toplevel(self.root)
        self.timezone_window.title("Change Timezone")

        self.new_tz_label = ttk.Label(self.timezone_window, text="Enter the new time zone (PST, MST, CST, EST):")
        self.new_tz_label.pack(pady=5)

        self.new_tz_entry = ttk.Entry(self.timezone_window)
        self.new_tz_entry.pack(pady=5)

        self.set_tz_button = ttk.Button(self.timezone_window, text="Set Timezone", 
                                        command=self.change_timezone, 
                                        style="RoundedButton.TButton")
        self.set_tz_button.pack(pady=5)
    
    def change_timezone(self):
        new_time_zone = self.new_tz_entry.get().lower()
        if new_time_zone in self.time_zone_offsets:
            self.current_time_zone = new_time_zone
            self.output_label.config(text=f"Time zone successfully changed to {new_time_zone.upper()}")
            self.timezone_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid time zone entered. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
