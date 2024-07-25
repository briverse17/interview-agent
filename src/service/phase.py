import os
import time
from enum import Enum
from typing import Callable, Dict, List

from src.service.document import Document
from src.settings import DIRECTORIES
from src.utils import add_debug, get_filepath


class PhaseUpdateType(Enum):
    PRIMARY = "primary"
    FOLLOW = "follow"


class HistoryEntryItem:
    def __init__(self, role, content) -> None:
        self.role = role
        self.content = content

    @property
    def st_role(self):
        if self.role == "question":
            return "assistant"
        if self.role == "answer":
            return "user"

class HistoryEntry:
    def __init__(self) -> None:
        self.timestamp = int(time.time())
        self._question: HistoryEntryItem
        self._answer: HistoryEntryItem
        self._evaluation: HistoryEntryItem

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, item):
        self._question = item

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, item):
        self._answer = item

    @property
    def evaluation(self):
        return self._evaluation

    @evaluation.setter
    def evaluation(self, item):
        self._evaluation = item


class Instructions:
    def __init__(self, prefix: str) -> None:
        primary_filepath = get_filepath("instruction", prefix, "primary.md")
        questions_filepath = get_filepath("instruction", prefix, "questions.md")
        eval_filepath = get_filepath("instruction", prefix, "eval.md")
        follow_filepath = get_filepath("instruction", prefix, "follow.md")

        self.primary = Document(primary_filepath, f"{prefix}".upper())
        self.questions = Document(questions_filepath, f"{prefix}_questions".upper())
        self.eval = Document(eval_filepath, f"{prefix}_eval".upper())
        self.follow = Document(follow_filepath, f"{prefix}_follow".upper())


class Phase:
    def __init__(self, name) -> None:
        self.name = name
        self.instructions = Instructions(self.name)
        self.questions: Document = None
        self.history: List[HistoryEntry] = []

    def make_questions(self, inferencer: Callable):
        instruction = self.populate("primary")
        return inferencer(instruction)

    def update(self, inferencer: Callable, type: PhaseUpdateType):
        if not self.questions:
            self.questions = self.make_questions(inferencer)
            add_debug(f"{self.name} make questions".upper(), self.questions)
        add_debug("phase update".upper(), self.name, type.value)

        instruction = self.populate(type.value)
        return instruction

    def evaluate(self, inferencer: Callable):
        instruction = self.populate("eval")
        evaluation = inferencer(instruction)
        add_debug(f"{self.name} eval".upper(), evaluation)
        self.update_history("evaluation", evaluation)

    def follow(self, inferencer: Callable):
        instruction = self.populate("follow")
        following = inferencer(instruction)
        add_debug(f"{self.name} follow".upper(), following)

        match self.name:
            case "start":
                if "technical_phase" in following:
                    return "technical", PhaseUpdateType.PRIMARY
            case "technical":
                if "behavioral_phase" in following:
                    return "behavioral", PhaseUpdateType.PRIMARY
            case "behavioral":
                if "experience_phase" in following:
                    return "experience", PhaseUpdateType.PRIMARY
            case "experience":
                if "qna_phase" in following:
                    return "qna", PhaseUpdateType.PRIMARY
            case "qna":
                if "finish_phase" in following:
                    return "finish", PhaseUpdateType.PRIMARY

        return self.name, PhaseUpdateType.FOLLOW

    def update_history(self, type: str, content: str):
        if type == "question":
            self.history.append(HistoryEntry())
        setattr(self.history[-1], type, HistoryEntryItem(type, content))

    def stringify_history(self):
        history = ""
        for item in self.history:
            history += f'Question: "{item.question.content}"\n'
            history += f'Answer: "{item.answer.content}"\n'

        last_eval = getattr(self.history[-1], "evaluation", None)
        if last_eval:
            history += f'Last Evaluation: "{last_eval.content}"\n'
        return history

    def populate(self, step: str):
        kwargs = {}
        if step != "primary":
            history = self.stringify_history()
            kwargs = {"questions": self.questions, "history": history}
        populated = getattr(self.instructions, step).content.format(**kwargs)
        return populated


class Phases:
    def __init__(self) -> None:
        self.start = Phase("start")
        self.technical = Phase("technical")
        self.behavioral = Phase("behavioral")
        self.experience = Phase("experience")
        self.qna = Phase("qna")
        self.finish = Phase("finish")
