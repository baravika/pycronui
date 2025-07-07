from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import models
from cronservice import CronService
from models import Job, JobRequest
from utils import watch_status, load_logs

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_cron_service():
    return CronService()


def update_displayed_schedule(cronservice) -> None:
    jobs = cronservice.get_cron_jobs()

    for job in jobs:
        job.next_run = cronservice.get_next_schedule(job.name)
        job.status = watch_status(job.name)

    return jobs


@app.get("/")
async def home(request: Request, cronservice: CronService = Depends(get_cron_service)):
    jobs = update_displayed_schedule(cronservice)
    output = {"request": request, "jobs": jobs}
    return templates.TemplateResponse("home.html", output)


@app.get("/jobs/{job_name}")
async def get_jobs(job_name: str, request: Request, cronservice: CronService = Depends(get_cron_service)):
    job_update = cronservice.get_cron_job(job_name)
    output = {"request": request, "job_update": job_update}
    return templates.TemplateResponse("jobs.html", output)


@app.get("/logs/{job_id}")
async def get_logs(job_name, request: Request):
    update_log = {"log": load_logs(job_name)}
    job.update(update_log)
    output = {"request": request, "job": update_log}
    return templates.TemplateResponse("logs.html", output)


@app.post("/create_job/")
async def create_job(job_request: JobRequest, cronservice: CronService = Depends(get_cron_service)):
    try:
        cronservice.add_cron_job(job_request.command, job_request.name, job_request.schedule, job_request.user)
        job.next_run = cronservice.get_next_schedule(job.name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid Cron Expression")
    return job_request


@app.put("/update_job/{job_name}/")
async def update_job(job_name: str, job_request: JobRequest, cronservice: CronService = Depends(get_cron_service)):
    cronservice.update_cron_job(
        job_request.command,
        job_request.name,
        job_request.schedule,
        job_name,
        job_request.user
    )
    return {"msg": "Successfully updated data."}


@app.get("/run_job/{job_name}/")
async def run_job(job_name, cronservice: CronService = Depends(get_cron_service)):
    cronservice.run_manually(job_name)
    return {"msg": "Successfully run job."}


@app.delete("/job/{job_name}/")
async def delete_job(job_name: str, cronservice: CronService = Depends(get_cron_service)):
    cronservice.delete_cron_job(job_name)
    return {"INFO": f"Deleted {job_id} Successfully"}
