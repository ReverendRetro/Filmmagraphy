# Filmmagraphy

Filmmagraphy is a self-hosted web application for cataloging your personal movie collection. Think of it as Discogs, but for your physical and digital movie library. It allows multiple users to securely manage their own private collections, with an admin account for overall site management.
Features

## The first account created will be the admin account

- User Accounts: Secure, password-protected accounts. Each user's collection is completely private.

- Admin Role: The first user to register automatically becomes the admin, with the ability to manage other users and the site database.

- Movie Logging: Easily add movies to your collection with details like format (Blu-ray, 4K UHD, etc.), media condition, and barcode (UPC).

- Search, Sort, and Filter:

- Instantly search your collection by title.

- Sort your movies by title or date added.

- Filter your view to show only specific formats.

### Admin Dashboard:

- User Management: Admins can reset the passwords of any user.

- Database Backup: Admins can export the entire site database for safekeeping and import a backup file to restore the site.

## Installation and Setup

Follow these steps to get Filmmagraphy running on your local machine or server.

1. Prerequisites

You must have Python 3 installed on your system.

2. Create Project Files

Create a new folder for your project. Inside that folder, create two files:

```
app.py
```

Download the app.py or copy the contents into this file

```
requirements.txt
```

Copy the following lines into this file. It lists the necessary Python libraries for the project.

```
Flask
Flask-SQLAlchemy
Werkzeug
```

3. Set Up a Virtual Environment

Open your terminal or command prompt and navigate into your project folder.

Create the virtual environment (we'll call it venv):

On macOS/Linux: `python3 -m venv venv`

On Windows: `python -m venv venv`

Activate the environment:

On macOS/Linux: `source venv/bin/activate`

On Windows: `.\venv\Scripts\activate`

Your terminal prompt should now start with (venv), indicating the environment is active.

4. Install Dependencies

With the virtual environment active, run the following command to install the required libraries:
```
pip install -r requirements.txt
```
5. Run the Application

Make sure you are in your project directory and your (venv) is active.

Run the application with this command:
```
python3 app.py
```
The terminal will show output indicating the server is running, similar to this:

* Running on http://0.0.0.0:5002/

Open your web browser and navigate to your server's IP address on port 5002. If you're running it on the same machine, you can use: http://127.0.0.1:5002

The first time you run the app, it will automatically create a movies.db file in your project folder. This is your database.

## Important Note on Database Changes

This application uses SQLAlchemy to manage the database schema based on the models defined in the code. If you modify the database models in app.py (e.g., add a new column to the Movie table), the existing movies.db file will be outdated and will cause an error.

To fix this, you must:

Stop the application (Ctrl+C in the terminal).

Delete the movies.db file.

Restart the application (python app.py).

A new, empty database with the correct structure will be created.
