from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, Body, Request
import os
from celery_worker import add, compute_accuracy, celery_app
from celery.result import AsyncResult
import asyncio

app = FastAPI()

@app.get("/process")
async def process_endpoint(a: int, b: int):
    result = add.delay(a, b)
    return {"task_id": result.id}

@app.post("/compute_accuracy")
async def compute_accuracy_endpoint(request: Request):
    """
    This endpoint supports two types of requests:
      - multipart/form-data with a file upload (key: "file")
      - JSON payload with a "csv_path" field

    Debug statements have been added to help trace the received CSV path
    and verify if the file exists on disk.
    """
    content_type = request.headers.get("Content-Type", "")
    print(f"DEBUG: Received Content-Type: {content_type}")
    
    if "multipart/form-data" in content_type:
        # Handle file upload
        form = await request.form()
        file = form.get("file")
        if not file:
            raise HTTPException(status_code=422, detail="File not provided.")
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        path_to_use = file_location
        print(f"DEBUG: File uploaded. Saved to: {path_to_use}")
    elif "application/json" in content_type:
        # Handle JSON payload
        body = await request.json()
        csv_path = body.get("csv_path")
        if not csv_path:
            raise HTTPException(status_code=422, detail="CSV path not provided.")
        # Convert backslashes to forward slashes and prepend "../"
        converted_path = csv_path.replace("\\", "/")
        path_to_use =  converted_path
        print(f"DEBUG: JSON payload received. csv_path: {csv_path}")
        print(f"DEBUG: Converted and adjusted path: {path_to_use}")
    else:
        raise HTTPException(status_code=415, detail="Unsupported content type.")

    # Check if the file exists at the resolved path
    if os.path.exists(path_to_use):
        print(f"DEBUG: File exists at path: {path_to_use}")
    else:
        print(f"DEBUG: File NOT found at path: {path_to_use}")

    # Trigger the compute_accuracy task with the resolved path.
    result = compute_accuracy.delay(path_to_use)
    return {"task_id": result.id}


@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    # Retrieve the task result using the Celery AsyncResult.
    result = AsyncResult(task_id, app=celery_app)

    while True:
        if result.ready():
            break
        await websocket.send_text(result.state)
        await asyncio.sleep(1)

    # Once the task is complete, send the final result.
    if result.successful():
        await websocket.send_text(str(result.state))
        await websocket.send_text(str(result.result))
        await websocket.close()
    else:
        await websocket.send_text(result.state)

@app.get("/task_result/{task_id}")
async def task_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if not result.ready():
        return {"status": result.state, "result": None}
    if result.successful():
        return {"status": result.state, "result": result.result}
    else:
        return {"status": result.state, "error": "Task failed"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
