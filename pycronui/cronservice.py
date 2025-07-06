from crontab import CronTab
from croniter import croniter
from datetime import datetime
import getpass
from models import Job
import os

from utils import add_log_file, Command, Name, Schedule, delete_log_file
DEFAULT_CRON_FILE = "/etc/cron.d/e2scrub_all"


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            print(f"Instance of {cls.__name__} created for the first time.")
        else:
            print(f"Returning existing instance of {cls.__name__}.")
        return instances[cls]
    return get_instance

@singleton
class CronService:
    def __init__(self):
        self.filename = os.getenv("CRON_FILE", DEFAULT_CRON_FILE)
        self._crontab = CronTab(user=False)
        #self.jobs = []

    def add_cron_job(self, comm: Command, name: Name, sched: Schedule) -> None:
        if croniter.is_valid(sched):
            job = self._crontab.new(command=comm, comment=name, user="root")
            job.setall(sched)
            self._crontab.write(self.filename)
        else:
            raise ValueError("Invalid Cron Expression")

    def update_cron_job(self, comm: Command, name: Name, sched: Schedule, old_name: Name) -> None:
        self.delete_cron_job(old_name)
        self.add_cron_job(comm, name, sched)

    def delete_cron_job(self, name: Name) -> None:
        self._crontab.remove_all(comment=name)
        self._crontab.write(self.filename)

    def run_manually(self, name: Name) -> None:
        match = self._crontab.find_comment(name)
        job = list(match)[0]
        print(job)
        job.run()

    def get_next_schedule(self, name: Name) -> str:
        try:
            match = self._crontab.find_comment(name)
            job = list(match)[0]
            schedule = job.schedule(date_from=datetime.now())
            return schedule.get_next().strftime("%d/%m/%Y %H:%M:%S").replace("/", "-")
        except IndexError:
            return None

    def get_cron_jobs(self) -> list:
        jobs = []
        self._crontab.read(self.filename)
        for cron in self._crontab.crons:
            job = Job(
                command=cron.command,
                name=cron.comment,
                schedule=cron.slices,
            )
            jobs.append(job)
        return jobs

    def get_cron_job(self, name):
        jobs = self.get_cron_jobs()
        for job in jobs:
            if job.name == name:
                return job