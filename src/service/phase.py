import os
import string
import time
from enum import Enum
from typing import Callable, Dict, Iterable, Iterator, List

from src.service.document import Document
from src.settings import DIRECTORIES
from src.utils import add_debug, get_path, write_file


class PhaseUpdateType(Enum):
    PRIMARY = "primary"
    PROCEED = "proceed"


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

    @property
    def api_role(self):
        if self.role == "question":
            return "model"
        if self.role == "answer":
            return "user"


class HistoryEntry(Dict[str, HistoryEntryItem]):
    def __init__(self) -> Dict[str, HistoryEntryItem]:
        self.timestamp = int(time.time())
        self.question: HistoryEntryItem = None
        self.answer: HistoryEntryItem = None
        self.evaluation: HistoryEntryItem = None

    def __setitem__(self, key: str, value: HistoryEntryItem) -> None:
        setattr(self, key, value)

    def __getitem__(self, key: str) -> HistoryEntryItem:
        return getattr(self, key, None)

    def __dict__(self):
        _dict = {}
        for key in ("question", "answer", "evaluation"):
            if self[key]:
                _dict[key] = self[key].content
        return _dict


class History(List[HistoryEntry]):
    def __init__(self) -> List[HistoryEntry]:
        pass

    def __setitem__(self, index: int, item: HistoryEntry):
        super().__setitem__(index, item)

    def __str__(self) -> str:
        history = ""
        for item in self:
            history += f'Question: "{item.question.content}"\n'
            history += f'Answer: "{item.answer.content}"\n'
            history += "##########"

        if self[-1]["evaluation"]:
            history += f'Last Evaluation: "{self[-1]["evaluation"].content}"\n'
        return history

    def update(self, type: str, content: str):
        if type == "question":
            self.append(HistoryEntry())
        self[-1][type] = HistoryEntryItem(type, content)


class Instruction(Document):
    def __init__(self, path: str, title: str = None):
        super().__init__(path, title)

    @property
    def params(self):
        return [
            tup[1]
            for tup in string.Formatter().parse(self.content)
            if tup[1] is not None
        ]

    def populate(self, history: History = None, questions: Document = None):
        kwargs = {}
        for param in self.params:
            match param:
                # case "question":
                #     kwargs["question"] = history[-1].question
                # case "answer":
                #     kwargs["answer"] = history[-1].answer
                # case "evaluation":
                #     kwargs["evaluation"] = history[-1].evaluation
                # case "history":
                #     kwargs["history"] = str(history)
                case "questions":
                    kwargs["questions"] = questions.content
                case _:
                    add_debug(
                        f"{self.title} population".upper(), f"Unknown param {param}"
                    )
        return self.content.format(**kwargs)


class Instructions(Dict[str, Instruction]):
    def __init__(self, prefix: str) -> Dict[str, Instruction]:
        self.prefix = prefix
        self.primary: Instruction = None
        self.questions: Instruction = None
        self.eval: Instruction = None
        self.proceed: Instruction = None

        self.directory = get_path("instruction", self.prefix)
        filenames = os.listdir(self.directory)

        for filename in filenames:
            step = filename.removesuffix(".md")
            self[step] = Instruction(
                os.path.join(self.directory, filename), f"{self.prefix} - {step}"
            )

    def __getitem__(self, key: str) -> Instruction:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Instruction) -> None:
        setattr(self, key, value)


class Phase:
    def __init__(self, name) -> None:
        self.name = name
        self.instructions = Instructions(self.name)
        self.questions: Document = None
        self.history = History()

    def make_questions(self, inferencer: Callable, interview_id: str):
        if self.instructions.questions:
            filepath = get_path("cache", f"questions_{self.name}_{interview_id}.md")
            if not os.path.isfile(filepath):
                instruction = self.instructions.questions.populate()
                generation = inferencer(instruction)
                write_file(filepath, generation)
            self.questions = Document(filepath)

    def primary(self, inferencer: Callable, interview_id: str):
        if not self.questions:
            self.make_questions(inferencer, interview_id)

        instruction = self.instructions.primary.populate(questions=self.questions)
        add_debug(f"phase {self.name} - primary".upper(), "Instruction", instruction)
        return instruction

    def evaluate(self, inferencer: Callable):
        instruction = self.instructions.eval.populate(questions=self.questions)
        evaluation = inferencer(instruction)
        add_debug(f"phase {self.name} - eval".upper(), evaluation)
        self.history.update("evaluation", evaluation)

    def proceed(self, inferencer: Callable):
        instruction = self.instructions.proceed.populate(questions=self.questions)
        proceeds = inferencer(instruction)
        add_debug(f"phase {self.name} - proceed".upper(), proceeds)

        match self.name:
            case "start":
                if "technical_phase" in proceeds:
                    return "technical", PhaseUpdateType.PRIMARY, None
            case "technical":
                if "behavioral_phase" in proceeds:
                    return "behavioral", PhaseUpdateType.PRIMARY, None
            case "behavioral":
                if "qna_phase" in proceeds:
                    return "qna", PhaseUpdateType.PRIMARY, None
            case "qna":
                if "finish_phase" in proceeds:
                    return "finish", PhaseUpdateType.PRIMARY, None
            case "finish":
                if "terminate_phase" in proceeds:
                    return "terminate", PhaseUpdateType.PRIMARY, None

        return self.name, PhaseUpdateType.PROCEED, proceeds


class Phases(Dict[str, Phase]):
    def __init__(self) -> None:
        self.start = Phase("start")
        self.technical = Phase("technical")
        self.behavioral = Phase("behavioral")
        self.qna = Phase("qna")
        self.finish = Phase("finish")

    def __setitem__(self, key: str, value: Phase) -> None:
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Phase:
        return getattr(self, key, None)

    @property
    def history(self) -> Iterator[HistoryEntryItem]:
        for name in ("start", "technical", "behavioral", "qna", "finish"):
            for entry in self[name].history:
                for item_name in ("question", "answer"):
                    if entry[item_name]:
                        yield entry[item_name]

    @property
    def api_history(self):
        """
        >>> messages = [{'role':'user', 'parts': ['hello']}]
        >>> response = model.generate_content(messages) # "Hello, how can I help"
        >>> messages.append(response.candidates[0].content)
        >>> messages.append({'role':'user', 'parts': ['How does quantum physics work?']})
        >>> response = model.generate_content(messages)
        """
        messages = []
        for name in ("start", "technical", "behavioral", "qna", "finish"):
            for i, entry in enumerate(self[name].history):
                q = [entry["question"].content]
                a = [entry["answer"].content]
                e = None
                if i > 0:
                    e = self[name].history[i - 1]["evaluation"].content
                    e = f"Evaluation of previous answer\n{e}"
                    q = [e] + q
                messages.extend(
                    [{"role": "model", "parts": q}, {"role": "user", "parts": a}]
                )
        return messages

    def __dict__(self):
        _dict = {}
        for name in ("start", "technical", "behavioral", "qna", "finish"):
            entries = []
            for entry in self[name].history:
                entries.append(entry.__dict__())
            _dict[name] = entries

        return _dict
