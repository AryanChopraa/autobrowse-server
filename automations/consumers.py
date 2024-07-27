import re
import time
import aiohttp
import json
import base64
from os import getenv, path
import os
import asyncio
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
from channels.generic.websocket import AsyncWebsocketConsumer
from automations.config.prompts import SYSTEM_PROMPT
from automations.config.scripts import HIGHLIGHT_LINKS_SCRIPT
from automations.config.tools import TOOLS

load_dotenv()

GPT_MODEL = "gpt-4o"

client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

def initialize_driver():
    print("Initializing driver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--window-size=1440,900')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("Driver initialized successfully")
    return driver

def highlight_links(driver):
    print("Highlighting links and taking screenshot...")
    try:
        driver.execute_script(HIGHLIGHT_LINKS_SCRIPT)
        screenshot = driver.get_screenshot_as_png()
        encoded_screenshot = base64.b64encode(screenshot).decode('utf-8')
        print("Screenshot taken and encoded successfully")
        return encoded_screenshot
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    print("Sending chat completion request...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        print("Chat completion request successful")
        return response
    except Exception as e:
        print(f"Error in chat completion request: {e}")
        return e

def preprocess_text(text):
    print(f"Preprocessing text: {text}")
    processed = re.sub(r'[^\w\s]', '', text).lower()
    print(f"Preprocessed text: {processed}")
    return processed

def handle_url(driver, url):
    print(f"Handling URL: {url}")
    driver.get(url)
    return highlight_links(driver)

def handle_search(driver, query):
    print(f"Handling search query: {query}")
    driver.get(f"https://www.google.com/search?q={query}")
    return highlight_links(driver)

def handle_click(driver, link_text):
    print(f"Handling click on link text: {link_text}")
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, '[gpt-link-text]')
        partial = next((e for e in elements if preprocess_text(link_text) in preprocess_text(e.get_attribute('gpt-link-text'))), None)
        exact = next((e for e in elements if preprocess_text(e.get_attribute('gpt-link-text')) == preprocess_text(link_text)), None)
                    
        if exact:
            print("Clicking on exact match")
            exact.click()
        elif partial:
            print("Clicking on partial match")
            partial.click()
        else:
            raise Exception("Can't find link")
    except Exception as e:
        print(f"Error clicking link: {e}")
    finally:
        asyncio.sleep(5)
    return highlight_links(driver)

def handle_scroll(driver):
    print("Handling scroll")
    try:
        viewport_height = driver.execute_script("return window.innerHeight")
        driver.execute_script(f"window.scrollBy(0, {viewport_height});")
        asyncio.sleep(1)
        print("Scroll successful")
    except Exception as e:
        print(f"Error scrolling: {e}")
    return highlight_links(driver)

def handle_typing(driver, placeholder_value, text):
    print(f"Handling typing: placeholder='{placeholder_value}', text='{text}'")
    elements = driver.find_elements(By.CSS_SELECTOR, f'input[placeholder="{placeholder_value}"]')
    if elements:
        element = elements[0]
        element.clear()
        element.send_keys(text)
        element.send_keys(Keys.RETURN)
        print("Typing successful")
    else:
        print(f"No input element found with placeholder '{placeholder_value}'")
    return highlight_links(driver)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connection established")
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected to WebSocket"}))

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")
        if hasattr(self, 'driver'):
            await asyncio.to_thread(self.driver.quit)
            print("Driver quit successfully")

    async def receive(self, text_data):
        print(f"Received data: {text_data}")
        text_data_json = json.loads(text_data)
        if 'objective' in text_data_json:
            objective = text_data_json['objective']
            print(f"Starting main loop with objective: {objective}")
            await self.main_loop(objective)
        else:
            message = text_data_json['message']
            print(f"Received message: {message}")

    async def send_screenshots(self):
        print("Starting screenshot sending loop")
        while True:
            await asyncio.sleep(1)  
            base64img = await asyncio.to_thread(highlight_links, self.driver)
            
            if base64img:
                print("Sending screenshot")
                await self.send(text_data=json.dumps({"screenshot": base64img}))

    async def main_loop(self, objective):
        print("Initializing driver for main loop")
        self.driver = await asyncio.to_thread(initialize_driver)
        
        print("Loading blank page")
        await asyncio.to_thread(self.driver.get, "about:blank")
        
        screenshot_task = asyncio.create_task(self.send_screenshots())
            
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{objective}"}
        ]

        while True:
            print("Sending chat completion request")
            chat_response = await asyncio.to_thread(chat_completion_request, messages, tools=TOOLS)
            response = chat_response.choices[0].message
            print(f"Received response: {response.content}")
            await self.send(text_data=json.dumps({"response": response.content}))

            if response.tool_calls:
                tool_call = response.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                    
                explanation = arguments.get('explanation', '')
                action = arguments.get('action', '')
                    
                print(f"Executing tool call: {function_name}")
                print(f"Explanation: {explanation}")
                print(f"Action: {action}")

                await self.send(text_data=json.dumps({
                    "explanation": explanation,
                    "action": action
                }))

                if function_name == "handle_url":
                    base64img = await asyncio.to_thread(handle_url, self.driver, arguments['url'])
                elif function_name == "handle_search":
                    base64img = await asyncio.to_thread(handle_search, self.driver, arguments['query'])
                elif function_name == "handle_click":
                    base64img = await asyncio.to_thread(handle_click, self.driver, arguments['text'])
                elif function_name == "handle_scroll":
                    base64img = await asyncio.to_thread(handle_scroll, self.driver)
                elif function_name == "handle_typing":
                    base64img = await asyncio.to_thread(handle_typing, self.driver, arguments['placeholder_value'], arguments['text'])

                print("Adding screenshot to messages")
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Here is the screenshot of the current page after executing: {function_name}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64img}"}}
                    ]
                })
            else:
                print("No tool calls, sending final response")
                final_response = {"final_response": response.content}
                await self.send(text_data=json.dumps(final_response))
                break

        print("Cancelling screenshot task")
        screenshot_task.cancel() 
        print("Quitting driver")
        await asyncio.to_thread(self.driver.quit)