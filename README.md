# Webapp

This is a Django based RESTful API for managing user data. It includes APIs for registration, login, and user details retrieval and update.


### Requirements
- Python 3.x
- Django 3.x
- Django REST framework
- 

### Installation
1. Clone the repository to your local machine and cd into webapp.
2. Create a virtual environment in the project directory.
3. Activate the virtual environment.
4. Install the required packages using the following command:
```bash
pip install -r requirements/local.txt
```
5. Export the database configurations to the environment. 
```bash
export DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```
> **_NOTE:_**  replace the POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB with your database configurations.

### Setting Up Your Users

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

### Run Django server
- Migrate all the migration files into the database.

      $ python manage.py migrate
- Run server

      $ python manage.py runserver

### Running tests with django

    $ python manage.py test

### Usage
The API has the following endpoints:

1. Register user: /v1/user/ (POST)
2. Login: /v1/user/login/ (POST)
3. User details: /v1/user/<user_id> (GET, PUT)
4. Health Check: /healthz (GET)
5. Product add: /v1/product/ (POST)
6. Product details: /v1/product/<product_id> (GET, PATCH, DELETE, PUT)

You can test the API using any REST client such as Postman.

### Note
The API uses basic authentication for accessing user details. A token is generated during login, which can be used to access the user details.

### License
This project is licensed under the MIT License.
