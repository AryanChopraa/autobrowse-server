TOOLS = [
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