from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
    expose_headers=["*"],
)

Data_File = Path(__file__).parent / "q-vercel-latency.json"
df=pd.read_json(Data_File)

@app.get("/")
async def root():
    return {"message": "Vercel Latency Analytics API is running."}  

@app.post("/api/")
async def get_latency_stats(request: Request):
    payload = await request.json()
    region_to_process = payload.get("regions",[])
    threshold = payload.get("threshold_ms",200)

    result = []
    for region in region_to_process:
        region_df = df[df['regions'] == region]
        if region_df.empty:
            avg_latency = round(region_df['latency_ms'].mean(), 2)
            p95_latency = round(np.percentile(region_df['latency_ms'], 95), 2)
            avg_uptime = round(region_df['uptime_pct'].mean(), 2)
            breaches = int(region_df[region_df['latency_ms'] > threshold].shape[0])

            result.append({
                "regions": region,
                "average_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            })

    return {"regions": result}
