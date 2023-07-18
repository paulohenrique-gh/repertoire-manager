# Repertoire Manager

Manage musical repertoire by adding pieces to a database.

Get recomendations for when to play pieces in your repertoire in order to improve memorization.

Video Demo: https://youtu.be/u_XZbLFKVB0

## Technologies

- HTML
- CSS - Bootstrap
- Python / Flask
- MySQL


## Features:

- Registration and login
- Add musical pieces that you study to a collection
- Add pieces from your collection to your repertoire
- Every piece has a details page
- Edit details
- In the details page, if a piece is in your repertoire, there's a list of dates on which you should play it again in order to help with memorization
- You can reset the rotation of repetitions any time
- In the calendar page, you can search by range, and get a list of pieces to play by date


## Files:

- **requirements.txt**: modules required to run the application
- **create_db_tables.sql**: SQL queries for creating the database and tables in MySQL
- **app.py**: the main file in Python. Contains logic for the backend of the application, such as validating forms, doing operations with data from database queries, etc.
- **queries.py**: functions for database queries
- **helpers.py**: additional helping functions
- **static/**: folder for static favicon and stylesheets files:
    - **favicon.png**: simple favicon for the app
    - **styles.css**: additional styles. The main styling comes from bootstrap classes
- **templates/**: contains the templates for html pages:
    - **layout.html**: main layout page that all other pages extend
    - **signup.html**: registration page
    - **login.html**: login page
    - **index.html**: first page after logging in. Displays five latest entries to the collection, with a link to display all of them.
    - **index_all.html**: renders all the entries in the user's collection
    - **add_piece.html**: form for adding a new piece. The fields are: Title, Opus, Number, Movement, Composer, Period, Start date, Finish date, Instrument, Difficulty level, Add to repertoire
    - **details.html**: page for details of the piece. Renders a list of dates on which to play the piece next
    - **edit.html**: form for editing the details of a piece in your collection 
    - **repertoire.html**: similar to the index page, but loads only the pieces for which the user marked the option "Add to repertoire". Each piece in this page has a button to reset the repetition rotation
    - **calendar.html**: allows searching for a date range
    - **calendar_search.html**: returns the result of the date range search


## Some things this project has helped me practice:

- Python in general
- Validating data from HTML forms
- Creating routes in flask
- GET and POST request methods
- Creating database and tables
- Primary and foreign keys in SQL
- Querying the database for a specific piece of information


## Todo

- [ ] Fix bug that doesn't show next date in repertoire page
- [ ] Add to details page that redirects to Google or YouTube search of that piece  
- [ ] Fix string capitalization on index page
- [ ] Add page for searching with parameters (author, title, date, etc.)
- [ ] Add sorting to index and repertoire
- [ ] Password change
- [ ] A better way to render the list of dates in the details page
- [ ] Add button to reset the rotation in the details page
- [ ] Improvements to the UI
- [ ] Cloud database
- [ ] Deploy the application
- [ ] Review code to make it more efficient




