import pandas as pd

r1 = pd.read_csv("data/Resume.csv")
r2 = pd.read_csv("data/candidate_job_role_dataset.csv")
jobs = pd.read_csv("data/JobsDatasetProcessed.csv")
skills = pd.read_csv("data/data.csv")

print("Resume.csv:", r1.columns)
print("candidate_job_role_dataset:", r2.columns)
print("JobsDatasetProcessed:", jobs.columns)
print("data.csv:", skills.columns)