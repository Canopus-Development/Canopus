import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage,
    UserMessage,
    TextContentItem,
    ImageContentItem,
    ImageUrl,
    ImageDetailLevel,
    AssistantMessage,
    ChatCompletionsToolCall,
    ChatCompletionsToolDefinition,
    CompletionsFinishReason,
    FunctionDefinition,
    ToolMessage,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

class AIModelManager:
    def __init__(self, config):
        self.token = os.getenv("AZURE_TOKEN")
        self.endpoint = config.get('azure_endpoint', "https://models.inference.ai.azure.com")
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.token),
        )
        self.models = {
            'gpt4-vision': "gpt-4o",
            'llama': "Llama-3.3-70B-Instruct",
            'cohere': "Cohere-command-r-plus"
        }

    def process_image(self, image_path, prompt="What's in this image?"):
        response = self.client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant that describes images in details."),
                UserMessage(content=[
                    TextContentItem(text=prompt),
                    ImageContentItem(
                        image_url=ImageUrl.load(
                            image_file=image_path,
                            image_format=image_path.split('.')[-1],
                            detail=ImageDetailLevel.LOW
                        )
                    ),
                ]),
            ],
            model=self.models['gpt4-vision'],
        )
        return response.choices[0].message.content

    def get_completion(self, messages, model_type='llama', tools=None):
        return self.client.complete(
            messages=messages,
            tools=tools,
            model=self.models[model_type],
        )
