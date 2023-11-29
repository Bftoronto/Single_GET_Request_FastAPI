**This is API with a single GET request that returns True/False information.**

1. Install the required dependencies:

**pip install fastapi pydantic sqlalchemy**

2. Run the FastAPI app using Uvicorn:

**uvicorn main:app --workers 10 --reload**

This will start the FastAPI app with 10 Docker workers and automatic reloading enabled.

3. Now, you can make a GET request to **http://localhost:8000/check_request_status** to check the availabillity of the third-party API.
The response will contain the **can_make_request** field, which will be **True** or **False** depending on the current status.
