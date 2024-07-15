# import re
# import time
# import json
# import base64
# import os
# import asyncio
# from dotenv import load_dotenv
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from openai import OpenAI
# from channels.generic.websocket import AsyncWebsocketConsumer

# load_dotenv()

# GPT_MODEL = "gpt-4o"
# SCREENSHOT_PATH = './screenshot.png'

# client = OpenAI(api_key="sk-proj-V9xPa2nvdJ4DFj4c4bLdT3BlbkFJy7dcTnyIoaZdlqcJNF0R")

# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_url",
#             "description": "Navigate to a specific URL.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "url": {
#                         "type": "string",
#                         "description": "The URL to navigate to."
#                     },
#                     "explanation": {
#                         "type": "string",
#                         "description": "Explanation for why this action is being taken."
#                     },
#                     "action": {
#                         "type": "string",
#                         "description": "Textual summary of the action being taken."
#                     }
#                 },
#                 "required": ["url", "explanation", "action"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_search",
#             "description": "Perform a Google search.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "The search query."
#                     },
#                     "explanation": {
#                         "type": "string",
#                         "description": "Explanation for why this action is being taken."
#                     },
#                     "action": {
#                         "type": "string",
#                         "description": "Textual summary of the action being taken."
#                     }
#                 },
#                 "required": ["query", "explanation", "action"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_click",
#             "description": "Click on an element with the specified text.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "text": {
#                         "type": "string",
#                         "description": "The text of the element to click."
#                     },
#                     "explanation": {
#                         "type": "string",
#                         "description": "Explanation for why this action is being taken."
#                     },
#                     "action": {
#                         "type": "string",
#                         "description": "Textual summary of the action being taken."
#                     }
#                 },
#                 "required": ["text", "explanation", "action"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_scroll",
#             "description": "Scroll the page by one viewport height.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "explanation": {
#                         "type": "string",
#                         "description": "Explanation for why this action is being taken."
#                     },
#                     "action": {
#                         "type": "string",
#                         "description": "Textual summary of the action being taken."
#                     }
#                 },
#                 "required": ["explanation", "action"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_typing",
#             "description": "Type text into an input field with the specified placeholder.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "placeholder_value": {
#                         "type": "string",
#                         "description": "The placeholder value of the input field."
#                     },
#                     "text": {
#                         "type": "string",
#                         "description": "The text to type into the input field."
#                     },
#                     "explanation": {
#                         "type": "string",
#                         "description": "Explanation for why this action is being taken."
#                     },
#                     "action": {
#                         "type": "string",
#                         "description": "Textual summary of the action being taken."
#                     }
#                 },
#                 "required": ["placeholder_value", "text", "explanation", "action"]
#             }
#         }
#     }
# ]

# def initialize_driver():
#     service = Service(ChromeDriverManager().install())
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument('--window-size=1440,900')
#     return webdriver.Chrome(service=service, options=options)

# def highlight_links(driver):
#     script = """
#     (function() {
#         // Remove existing gpt-link-text attributes
#         document.querySelectorAll('[gpt-link-text]').forEach(e => {
#             e.removeAttribute("gpt-link-text");
#         });

#         // Select all elements that can be clickable
#         const elements = document.querySelectorAll(
#             "a, button, input, textarea, [role=button], [role=treeitem]"
#         );

#         elements.forEach(e => {
#             function isElementVisible(el) {
#                 if (!el) return false; // Element does not exist

#                 function isStyleVisible(el) {
#                     const style = window.getComputedStyle(el);
#                     return style.width !== '0' &&
#                         style.height !== '0' &&
#                         style.opacity !== '0' &&
#                         style.display !== 'none' &&
#                         style.visibility !== 'hidden';
#                 }

#                 function isElementInViewport(el) {
#                     const rect = el.getBoundingClientRect();
#                     return (
#                         rect.top >= 0 &&
#                         rect.left >= 0 &&
#                         rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
#                         rect.right <= (window.innerWidth || document.documentElement.clientWidth)
#                     );
#                 }

#                 // Check if the element is visible style-wise
#                 if (!isStyleVisible(el)) {
#                     return false;
#                 }

#                 // Traverse up the DOM and check if any ancestor element is hidden
#                 let parent = el;
#                 while (parent) {
#                     if (!isStyleVisible(parent)) {
#                         return false;
#                     }
#                     parent = parent.parentElement;
#                 }

#                 // Finally, check if the element is within the viewport
#                 return isElementInViewport(el);
#             }

#             // Add red border to the element
#             e.style.border = "1px solid red";

#             const position = e.getBoundingClientRect();

#             if (position.width > 5 && position.height > 5 && isElementVisible(e)) {
#                 const link_text = e.textContent.replace(/[^a-zA-Z0-9 ]/g, '');
#                 e.setAttribute("gpt-link-text", link_text);
#             }
#         });
#     })();
#     """
#     try:
#         driver.execute_script(script)
#         driver.save_screenshot(SCREENSHOT_PATH)
#     except Exception:
#         pass


# def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
#     try:
#         return client.chat.completions.create(
#             model=model,
#             messages=messages,
#             tools=tools,
#             tool_choice=tool_choice,
#         )
#     except Exception as e:
#         return e

# def preprocess_text(text):
#     return re.sub(r'[^\w\s]', '', text).lower()

# def handle_url(driver, url):
#     driver.get(url)
#     highlight_links(driver)

# def handle_search(driver, query):
#     driver.get(f"https://www.google.com/search?q={query}")
#     highlight_links(driver)

# def handle_click(driver, link_text):
#     print(f"Clicking on {link_text}")
#     try:
#         elements = driver.find_elements(By.CSS_SELECTOR, '[gpt-link-text]')
#         with open("output.txt", "w") as file:
#             for element in elements:
#                 file.write(element.get_attribute('gpt-link-text') + "\n")
        
#         partial = next((e for e in elements if preprocess_text(link_text) in preprocess_text(e.get_attribute('gpt-link-text'))), None)
#         exact = next((e for e in elements if preprocess_text(e.get_attribute('gpt-link-text')) == preprocess_text(link_text)), None)
                    
#         if exact:
#             exact.click()
#         elif partial:
#             partial.click()
#         else:
#             raise Exception("Can't find link")
#     except Exception:
#         print("Can't find link")
#     finally:
#         time.sleep(5)
#     highlight_links(driver)
        

# def handle_scroll(driver):
#     try:
#         viewport_height = driver.execute_script("return window.innerHeight")
#         driver.execute_script(f"window.scrollBy(0, {viewport_height});")
#         time.sleep(1)
#         highlight_links(driver)
#     except Exception:
#         pass

# def handle_typing(driver, placeholder_value, text):
#     elements = driver.find_elements(By.CSS_SELECTOR, f'input[placeholder="{placeholder_value}"]')
#     if elements:
#         element = elements[0]
#         element.clear()
#         element.send_keys(text)
#         element.send_keys(Keys.RETURN)
#         highlight_links(driver)

# def encode_image(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send(text_data=json.dumps({"message": "Connected to WebSocket"}))

#     async def disconnect(self, close_code):
#         # Cleanup code here (e.g., closing the driver)
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         if 'objective' in text_data_json:
#             objective = text_data_json['objective']
#             await self.main_loop(objective)
#         else:
#             message = text_data_json['message']
#             print(message)

#     async def main_loop(self, objective):
#         driver = await asyncio.to_thread(initialize_driver)
        
#         system_prompt = """
#         You are a website crawler. You will receive instructions for browsing websites. 
#         I can access a web browser and analyze screenshots to identify links (highlighted in red). 
#         Always follow the information in the screenshot, don't guess link names or instructions.
#         To navigate through the pages, use the following functions:
#         * Navigate to a URL: handle_url({"url": "your_url_here", "explanation": "...", "action": "..."})
#         * Perform a Google search: handle_search({"query": "your_search_query", "explanation": "...", "action": "..."})
#         * Click a link by its text: handle_click({"text": "your_link_text", "explanation": "...", "action": "..."})
#         * Scroll the page: handle_scroll({"explanation": "...", "action": "..."})
#         * Type in an input field: handle_typing({"placeholder_value": "placeholder", "text": "your_text", "explanation": "...", "action": "..."})
#         For each action, provide an explanation of why you're taking that action and a textual summary of the action itself.
#         Once you've found the answer on a webpage, you can respond with a regular message like:
#         {
#         "finalResponse": "Your response here"
#         }
#         If the question/answer suggests a specific URL, go there directly. Otherwise, perform a Google search for it.
#         """

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": f"{objective}"}
#         ]

#         while True:
#             chat_response = await asyncio.to_thread(chat_completion_request, messages, tools=tools)
#             response = chat_response.choices[0].message
#             await self.send(text_data=json.dumps({"response": response.content}))

#             if response.tool_calls:
#                 tool_call = response.tool_calls[0]
#                 function_name = tool_call.function.name
#                 arguments = json.loads(tool_call.function.arguments)
                
#                 explanation = arguments.get('explanation', '')
#                 action = arguments.get('action', '')
                
#                 await self.send(text_data=json.dumps({
#                     "explanation": explanation,
#                     "action": action
#                 }))

#                 if function_name == "handle_url":
#                     await asyncio.to_thread(handle_url, driver, arguments['url'])
#                 elif function_name == "handle_search":
#                     await asyncio.to_thread(handle_search, driver, arguments['query'])
#                 elif function_name == "handle_click":
#                     print("clicking on",arguments['text'])
#                     await asyncio.to_thread(handle_click, driver, arguments['text'])
#                 elif function_name == "handle_scroll":
#                     await asyncio.to_thread(handle_scroll, driver)
#                 elif function_name == "handle_typing":
#                     await asyncio.to_thread(handle_typing, driver, arguments['placeholder_value'], arguments['text'])

#                 base64img = await asyncio.to_thread(encode_image, SCREENSHOT_PATH)
#                 messages.append({
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": f"Here is the screenshot of the current page after executing: {function_name}"},
#                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64img}"}}
#                     ]
#                 })
                
#                 await self.send(text_data=json.dumps({"screenshot": base64img}))
#             else:
#                 final_response = {"final_response": response.content}
#                 await self.send(text_data=json.dumps(final_response))
#                 break

#         await asyncio.to_thread(driver.quit)
import re
import time
import json
import base64
from os import getenv, path
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
from webdriver_manager.core.utils import ChromeType


load_dotenv()

GPT_MODEL = "gpt-4o"
SCREENSHOT_PATH = './screenshot.png'
STARTING_SCENE_PATH = './startingscene.png'

client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "handle_url",
            "description": "Navigate to a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explanation for why this action is being taken."
                    },
                    "action": {
                        "type": "string",
                        "description": "Textual summary of the action being taken."
                    }
                },
                "required": ["url", "explanation", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_search",
            "description": "Perform a Google search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explanation for why this action is being taken."
                    },
                    "action": {
                        "type": "string",
                        "description": "Textual summary of the action being taken."
                    }
                },
                "required": ["query", "explanation", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_click",
            "description": "Click on an element with the specified text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text of the element to click."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explanation for why this action is being taken."
                    },
                    "action": {
                        "type": "string",
                        "description": "Textual summary of the action being taken."
                    }
                },
                "required": ["text", "explanation", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_scroll",
            "description": "Scroll the page by one viewport height.",
            "parameters": {
                "type": "object",
                "properties": {
                    "explanation": {
                        "type": "string",
                        "description": "Explanation for why this action is being taken."
                    },
                    "action": {
                        "type": "string",
                        "description": "Textual summary of the action being taken."
                    }
                },
                "required": ["explanation", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_typing",
            "description": "Type text into an input field with the specified placeholder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "placeholder_value": {
                        "type": "string",
                        "description": "The placeholder value of the input field."
                    },
                    "text": {
                        "type": "string",
                        "description": "The text to type into the input field."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explanation for why this action is being taken."
                    },
                    "action": {
                        "type": "string",
                        "description": "Textual summary of the action being taken."
                    }
                },
                "required": ["placeholder_value", "text", "explanation", "action"]
            }
        }
    }
]

def initialize_driver():
    # service = Service(ChromeDriverManager().install())
    service = Service(ChromeDriverManager(version="specific_version").install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--window-size=1440,900')
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
            //e.style.border = "1px solid red";

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

def handle_url(driver, url):
    driver.get(url)
    highlight_links(driver)

def handle_search(driver, query):
    driver.get(f"https://www.google.com/search?q={query}")
    highlight_links(driver)

def handle_click(driver, link_text):
    print(f"Clicking on {link_text}")
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, '[gpt-link-text]')
        # with open("output.txt", "w") as file:
        #     for element in elements:
        #         file.write(element.get_attribute('gpt-link-text') + "\n")
        
        partial = next((e for e in elements if preprocess_text(link_text) in preprocess_text(e.get_attribute('gpt-link-text'))), None)
        exact = next((e for e in elements if preprocess_text(e.get_attribute('gpt-link-text')) == preprocess_text(link_text)), None)
                    
        if exact:
            exact.click()
        elif partial:
            partial.click()
        else:
            raise Exception("Can't find link")
    except Exception:
        print("Can't find link")
    finally:
        time.sleep(5)
    highlight_links(driver)
        

def handle_scroll(driver):
    try:
        viewport_height = driver.execute_script("return window.innerHeight")
        driver.execute_script(f"window.scrollBy(0, {viewport_height});")
        time.sleep(1)
        highlight_links(driver)
    except Exception:
        pass

def handle_typing(driver, placeholder_value, text):
    elements = driver.find_elements(By.CSS_SELECTOR, f'input[placeholder="{placeholder_value}"]')
    if elements:
        element = elements[0]
        element.clear()
        element.send_keys(text)
        element.send_keys(Keys.RETURN)
        highlight_links(driver)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected to WebSocket"}))

    async def disconnect(self, close_code):
        if os.path.exists(SCREENSHOT_PATH):
            os.remove(SCREENSHOT_PATH)
        pass
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

    async def send_screenshots(self, driver):
        while True:
            await asyncio.sleep(1)  # Wait for 2 seconds
            if os.path.exists(SCREENSHOT_PATH):
                base64img = await asyncio.to_thread(encode_image, SCREENSHOT_PATH)
            else:
                base64img = await asyncio.to_thread(encode_image, STARTING_SCENE_PATH)
            await self.send(text_data=json.dumps({"screenshot": base64img}))

    async def main_loop(self, objective):
        driver = await asyncio.to_thread(initialize_driver)
        
        # Start the screenshot sending task
        screenshot_task = asyncio.create_task(self.send_screenshots(driver))
        
        system_prompt = """
        You are a website crawler. You will receive instructions for browsing websites. 
        I can access a web browser and analyze screenshots to identify links (highlighted in red). 
        Always follow the information in the screenshot, don't guess link names or instructions.
        To navigate through the pages, use the following functions:
        * Navigate to a URL: handle_url({"url": "your_url_here", "explanation": "...", "action": "..."})
        * Perform a Google search: handle_search({"query": "your_search_query", "explanation": "...", "action": "..."})
        * Click a link by its text: handle_click({"text": "your_link_text", "explanation": "...", "action": "..."})
        * Scroll the page: handle_scroll({"explanation": "...", "action": "..."}) 
        * Type in an input field: handle_typing({"placeholder_value": "placeholder", "text": "your_text", "explanation": "...", "action": "..."})
        For each action, provide an explanation of why you're taking that action and a textual summary of the action itself.
        Once you've found the answer on a webpage, you can respond with a regular message.
        If the question/answer suggests a specific URL, go there directly. Otherwise, perform a Google search for it.
        """

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
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                explanation = arguments.get('explanation', '')
                action = arguments.get('action', '')
                
                await self.send(text_data=json.dumps({
                    "explanation": explanation,
                    "action": action
                }))

                if function_name == "handle_url":
                    await asyncio.to_thread(handle_url, driver, arguments['url'])
                elif function_name == "handle_search":
                    await asyncio.to_thread(handle_search, driver, arguments['query'])
                elif function_name == "handle_click":
                    print("clicking on",arguments['text'])
                    await asyncio.to_thread(handle_click, driver, arguments['text'])
                elif function_name == "handle_scroll":
                    await asyncio.to_thread(handle_scroll, driver)
                elif function_name == "handle_typing":
                    await asyncio.to_thread(handle_typing, driver, arguments['placeholder_value'], arguments['text'])

                base64img = await asyncio.to_thread(encode_image, SCREENSHOT_PATH)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Here is the screenshot of the current page after executing: {function_name}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64img}"}}
                    ]
                })
            else:
                final_response = {"final_response": response.content}
                await self.send(text_data=json.dumps(final_response))
                break

        # After the while loop ends:
        screenshot_task.cancel()  # Stop the screenshot task
        

        await asyncio.to_thread(driver.quit)



