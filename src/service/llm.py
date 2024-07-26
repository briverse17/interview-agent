import os
import time

import google.generativeai as genai

from src.service.application import Application, ApplicationData
from src.service.document import Document
from src.service.phase import Phase, Phases, PhaseUpdateType
from src.settings import APIKEY
from src.utils import add_debug, get_path, read_file, write_file, write_json


class LLM:
    def __init__(self, model_name: str, application: Application) -> None:
        genai.configure(api_key=APIKEY)
        self.timestamp = int(time.time())
        self.model_name = model_name
        self.application = application
        self.model = self.get_model()
        self.session = self.model.start_chat(history=[])
        self.phases = Phases()
        self.current_phase: Phase = None
        self.terminated = False

    @property
    def chat_history(self):
        return self.phases.history

    def single(self, content=None):
        history = self.phases.api_history
        if content:
            history.append({"role": "user", "parts": [content]})
        return self.model.generate_content(history).text

    def stream(self, content):
        response = self.session.send_message(content, stream=True)
        for chunk in response:
            yield chunk.text.rstrip("\n")

    def make_report(self):
        report = self.single(
            (
                "Process the whole conversation and make a report conforming the following format"
                "---"
                "SCREENING REPORT FOR [CANDIDATE FULLNAME]"
                "## Overview"
                "/* List your general assessments of the candidate as bullet points */"
                "/* No more than 4 points */"
                "## Technical"
                "/* List your assessments of the technical fit between the candidate and the job as bullet points */"
                "/* No more than 5 points */"
                "## Behavioral"
                "/* List your assessments of the behavioral fit between the candidate and the job as bullet points */"
                "/* No more than 5 points */"
                "## Conclusion"
                "/* List your subjective conclusion on whether the company should proceed with this application as bullet points */"
                "/* No more than 3 points */"
            )
        )
        filepath = get_path("report", f"{self.application.id}_{self.timestamp}.md")
        write_file(filepath, report)
        return report

    def dump_conversations(self):
        filepath = get_path(
            "conversation", f"{self.application.id}_{self.timestamp}.json"
        )
        write_json(filepath, self.phases.__dict__())

    def eval(self):
        self.current_phase.evaluate(self.single)

    def proceed(self):
        return self.current_phase.proceed(self.single)

    def update(
        self,
        phase_name: str = None,
        type: PhaseUpdateType = PhaseUpdateType.PRIMARY,
        msg: str = None,
    ):
        if type == PhaseUpdateType.PROCEED:
            yield msg
        else:
            if phase_name == "terminate":
                yield from self.stream(
                    "We are terminating the interview. Say thanks to the candidate one more time and wish them best luck."
                )
                self.terminated = True
            else:
                phase: Phase = getattr(self.phases, phase_name)
                self.current_phase = phase
                instruction = self.current_phase.primary(
                    self.single, self.application.id
                )
                yield from self.stream(instruction)

    def get_model(self):
        document = Document(get_path("instruction", "system.md"))
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
        parsed_filepath = get_path("cache", f"parsed_{type}_{rootname}.md")

        document = None
        if os.path.isfile(parsed_filepath):
            document = read_file(parsed_filepath)
        else:
            instruction = Document(get_path("instruction", "system_parse_doc.md"))
            system_instruction = instruction.content.format(
                document_type=data.document.filetype,
                document_name=data.document.title,
                document_raw_content=data.document.content,
            )

            helper_model = genai.GenerativeModel(
                self.model_name, system_instruction=system_instruction
            )

            instruction1 = Document(get_path("instruction", f"parse_{type}.md"))
            response = helper_model.generate_content(instruction1.content)
            document = response.text
            write_file(parsed_filepath, document)

        data.document.parsed_content = document
        setattr(self.application, type, data)
        add_debug(f"{data.document.title}".upper(), document)
        return document
