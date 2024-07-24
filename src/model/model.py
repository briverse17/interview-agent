import google.generativeai as genai

from src.settings import APIKEY


class Service:
    def __init__(self, model_name: str, system_instruction: str) -> None:
        genai.configure(api_key=APIKEY)
        self.model = genai.GenerativeModel(
            model_name, system_instruction=system_instruction
        )
        self.session = self.model.start_chat(history=[])
        self.started = False

    def chat(self, user_message: str):
        response = self.session.send_message(user_message, stream=True)
        for chunk in response:
            yield chunk.text.rstrip("\n")

    def start(self, instruction: str):
        yield from self.chat(instruction)
        self.started = True
