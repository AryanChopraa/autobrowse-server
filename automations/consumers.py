import re
import time
import json
import base64
import os
import asyncio
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from openai import OpenAI
from channels.generic.websocket import AsyncWebsocketConsumer

load_dotenv()

GPT_MODEL = "gpt-4o"
SCREENSHOT_PATH = './screenshot.png'

client = OpenAI(api_key="sk-proj-V9xPa2nvdJ4DFj4c4bLdT3BlbkFJy7dcTnyIoaZdlqcJNF0R")

tools = [
    {
        "type": "function",
        "function": {
            "name": "executeAction",
            "description": "Execute a browser action such as opening a URL, performing a Google search, or clicking an element.",
            "parameters": {
                "type": "object",
                "properties": {
                    "actionType": {
                        "type": "string",
                        "enum": ["url", "search", "click"],
                        "description": "The type of action to perform. Must be one of 'url', 'search', or 'click'."
                    },
                    "action": {
                        "type": "string",
                        "description": "The specific action to perform based on the actionType. For 'url', provide the URL to navigate to. For 'search', provide the search term. For 'click', provide the text of the link to click."
                    },
                    "driver": {
                        "type": "object",
                        "description": "The Selenium WebDriver instance used to perform the browser actions."
                    }
                },
                "required": ["actionType", "action", "driver"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getting_instructions_tool",
            "description": "Generate a series of browser actions based on a given query, such as searching the web, logging into a website, or creating a Doc and many more",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The task to be performed, like searching for a term, logging into a website, or creating a document."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_typing",
            "description": "Locate input elements with a specified placeholder value and enter the given text into the first found element.",
            "parameters": {
                "type": "object",
                "properties": {
                    "placeholder_value": {
                        "type": "string",
                        "description": "The placeholder value of the input element to be located."
                    },
                    "text": {
                        "type": "string",
                        "description": "The text to enter into the located input element. for searching or inputing some value"
                    },
                },
                "required": ["placeholder_value", "text", "driver"]
            }
        }
    }
]

class AgentMemory:
    def __init__(self):
        self.data = {}

    def add(self, key, value):
        if key in self.data:
            if isinstance(self.data[key], list):
                self.data[key].append(value)
                print(self.data[key])
            else:
                self.data[key] = [self.data[key], value]
                print(self.data[key])
        else:
            self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def clear(self):
        self.data.clear()

    def to_dict(self):
        return self.data

# def initialize_driver():
#     service = Service('./agentComponents/driver/chromedriver')
#     return webdriver.Chrome(service=service)

def initialize_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    return webdriver.Chrome(service=service, options=options)

def highlight_links(driver):
    script = """
    (function() {
        // Remove existing gpt-link-text attributes
        document.querySelectorAll('[gpt-link-text]').forEach(e => {
            e.removeAttribute("gpt-link-text");
        });

        // Select all elements that can be clickable
        const elements = document.querySelectorAll(
            "a, button, input, textarea, [role=button], [role=treeitem]"
        );

        elements.forEach(e => {
            function isElementVisible(el) {
                if (!el) return false; // Element does not exist

                function isStyleVisible(el) {
                    const style = window.getComputedStyle(el);
                    return style.width !== '0' &&
                        style.height !== '0' &&
                        style.opacity !== '0' &&
                        style.display !== 'none' &&
                        style.visibility !== 'hidden';
                }

                function isElementInViewport(el) {
                    const rect = el.getBoundingClientRect();
                    return (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                }

                // Check if the element is visible style-wise
                if (!isStyleVisible(el)) {
                    return false;
                }

                // Traverse up the DOM and check if any ancestor element is hidden
                let parent = el;
                while (parent) {
                    if (!isStyleVisible(parent)) {
                        return false;
                    }
                    parent = parent.parentElement;
                }

                // Finally, check if the element is within the viewport
                return isElementInViewport(el);
            }

            // Add red border to the element
            e.style.border = "1px solid red";

            const position = e.getBoundingClientRect();

            if (position.width > 5 && position.height > 5 && isElementVisible(e)) {
                const link_text = e.textContent.replace(/[^a-zA-Z0-9 ]/g, '');
                e.setAttribute("gpt-link-text", link_text);
            }
        });
    })();
    """
    try:
        driver.execute_script(script)
        driver.save_screenshot(SCREENSHOT_PATH)
    except Exception:
        pass

def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
    except Exception as e:
        return e

def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text).lower()

def getting_instructions_tool(query):
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant..."},
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

def handle_typing(driver, placeholder_value, text):
    elements = driver.find_elements(By.CSS_SELECTOR, f'input[placeholder="{placeholder_value}"]')
    if elements:
        element = elements[0]
        element.clear()
        element.send_keys(text)
        element.send_keys(Keys.RETURN)
        highlight_links(driver)

def scroll_page(driver):
    try:
        viewport_height = driver.execute_script("return window.innerHeight")
        driver.execute_script(f"window.scrollBy(0, {viewport_height});")
        time.sleep(1)
        highlight_links(driver)
    except Exception:
        pass

def execute_action(driver, action_type, action):
    actions = {
        "url": lambda url: driver.get(url),
        "search": lambda term: driver.get(f"https://www.google.com/search?q={term}"),
        "click": lambda text: click_element(driver, text),
        "scroll": lambda _: scroll_page(driver)
    }
    
    if action_type in actions:
        actions[action_type](action)
        highlight_links(driver)

def click_element(driver, link_text):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, '[gpt-link-text]')
        partial = next((e for e in elements if preprocess_text(link_text) in preprocess_text(e.get_attribute('gpt-link-text'))), None)
        exact = next((e for e in elements if preprocess_text(e.get_attribute('gpt-link-text')) == preprocess_text(link_text)), None)
        
        if exact:
            exact.click()
        elif partial:
            partial.click()
        else:
            raise Exception("Can't find link")
    except Exception:
        pass
    finally:
        time.sleep(5)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected to WebSocket"}))
        # await self.main_loop()

    async def disconnect(self, close_code):
        # Cleanup code here (e.g., closing the driver)
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'objective' in text_data_json:
            objective = text_data_json['objective']
            await self.main_loop(objective)
                    
        else:
            message = text_data_json['message']
            print(message)
       
        
   
        # Handle incoming messages from frontend
        # You might want to add logic here to control the main loop

    async def main_loop(self,objective):
        driver = await asyncio.to_thread(initialize_driver)
        memory = AgentMemory()
        
        system_prompt = """
        You are a website crawler with memory capabilities. You will receive instructions by browsing websites. 
        I can access a web browser and analyze screenshots to identify links (highlighted in red). 
        Always follow the information in the screenshot, don't guess link names or instruction by the user.
        You have access to a memory store where you can save information 
        To navigate through the pages and manage memory, use the following functions:
        * Enter a URL directly: executeAction({"actionType": "url", "action": "your_url_here"}, driver)
        * Enter a search term: executeAction({"actionType": "search", "action": "your_search_term"}, driver)
        * Click a link by its text: executeAction({"actionType": "click", "action": "your_link_text"}, driver)
        * Type something in a search bar or input field and type enter : handle_typing("placeholder_value","input_text")
        * Scroll the page by one full viewport: executeAction({"actionType": "scroll", "action": null}, driver)
        * Save to memory: memory.add("key", "value")
        Once you've found the answer on a webpage, you can respond with a regular message like 
        If the question/answer suggests a specific URL, go there directly. else make a google search for it
        Remember to use the memory to accumulate information across multiple actions when necessary.

        For each action you decide to take, provide an explanation of why you're taking that action, followed by the textual sumary of the action itself. Format your response like this in a json format
        {
        "Explanation": "Your explanation here",
        "Action": "The action you are taking in text"
     
        }
        This is your memory store for you to refer to:
        
        """ + json.dumps(memory.to_dict())

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{objective}"}
        ]

        while True:
            chat_response = await asyncio.to_thread(chat_completion_request, messages, tools=tools)
            response = chat_response.choices[0].message
            await self.send(text_data=json.dumps({"response": response.content}))


            if response.tool_calls:
                tool_call = response.tool_calls[0]
                arguments = json.loads(tool_call.function.arguments)
                
                if tool_call.function.name == "getting_instructions_tool":
                    instructions = await asyncio.to_thread(getting_instructions_tool, arguments['query'])
                    messages.append({"role": "user", "content": instructions})
                elif tool_call.function.name == "handle_typing":
                    await asyncio.to_thread(handle_typing, driver, arguments['placeholder_value'], arguments['text'])
                elif tool_call.function.name == "memory.add":
                    memory.add(arguments['key'], arguments['value'])
                else:
                    await asyncio.to_thread(execute_action, driver, arguments['actionType'], arguments['action'])

                base64img = await asyncio.to_thread(encode_image, SCREENSHOT_PATH)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Here is the screenshot of the current page after executing: {tool_call.function.name}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64img}"}}
                    ]
                })
                
                await self.send(text_data=json.dumps({"screenshot": base64img}))
            else:
                final_response = {"final_response": response.content}
                await self.send(text_data=json.dumps(final_response))
                break

        await asyncio.to_thread(driver.quit)

# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

        

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)

            
#         if 'objective' in text_data_json:
#             objective = text_data_json['objective']
#             await self.send_message(f"Welcome to the chat i ahve revieve your ibj, {objective}!")
#         else:
#             message = text_data_json['message']
#             await self.send_message(message)
#         print(message)

#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
#     async def send_message(websocket, message):
#         await websocket.send(json.dumps({"message": message}))