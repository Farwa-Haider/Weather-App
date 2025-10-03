import os
import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO

API_Key = "f9ef058b309c937236e748696c32ee99"

def get_weather_from_api(city):
    if not city:
        return "Please enter a city name"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_Key}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if r.status_code != 200:
            return f"Error: {data.get('message', 'Could not get data')}"
        name = data.get("name",city).title()
        temp = data.get("main", {}).get("temp")
        w = data.get("weather", [{}])[0]
        desc = w.get("description","")
        main = w.get("main", "")
        return {"name": name, "temp": temp, "desc": desc.capitalize(), "main": main}
    except requests.RequestException:
        return "Network Error. Try Again"

def on_get_click():
    city = city_entry.get().strip()
    result = get_weather_from_api(city)
    if isinstance(result, str):
        result_label.config(text=result, font=("Arial", 14, "bold"))
        temp_label.config(text="")
        desc_label.config(text="")
        result_label.pack_configure(pady=5)
        temp_label.pack_configure(pady=5)
        desc_label.pack_configure(pady=5)
        return

    name = result.get("name", "")
    temp = result.get("temp")
    desc = result.get("desc", "")
    main_cond = result.get("main", "")

    global last_condition
    last_condition = main_cond
    
    set_background_for_condition(main_cond)

    result_label.config(text=name, font=("Arial", 20, "bold"))

    result_label.pack_configure(pady=(10, 25)) 

    temp_text = f"{round(temp)}°C" if temp is not None else "--"
    temp_label.config(text=temp_text, font=("Arial", 42, "bold"))
    temp_label.pack_configure(pady=(0, 25)) 

    desc_label.config(text=desc, font=("Arial", 20))
    desc_label.pack_configure(pady=(0, 10))

def set_background_for_condition(condition):
    mapping = {
        "Clear": "bg_clear.jpg",
        "Clouds": "bg_clouds.jpg",
        "Rain": "bg_rain.jpg",
        "Drizzle": "bg_rain.jpg",
        "Thunderstorm": "bg_rain.jpg",
        "Snow": "bg_snow.jpg",
        "Mist": "bg_fog.jpg",
        "Fog": "bg_fog.jpg",
        "Haze": "bg_fog.jpg"
    }
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, "images")   # use lowercase 'images' folder
    filename = mapping.get(condition, "bg_default.jpg")
    fn = os.path.join(images_dir, filename)

    try:
        root.update_idletasks()                 # make sure geometry info is current
        w = root.winfo_width() or root.winfo_screenwidth() or 800
        h = root.winfo_height() or root.winfo_screenheight() or 600

        img = Image.open(fn)
        img = img.resize((w, h), Image.LANCZOS)  # resize to current window size
        bg_photo = ImageTk.PhotoImage(img)

        background_label.config(image=bg_photo)
        background_label.image = bg_photo         # keep reference so GC won't remove it

    except Exception as e:
        # debugging info printed to console
        print("Failed to load background:", fn)
        print("Error:", repr(e))
        # fallback: remove image and set plain background color
        try:
            background_label.config(image="")
            background_label.image = None
            root.config(bg="#ffffff")
        except Exception:
            pass

root = tk.Tk()
root.title("Weather App")
root.geometry("450x450")

background_label = tk.Label(root)
background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

tk.Label(root, text="City:",  font=("Arial", 14)).pack(padx=18, pady=6, anchor="w")

city_entry = tk.Entry(root, width=30)
city_entry.pack(padx=8)

get_btn = tk.Button(root, text="Get Weather", command=on_get_click)
get_btn.pack(pady=6)

result_label = tk.Label(root, text="Type a city and click Get Weather", justify="left", font=("Arial", 14))
result_label.pack(padx=8, pady=5)

temp_label = tk.Label(root, text="", font=("Arial", 28, "bold"), fg="blue")
temp_label.pack(pady=5)

desc_label = tk.Label(root, text="", font=("Arial", 14))
desc_label.pack(pady=5)

BASE_WIDTH = 450
BASE_HEIGHT = 450

def apply_scaled_fonts(scale):
    city_font = ("Arial", max(10, int(20 * scale)), "bold") 
    temp_font = ("Arial", max(12, int(42 * scale)), "bold")
    desc_font = ("Arial", max(9, int(20 * scale)))            
    entry_font = ("Arial", max(8, int(12 * scale)))
    btn_font = ("Arial", max(8, int(12 * scale)), "bold")
    result_label.config(font=city_font)
    temp_label.config(font=temp_font)
    desc_label.config(font=desc_font)
    city_entry.config(font=entry_font)
    get_btn.config(font=btn_font)

_resize_after_id = None
def on_resize(event=None):
    global _resize_after_id
    if _resize_after_id:
        root.after_cancel(_resize_after_id)
    _resize_after_id = root.after(100, do_resize_work)

def do_resize_work():
    w = root.winfo_width() or BASE_WIDTH
    h = root.winfo_height() or BASE_HEIGHT
    scale_w = w / BASE_WIDTH
    scale_h = h / BASE_HEIGHT
    scale = min(scale_w, scale_h)

    try:
        set_background_for_condition(last_condition if 'last_condition' in globals() else "")
    except Exception:
        set_background_for_condition("")

    apply_scaled_fonts(scale)

set_background_for_condition("")  

root.bind("<Configure>", on_resize)

do_resize_work()

root.mainloop()

