# address_book_app_fastapi
Address book application where API users can create, update and delete addresses

# prerequisites
1. python -m venv venv
2. source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. pip install -r requirements.txt

**Command to run**
# To have the termainal keep it reloading when changes made in script
uvicorn main:app --reload  

**Note:**
1. Used "Type Annotations" for better debug and development.
2. used docstrings and comments wherever required.
3. ORM is utilised to query the DB for information required.
4. Built-in FastAPI’s Swagger Doc is used for API Documentation
5. Sample Data in JSON format is provided for better understanding.

