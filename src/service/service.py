import os
from typing import Dict

import google.generativeai as genai

import src.settings as settings
import src.utils as utils


class Service:
    def __init__(self, model_name: str, application: Dict) -> None:
        genai.configure(api_key=settings.APIKEY)
        self.model_name = model_name
        self.application = application
        self.model = self.get_model()
        self.session = self.model.start_chat(history=[])
        self.started = False

    def chat(self, user_message: str):
        response = self.session.send_message(user_message, stream=True)
        for chunk in response:
            yield chunk.text.rstrip("\n")

    def generate(self, user_message: str):
        response = self.model.generate_content(user_message)
        return response

    def start(self, instruction: str):
        #  Prompt them to tell their past experiences related to 'job title'
        yield from self.chat(instruction)
        self.started = True

    def get_model(self):
        self.parsed_job_document = self.parse_document("job")
        self.parsed_candidate_document = self.parse_document("candidate")
        system_instruction = utils.get_instruction(
            "system",
            job_document=self.parsed_job_document,
            candidate_document=self.parsed_candidate_document,
        )
        return genai.GenerativeModel(
            self.model_name, system_instruction=system_instruction
        )

    def parse_document(self, type: str):
        rootname = os.path.splitext(self.application[type]["filename"])[0]
        parsed_filepath = utils.get_filepath("cache", f"parsed_{type}_{rootname}.md")

        document_name = "Job Description" if type == "job" else "Candidate Profile"
        document = None
        if os.path.isfile(parsed_filepath):
            document = utils.read_file(parsed_filepath)
        else:
            document_type = self.application[type]["filetype"]
            document_raw_content = self.application[type]["document"]
            system_instruction = utils.get_instruction(
                "system_parse_doc",
                document_type=document_type,
                document_name=document_name,
                document_raw_content=document_raw_content,
            )

            helper_model = genai.GenerativeModel(
                self.model_name, system_instruction=system_instruction
            )

            parse_instruction = utils.get_instruction(f"parse_{type}")
            response = helper_model.generate_content(parse_instruction)
            document = response.text
            utils.write_file(parsed_filepath, document)

        if settings.DEBUGGING:
            utils.add_debug(f"{document_name}".upper(), document)
        return document
