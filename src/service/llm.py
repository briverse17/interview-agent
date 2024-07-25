import os
import time
from typing import Dict, List

import google.generativeai as genai

from src.service.application import Application, ApplicationData
from src.service.document import Document
from src.service.phase import Phase, Phases, PhaseUpdateType
from src.settings import APIKEY
from src.utils import add_debug, get_filepath, read_file, write_file, write_json


class LLM:
    def __init__(self, model_name: str, application: Application) -> None:
        genai.configure(api_key=APIKEY)
        self.timestamp = int(time.time())
        self.model_name = model_name
        self.application = application
        self.model = self.get_model()
        # self.session = self.model.start_chat(history=[])
        self.phases = Phases()
        self.current_phase: Phase = None

    def single(self, content):
        return self.model.generate_content(content).text

    def stream(self, content):
        response = self.model.generate_content(content, stream=True)
        for chunk in response:
            yield chunk.text.rstrip("\n")

    def write_report(self):
        report_filepath = get_filepath("report", f"{self.code}_{self.timestamp}.json")
        write_json(report_filepath, self.report)

    def eval(self):
        self.current_phase.evaluate(self.single)

    def follow(self):
        return self.current_phase.follow(self.single)

    def update(
        self,
        phase_name: str = None,
        type: PhaseUpdateType = PhaseUpdateType.PRIMARY,
    ):
        phase: Phase = getattr(self.phases, phase_name)
        self.current_phase = phase
        instruction = self.current_phase.update(self.single, type)
        yield from self.stream(instruction)

    def get_model(self):
        document = Document(get_filepath("instruction", "system.md"))
        system_instruction = document.content.format(
            job_document=self.parse_document("job"),
            candidate_document=self.parse_document("candidate"),
        )
        add_debug(f"system instruction".upper(), system_instruction)
        return genai.GenerativeModel(
            self.model_name, system_instruction=system_instruction
        )

    def parse_document(self, type: str):
        data: ApplicationData = getattr(self.application, type)

        rootname = os.path.splitext(data.document.filename)[0]
        parsed_filepath = get_filepath("cache", f"parsed_{type}_{rootname}.md")

        document = None
        if os.path.isfile(parsed_filepath):
            document = read_file(parsed_filepath)
        else:
            instruction = Document(get_filepath("instruction", "system_parse_doc.md"))
            system_instruction = instruction.content.format(
                document_type=data.document.filetype,
                document_name=data.document.title,
                document_raw_content=data.document.content,
            )

            helper_model = genai.GenerativeModel(
                self.model_name, system_instruction=system_instruction
            )

            instruction1 = Document(get_filepath("instruction", f"parse_{type}.md"))
            response = helper_model.generate_content(instruction1.content)
            document = response.text
            write_file(parsed_filepath, document)

        data.document.parsed_content = document
        setattr(self.application, type, data)
        add_debug(f"{data.document.title}".upper(), document)
        return document
