import speech_recognition as sr
import pyttsx3
import random
import sqlite3
from datetime import datetime

# Initialize pyttsx3 (text-to-speech engine)
engine = pyttsx3.init()

# Initialize SpeechRecognition
recognizer = sr.Recognizer()

# Initialize SQLite database
conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()

# Create a table for reservations
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY,
        name TEXT,
        time TEXT,
        table_number INTEGER
    )
''')

# Create a table for kitchen orders
cursor.execute('''
    CREATE TABLE IF NOT EXISTS kitchen_orders (
        id INTEGER PRIMARY KEY,
        item_name TEXT,
        modifications TEXT,
        order_time TEXT,
        status TEXT
    )
''')
conn.commit()

# Define Indian restaurant menu
menu = {
    'veg': [
        {'name': 'Paneer Butter Masala', 'description': 'Rich tomato-based gravy with paneer.', 'price': 250},
        {'name': 'Dal Makhani', 'description': 'Slow-cooked black lentils in butter and cream.', 'price': 220},
        {'name': 'Aloo Paratha', 'description': 'Stuffed wheat flatbread with spiced potatoes.', 'price': 100},
        {'name': 'Chole Bhature', 'description': 'Spicy chickpea curry with deep-fried bread.', 'price': 150},
        {'name': 'Masala Dosa', 'description': 'Crispy rice crepe filled with spiced potatoes.', 'price': 120}
    ],
    'non-veg': [
        {'name': 'Butter Chicken', 'description': 'Chicken cooked in creamy tomato gravy.', 'price': 300},
        {'name': 'Mutton Rogan Josh', 'description': 'Spicy mutton curry with Kashmiri flavors.', 'price': 350},
        {'name': 'Chicken Biryani', 'description': 'Fragrant basmati rice cooked with spiced chicken.', 'price': 280},
        {'name': 'Prawn Curry', 'description': 'Juicy prawns in coconut-based curry.', 'price': 320},
        {'name': 'Fish Fry', 'description': 'Crispy fried fish with spices.', 'price': 250}
    ],
    'drinks': [
        {'name': 'Masala Chai', 'description': 'Traditional Indian spiced tea.', 'price': 50},
        {'name': 'Lassi', 'description': 'Sweet or salted yogurt-based drink.', 'price': 70},
        {'name': 'Filter Coffee', 'description': 'South Indian strong coffee.', 'price': 60}
    ],
    'desserts': [
        {'name': 'Gulab Jamun', 'description': 'Deep-fried milk dumplings in sugar syrup.', 'price': 80},
        {'name': 'Rasgulla', 'description': 'Spongy cottage cheese balls in syrup.', 'price': 90},
        {'name': 'Kheer', 'description': 'Sweet rice pudding with saffron and nuts.', 'price': 100}
    ]
}

# Function to speak the text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to take user input via speech
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand. Please try again.")
            return None
        except sr.RequestError:
            speak("Sorry, there is an issue with the speech recognition service.")
            return None

# Function to ask for dietary preferences
def ask_for_dietary_preferences():
    speak("Would you like vegetarian or non-vegetarian dishes?")
    preference = listen()
    if preference in ['vegetarian', 'veg']:
        return 'veg'
    elif preference in ['non vegetarian', 'non veg']:
        return 'non-veg'
    else:
        speak("I didn't understand. Please say veg or non-veg.")
        return ask_for_dietary_preferences()

# Function to show the menu
def show_menu():
    category = ask_for_dietary_preferences()
    speak(f"Here are the {category} items available:")
    for item in menu[category]:
        print(f"{item['name']} - {item['description']} - ₹{item['price']}")
        speak(f"{item['name']} - {item['description']} - Price: {item['price']} rupees")
    speak("Would you like to place an order?")

# Function to ask for modifications based on dish type
def ask_for_modifications(item_name):
    if 'biryani' in item_name.lower():
        speak("Would you like extra spice or less spice?")
    elif 'dosa' in item_name.lower():
        speak("Do you want extra crispy or soft dosa?")
    elif 'paratha' in item_name.lower():
        speak("Would you like extra butter or plain?")
    else:
        speak("Any modifications to your order?")
    modifications = listen()
    return modifications if modifications else "No modifications"

# Function to send the order to the kitchen
def send_order_to_kitchen(item_name, modifications):
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO kitchen_orders (item_name, modifications, order_time, status) VALUES (?, ?, ?, ?)",
                   (item_name, modifications, order_time, "Pending"))
    conn.commit()
    speak(f"Your order for {item_name} has been sent to the kitchen.")

# Function to estimate waiting time
def estimate_waiting_time():
    waiting_time = random.randint(10, 30)
    speak(f"Your order will be ready in approximately {waiting_time} minutes.")

# Function to take and place the order
def place_order():
    speak("What would you like to order?")
    command = listen()
    if command:
        for category in menu.values():
            for item in category:
                if item['name'].lower() in command:
                    speak(f"Your order for {item['name']} has been placed.")
                    order_number = random.randint(1000, 9999)
                    speak(f"Your order number is {order_number}.")

                    # Ask for modifications
                    modifications = ask_for_modifications(item['name'])

                    # Send order to the kitchen
                    send_order_to_kitchen(item['name'], modifications)

                    # Estimate waiting time
                    estimate_waiting_time()

                    return order_number
        speak("Sorry, I didn't understand the order. Could you please repeat it?")

# Main function
def main():
    speak("Hello, welcome to our Indian restaurant! How may I assist you today?")
    print("You can say 'order', 'menu', or 'reservation'.")

    while True:
        command = listen()
        if command:
            if 'order' in command:
                place_order()
            elif 'menu' in command:
                show_menu()
            elif 'reservation' in command:
                speak("Reservation feature coming soon!")
            elif 'exit' in command or 'quit' in command:
                speak("Goodbye! Have a great day!")
                break
            else:
                speak("Sorry, I didn't understand. You can say 'order', 'menu', or 'exit'.")

# Run the assistant
if __name__ == "__main__":
    main()
