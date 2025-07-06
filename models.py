

# class Job(Base):
#     __tablename__ = "jobs"
#
#     id = Column(Integer, primary_key=True, index=True)
#     command = Column(String, index=True)
#     name = Column(String, unique=True)
#     schedule = Column(String)
#     next_run = Column(String, default=None)
#     status = Column(String, default=None)
#     log = Column(String, default=None)
#     is_active = Column(Boolean, default=False)



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