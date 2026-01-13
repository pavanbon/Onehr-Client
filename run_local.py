import uvicorn
from lambda_function import app

if __name__ == "__main__":
    print("Starting OneHR 2.0 API on Localhost...")
    print("Swagger UI available at: http://127.0.0.1:8000/docs")
    # Using reload=True so it automatically restarts when you change code
    uvicorn.run("lambda_function:app", host="127.0.0.1", port=8000, reload=True)
