import json
import os
import time
from typing import Dict, List

import google.generativeai as genai

import src.settings as settings
import src.utils as utils


class Service:
    def __init__(self, model_name: str, code: str) -> None:
        genai.configure(api_key=settings.APIKEY)
        self.model_name = model_name
        self.code = code
        self.application = utils.get_application(self.code)
        self.model = self.get_model()
        self.session = self.model.start_chat(history=[])
        self.timestamp = int(time.time())
        self.report: Dict[str, List[Dict[str, str]]] = {}
        self.phase = None
        self.questions = {}

    def chat(self, content: str = None):
        response = self.session.send_message(content, stream=True)
        for chunk in response:
            yield chunk.text.rstrip("\n")

    def generate(self, content: str, text=True):
        # messages = [{'role':'user', 'parts': ['hello']}]
        # >>> response = model.generate_content(messages) # "Hello, how can I help"
        # >>> messages.append(response.candidates[0].content)
        response = self.model.generate_content(content)
        if text:
            response = response.text
        return response

    def write_report(self):
        report_filepath = utils.get_filepath(
            "report", f"{self.code}_{self.timestamp}.json"
        )
        utils.write_json(report_filepath, self.report)

    def update_report(self, type: str, content: str):
        if type == "question":
            self.report[self.phase].append({})
        self.report[self.phase][-1][type] = content

    def stringify_history(self):
        history = ""
        for data in self.report[self.phase]:
            question = data["question"]
            history += f'Question: "{question}"\n'
            answer = data["answer"]
            history += f'Answer: "{answer}"\n'
            evaluation = data.get("evaluation")
            if evaluation:
                history += f'Evaluation: "{evaluation}"\n'

        return history

    def eval(self):
        history = self.stringify_history()

        questions = None
        if self.phase in self.questions:
            questions = self.questions[self.phase]
        instruction = utils.get_instruction(
            f"{self.phase}_eval", questions=questions, history=history
        )

        evaluation = self.generate(instruction)
        self.update_report("evaluation", evaluation)

        utils.add_debug("start eval".upper(), evaluation)

        self.write_report()
        return evaluation

    def follow(self):
        history = self.stringify_history()
        questions = None
        if self.phase in self.questions:
            questions = self.questions[self.phase]
        instruction = utils.get_instruction(
            f"{self.phase}_follow", questions=questions, history=history
        )
        following = self.generate(instruction)

        if self.phase == "start":
            if "technical_phase" in following:
                return "technical", True
        if self.phase == "technical":
            if "behavioral_phase" in following:
                return "behavioral", True
        return self.phase, False

    def update(self, phase: str = None, primary=True):
        self.phase = phase
        if not phase in self.report:
            self.report[self.phase] = []
            self.make_questions()

        utils.add_debug("phase update".upper(), phase, primary)

        questions = None
        if phase in self.questions:
            questions = self.questions[phase]

        if primary:
            instruction = utils.get_instruction(self.phase, questions=questions)
            yield from self.chat(instruction)
        else:
            history = self.stringify_history()
            instruction = utils.get_instruction(
                f"{self.phase}_follow", questions=questions, history=history
            )
            yield from self.chat(instruction)

    def get_model(self):
        self.parsed_job_document = self.parse_document("job")
        self.parsed_candidate_document = self.parse_document("candidate")
        system_instruction = utils.get_instruction(
            "system",
            job_document=self.parsed_job_document,
            candidate_document=self.parsed_candidate_document,
        )
        utils.add_debug(f"system instruction".upper(), system_instruction)
        return genai.GenerativeModel(
            self.model_name, system_instruction=system_instruction
        )

    def make_questions(self):
        try:
            instruction = utils.get_instruction(f"{self.phase}_questions")
            self.questions[self.phase] = self.generate(instruction)
            utils.add_debug(
                f"{self.phase} make questions".upper(), self.questions[self.phase]
            )
        except Exception as e:
            utils.add_debug(f"{self.phase} make questions".upper(), e.args[-1])

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

        utils.add_debug(f"{document_name}".upper(), document)
        return document
