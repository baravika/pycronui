from pydantic import BaseModel


class JobRequest(BaseModel):
    command: str
    name: str
    schedule: str


class Job:
    def __init__(self, command: str, name: str, schedule: str):
        self.command = command
        self.name = name
        self.schedule = schedule
        self.next_run = None
        self.status = None
        self.log = None
        self.is_active = False

    def __repr__(self):
        return f"<Job(name={self.name}, command={self.command}, schedule={self.schedule})>"