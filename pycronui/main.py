from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import models
import cronservice
from models import Job, JobRequest
from utils import watch_status, load_logs

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def update_displayed_schedule() -> None:
    jobs = cronservice.get_cron_jobs()

    for job in jobs:
        job.next_run = cronservice.get_next_schedule(job.name)
        job.status = watch_status(job.name)

    return jobs


@app.get("/")
async def home(request: Request):
    jobs = update_displayed_schedule()
    output = {"request": request, "jobs": jobs}
    return templates.TemplateResponse("home.html", output)


@app.get("/jobs/{job_id}")
async def get_jobs(job_id: int, request: Request):
    job_update = db.query(Job).filter(Job.id == job_id).first()
    output = {"request": request, "job_update": job_update}
    return templates.TemplateResponse("jobs.html", output)


@app.get("/logs/{job_id}")
async def get_logs(job_name, request: Request):
    update_log = {"log": load_logs(job_name)}
    job.update(update_log)
    output = {"request": request, "job": update_log}
    return templates.TemplateResponse("logs.html", output)


@app.post("/create_job/")
async def create_job(job_request: JobRequest):
    print(job_request)
    try:
        cronservice.add_cron_job(job_request.command, job_request.name, job_request.schedule)
        job.next_run = cronservice.get_next_schedule(job.name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid Cron Expression")
    return job_request


@app.put("/update_job/{job_id}/")
async def update_job(job_id: int):
    existing_job = db.query(Job).filter(Job.id == job_id)
    cronservice.update_cron_job(
        job_request.command,
        job_request.name,
        job_request.schedule,
        existing_job.first().name,
    )
    existing_job.update(job_request.__dict__)
    existing_job.update({"next_run": cronservice.get_next_schedule(job_request.name)})
    db.commit()
    return {"msg": "Successfully updated data."}


@app.get("/run_job/{job_id}/")
async def run_job(job_name):
    cronservice.run_manually(job_name)
    return {"msg": "Successfully run job."}


@app.delete("/job/{job_id}/")
async def delete_job(job_id: int):
    cronservice.delete_cron_job(job_update.name)
    db.delete(job_update)
    db.commit()
    return {"INFO": f"Deleted {job_id} Successfully"}
