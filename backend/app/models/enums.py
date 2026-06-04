from enum import StrEnum


class UserRole(StrEnum):
    participant = "participant"
    jury = "jury"
    organizer = "organizer"


class HackathonStatus(StrEnum):
    draft = "draft"
    registration = "registration"
    in_progress = "in_progress"
    judging = "judging"
    finished = "finished"


class SubmissionStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    checking = "checking"
    checked = "checked"


class CheckType(StrEnum):
    code = "code"
    documentation = "documentation"
    presentation = "presentation"
    screencast = "screencast"


class CheckStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class AlgoLanguage(StrEnum):
    python = "python"
    cpp = "cpp"
    java = "java"


class AlgoVerdict(StrEnum):
    pending = "pending"
    OK = "OK"
    WA = "WA"
    TL = "TL"
    ML = "ML"
    RE = "RE"
    CE = "CE"
