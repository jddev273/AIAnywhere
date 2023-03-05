# AIA (AI Anywhere) ChatGPT Usage Tool Main File
# Author: Johann Dowa
# Date: 2023-03-04
# Version 0.0.1
# License: MIT
"""
This program utilizes the ChatGPT to to generate responses to user input based on text in the clipboard or selected text.

This program also utilizes the PyStray library to create a system tray icon that allows the user to interact with the program. 

The program has three main functions: 
(1) to generate a response from user input, 
(2) to copy and paste the response to the clipboard, and 
(3) optionally paste the response to the active window.
(4) to provide notifications to the user regarding the status of the response generation process. 

This program can be customized through the use of command line arguments, and a settings.ini file. 
"""

# import modules
import time
import json
import configparser
import pyperclip
import requests
import pystray
import keyboard
import pyautogui
import apikeycheck
from PIL import Image
from notifypy import Notify
import logging

""" These are the global variables """
TRAY_ICON_GRAPHIC = Image.open('aianywhere.ico')
OPEN_AI_KEY = apikeycheck.perform_api_key_check()
tray_icon = None
openai_timeout = 120

def get_openai_api_key(api_key_file):
    """
    This function returns the API key from the file specified in api_key_file.  By default this file is name api_key.text and is located in the Secrets folder.
    """
    key = apikeycheck.perform_api_key_check()
    if key is None:
        logger.error("No OpenAI API key found.")
        exit()
    try:
        with open(api_key_file, 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(
            "An error occurred while reading the OpenAI API key file: %s", e)
        exit()


def stop_tray_icon():
    """
    This function stops the PyStray icon and unregisters all hotkeys
    """
    global tray_icon
    keyboard.unhook_all()
    tray_icon.stop()


def create_tray_menu():
    """
    This function creates the PyStray menu items
    """
    menu_items = (
        # create PyStray menu item to exit
        pystray.MenuItem('Exit', stop_tray_icon),
    )
    # return the menu items
    return menu_items


def create_tray_icon():
    """
    This function creates and runs the PyStray icon
    """
    global tray_icon
    tray_icon = pystray.Icon(
        title='AIAnywhere',
        icon=TRAY_ICON_GRAPHIC,
        name='AIAnywhere',
        menu=create_tray_menu()
    )
    tray_icon.run()


def get_chatgpt_response(content, api_key):
    """
    This function sends a JSON request to OpenAPI's ChatGPT API to generate a response
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": content}]
    }
    try:
        logger.info("Making API request...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            data=json.dumps(data),
            timeout=openai_timeout
        )
        response.raise_for_status()
        logger.info("API request successful.")
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred while making the API request: %s", e)
        return None
    # response contains json in this format:
    response_json = response.json()
    return response_json['choices'][0]['message']['content']


def notify_processing():
    """
    This function sends a notification to the user that their request is being processed
    """
    notification = Notify()
    notification.title = "Processing request..."
    notification.message = "Your request has been sent to the AI."
    notification.send()


def notify_processing_complete():
    """
    This function sends a notification to the user that their request has been processed
    """
    notification = Notify()
    notification.title = "Processing complete."
    notification.message = "Your request has been processed by the AI."
    notification.send()


def process_text_input(text):
    """
    This function processes the input text by sending it to the API and returns the response
    """
    if text != '' and text != ' ':
        notify_processing()
        logger.info("Processing...")
        response = get_chatgpt_response(text, OPEN_AI_KEY)
        if response is not None:
            notify_processing_complete()
            logger.info("Processing complete.")
            cleaned_text = response.strip()
            return cleaned_text
        else:
            logger.error("An error occurred while processing the request.")
    return None


def copy_text_to_clipboard(text):
    """
    This function copies the text to the clipboard and pastes it
    """
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    logger.info("Results pasted.")


def process_clipboard_text():
    """
    This function gets the highlighted text from the clipboard and passes it to process_text_input function
    """
    highlighted_text = pyperclip.paste()
    text = process_text_input(highlighted_text)
    pyperclip.copy(text)


def print_highlighted_text():
    """
    This function gets the highlighted text and passes it to process_text_input function and then pastes the response
    """
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    highlighted_text = pyperclip.paste()
    text = process_text_input(highlighted_text)
    copy_text_to_clipboard(text)


def print_text_from_clipboard():
    """
    This function gets the text from the clipboard and passes it to process_text_input function and then pastes the response
    """
    highlighted_text = pyperclip.paste()
    text = process_text_input(highlighted_text)
    copy_text_to_clipboard(text)

""" These are the main instructions """


""" This is the loading of the settings.ini file """
config = configparser.ConfigParser()
config.read('settings.ini')

""" This the setting of the global variables from the settings.ini file """
settings = config.items('Settings')
for setting, value in settings:
    if setting == 'openai_timeout':
        openai_timeout = int(value)
    else:
        continue

""" This is the loading of the hotkeys.ini file """
pyperclip.copy('')

hotkeys = config.items('Hotkeys')

for action, hotkey in hotkeys:
    if action == 'print_highlighted_text':
        callback = print_highlighted_text
    elif action == 'print_from_clipboard':
        callback = print_text_from_clipboard
    elif action == 'process_clipboard':
        callback = process_clipboard_text
    else:
        continue
    keyboard.add_hotkey(hotkey, callback)

""" This is the logger setup """
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

""" This is the creation of the PyStray icon, which will keep the program running until the user exits the program"""
create_tray_icon()
