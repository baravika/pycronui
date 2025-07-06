from crontab import CronTab
from croniter import croniter
from datetime import datetime
import getpass
from models import Job

from utils import add_log_file, Command, Name, Schedule, delete_log_file

_user = getpass.getuser()

_cron = CronTab(user=False)


def add_cron_job(comm: Command, name: Name, sched: Schedule) -> None:
    if croniter.is_valid(sched):
        job = _cron.new(command=comm, comment=name, user="root")
        job.setall(sched)
        _cron.write(filename="/etc/cron.d/e2scrub_all")
    else:
        raise ValueError("Invalid Cron Expression")


def update_cron_job(comm: Command, name: Name, sched: Schedule, old_name: Name) -> None:
    match = _cron.find_comment(old_name)
    job = list(match)[0]
    job.setall(sched)
    job.set_command(add_log_file(comm, name))
    job.set_comment(name)
    _cron.write()


def delete_cron_job(name: Name) -> None:
    _cron.remove_all(comment=name)
    _cron.write()
    delete_log_file(name)


def run_manually(name: Name) -> None:
    match = _cron.find_comment(name)
    job = list(match)[0]
    job.run()


def get_next_schedule(name: Name) -> str:
    try:
        match = _cron.find_comment(name)
        print(match)
        job = list(match)[0]
        schedule = job.schedule(date_from=datetime.now())
        return schedule.get_next().strftime("%d/%m/%Y %H:%M:%S").replace("/", "-")
    except IndexError:
        return None


def get_cron_jobs() -> list:
    jobs = []
    _cron.read("/etc/cron.d/e2scrub_all")
    for cron in _cron.crons:
        job = Job(
            command=cron.command,
            name=cron.comment,
            schedule=cron.slices,
        )
        jobs.append(job)
    print(jobs)
    return jobs
