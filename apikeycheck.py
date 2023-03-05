# AIA (AI Anywhere) ChatGPT Usage Tool Api Key Check File
# Author: Johann Dowa
# Date: 2023-03-04
# Version 0.0.1
# License: MIT

# Ask user to enter key if it is not found
""" This Python script defines three functions that are used for reading, prompting, and validating an OpenAI API key. The read_api_key function reads the API key from a text file, while the prompt_for_api_key function prompts the user to input an API key through a PySimpleGUI window. The perform_api_key_check function calls the read and prompt functions to ensure that a valid API key is obtained before continuing with other program logic. """

import os
import re
import PySimpleGUI as sg


def read_api_key():
    """
    Check if the API key file exists.
    If the file exists, read the API key and strip any whitespace.
    If the API key is not in the correct format, set it to None.
    If the file does not exist, set the API key to None.
    """
    if os.path.exists("Secrets/api_key.txt"):
        with open("Secrets/api_key.txt", "r") as f:
            api_key = f.read().strip()
            if not re.match("^sk-[a-zA-Z0-9\-]+$", api_key):
                api_key = None
    else:
        api_key = None
    return api_key


def prompt_for_api_key():
    """
    Set PySimpleGUI theme.
    Create PySimpleGUI layout for getting API key input.
    Loop until a valid API key has been obtained or the window is closed.
    If the window is closed, display error and set API key to None.
    If API key is not valid, display error and prompt user again.
    If API key is valid, save it to text file and exit loop.
    Close PySimpleGUI window and return API key.
    """
    sg.theme("DefaultNoMoreNagging")
    layout = [
        [sg.Text("Please enter your OpenAI API key:")],
        [sg.Input(key="api_key")],
        [sg.Button("OK")],
    ]
    window = sg.Window("Enter API Key", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            sg.popup("Sorry, an API key is required.")
            api_key = None
            break
        elif event == "OK":
            api_key = values["api_key"]
            if not re.match("^sk-[a-zA-Z0-9\-]+$", api_key):
                api_key = None
            if api_key is not None:
                with open("Secrets/api_key.txt", "w") as f:
                    f.write(api_key)
                break
            else:
                sg.popup(
                    "Invalid API key. Please enter a valid API key in the format sk-<character string>."
                )
    window.close()
    return api_key


def perform_api_key_check():
    """
    Get API key from file or prompt user for input.
    """
    api_key = read_api_key()
    if api_key is None:
        api_key = prompt_for_api_key()
    return api_key