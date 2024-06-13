import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, redirect, url_for, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required, allowed_file
from datetime import datetime


db = SQL("sqlite:///test.db")
UPLOAD_FOLDER = '/static'

# Configure application
app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = 'static'

current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")



@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")



# Context processor
@app.context_processor
def inject_profile_picture():
    # Retrieve the profile picture for the logged-in user, if available
    if 'id' in session:
        user_id = session['id']
        result = db.execute("SELECT profile_picture FROM profile_picture WHERE id = ?", user_id)
        row = result[0] if len(result) > 0 else None
        if row:
            profile_picture = row['profile_picture']
        else:
            profile_picture = None
    else:
        profile_picture = None

    # Return the profile_picture variable to be available in all templates
    return dict(profile_picture=profile_picture)




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Error messages
        if not username:
            flash("Username Required")

        elif not password:
            flash("Password Required")

        elif not confirmation:
            flash("Confirmation Required")

        elif password != confirmation:
            flash("Passwords do not match")

        else:
            # Function that checks if the user already exists
            user_exists = db.execute("SELECT id FROM users WHERE username = ?", username)
            if (user_exists):
                flash("Username is already taken")
            else:
                # Generate password hash
                hash = generate_password_hash(password)
                new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
                session["id"] = new_user
                flash("Succesfully Registered!")
                return render_template("profile.html")

        return redirect("/#login-form-homepage")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Redirect when already logged in
    if session.get('id') is not None:
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        # Error messages
        if not username:
            flash("Username Required")
        elif not password:
            flash("Password Required")
        else:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", username)
            # Ensure username exists and password is correct
            if len(rows) == 0:
                flash("Invalid username and/or password")
            elif not check_password_hash(rows[0]["hash"], password):
                flash("Invalid username and/or password")
            else:
                # Remember which user has logged in
                session["id"] = rows[0]["id"]
                user_id = session['id']
                user_albums = db.execute("SELECT * FROM user_albums WHERE user_id = ?", user_id)

                # Retrieve the first image for each album
                album_images = []
                for album in user_albums:
                    result = db.execute("SELECT filename FROM user_images WHERE album_id = ? LIMIT 1", album['id'])
                    if result:
                        album_images.append(result[0]['filename'])
                    else:
                        album_images.append(None)

                # Get the amount of images for each collection
                for album in user_albums:
                    amount = db.execute("SELECT COUNT(*) FROM user_images WHERE album_id = ?", (album['id'],))
                    image_count = amount[0]['COUNT(*)'] if amount else 0
                    album['image_count'] = image_count

                # Render the template with the updated user_albums
                return render_template("profile.html", collection=user_albums, album_images=album_images)

        return redirect("/login")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=['GET'])
@login_required
def profile():

    user_id = session['id']
    user_albums = db.execute("SELECT * FROM user_albums WHERE user_id = ?", user_id)

    # Retrieve the first image for each album
    album_images = []
    for album in user_albums:
        result = db.execute("SELECT filename FROM user_images WHERE album_id = ? LIMIT 1", album['id'])
        if result:
            album_images.append(result[0]['filename'])
        else:
            album_images.append(None)

    # Get the amount of images for each collection
    for album in user_albums:
        amount = db.execute("SELECT COUNT(*) FROM user_images WHERE album_id = ?", (album['id'],))
        image_count = amount[0]['COUNT(*)'] if amount else 0
        album['image_count'] = image_count

    # Render the template with the updated user_albums
    return render_template("profile.html", collection=user_albums, album_images=album_images)



@app.route("/settings", methods=["GET", "POST"])
def settings():
    user_id = session['id']

    if request.method == 'POST':
        # check if the post request has the file part
        if 'profile_picture' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['profile_picture']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Generate a new filename with the user ID (to prevent duplicate filenames)
            filename = secure_filename(f"{user_id}_{file.filename}")

            # Save the file to the appropriate location
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploads', filename))

            # Check if the user already has a profile picture in the database
            result = db.execute("SELECT profile_picture FROM profile_picture WHERE id = ?", user_id)
            if result:
                # Update the user's profile picture in the database
                db.execute("UPDATE profile_picture SET profile_picture = ? WHERE id = ?", filename, user_id)
            else:
                # Add a new row for the user in the database with the profile picture
                db.execute("INSERT INTO profile_picture (id, profile_picture) VALUES (?, ?)", user_id, filename)

            flash("Upload successful!")
            return redirect(url_for('settings'))

    if 'id' in session:
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]['username']
        return render_template("settings.html", username=username)
    else:
        return redirect(url_for('login'))


@app.route("/new_collection", methods=["GET", "POST"])
def upload_files():
    if request.method == 'GET':
        return render_template("new_collection.html")
    else:
        title = request.form.get('title')
        # check if the collection has a title
        if not title:
            flash('Missing title')
            return redirect(request.url)

        # Get the form data
        description = request.form['description']
        user_id = session['id']

        # Insert form data into the database table user_albums
        db.execute("INSERT INTO user_albums (user_id, title, description, created_at) VALUES (?, ?, ?, ?)",
                   user_id, title, description, datetime.now())

        # Retrieve the album_id using db.execute() and indexing
        result = db.execute("SELECT id FROM user_albums ORDER BY id DESC LIMIT 1")
        # Retrieve the first dictionary from the list
        album_dict = result[0]
        # Retrieve the album_id value from the dictionary
        album_id = album_dict['id']
        # Convert the album_id to an integer
        album_id = int(album_id)

        # Get the uploaded files, titles, and descriptions
        image_files = request.files.getlist('image_files[]')
        image_titles = request.form.getlist('image_titles[]')
        image_descriptions = request.form.getlist('image_descriptions[]')

        # Iterate over the uploaded files and save them
        for file, title, description in zip(image_files, image_titles, image_descriptions):
            if file.filename != '':
                user_id = session["id"]
                # Generate a new filename with the user ID (to prevent duplicate filenames)
                filename = secure_filename(f"{user_id}_{file.filename}")

                # Save the file to the appropriate location
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploads', filename))

                # Save the filename and other details to the database
                # Insert image information into user_images table
                db.execute("INSERT INTO user_images (album_id, filename, description, created_at, title) VALUES (?, ?, ?, ?, ?)",
                            album_id, filename, description, datetime.now(), title)

        # Redirect or render a success message after processing all the uploaded files
        flash("New collection created successfully!")
        return redirect(url_for("profile"))




@app.route("/download_file/<name>")
def download_file(name):
    # Implement the logic to handle file download
    # You can use the 'name' parameter to retrieve the file from the 'UPLOAD_FOLDER' directory
    # and return it as a response or redirect to the file

    # Example implementation:
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploads', name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found")
        return redirect(url_for('settings'))


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user's password"""
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        user_id = session["id"]
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Handle error messages for invalid inputs
        if not current_password or not new_password or not confirm_password:
            flash("All fields must be filled")

        # Retrieve the current user's information from the database
        user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)

        # Check if the current password provided matches the user's actual password
        if not check_password_hash(user[0]["hash"], current_password):
            flash("Current password is incorrect")

        # Check if new password has some number of letters, numbers, and/or symbols and password length
        #if len(new_password) < 8:
        #    return apology("Password must be at least 8 characters long")

        #if not re.search(r"[0-9]", new_password):
        #    return apology("Password must contain at least one digit")

        #if not re.search(r"[A-Z]", new_password):
        #    return apology("Password must contain at least one capital letter")

        #if not re.search(r"\W", new_password):
        #    return apology("Password must contain at least one special character")

        # Check if the new password and confirm_password match
        if new_password != confirm_password:
            flash("Passwords do not match")

        # Generate password hash for the new password
        new_hash = generate_password_hash(new_password)

        # Update the user's password in the database
        db.execute("UPDATE users SET hash = :new_hash WHERE id = :id", new_hash=new_hash, id=user_id)

        flash("Password Change Successful!")
        username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]['username']
        return render_template("settings.html", username=username)


@app.route('/view-collection/<int:collection_id>')
@login_required
def view_collection(collection_id):
    # Retrieve the collection from the database
    collection = get_collection(collection_id)

    # Check if the collection exists
    if collection is None:
        flash("Collection not found.")
        return redirect(url_for("profile"))

    # Retrieve the images for the collection
    album_images = get_images(collection_id)

    title = db.execute('SELECT title FROM user_albums WHERE id = ?', (collection_id))[0]['title']
    description = db.execute('SELECT description FROM user_albums WHERE id = ?', (collection_id))[0]['description']


    # Render the view-collection.html template with the collection and images
    return render_template("view-collection.html", collection=collection, images=album_images, description=description, name=title)


def get_collection(collection_id):
    # Get the album from the database
    collection = db.execute('SELECT * FROM user_albums WHERE id = ?', (collection_id,))
    return collection


def get_images(collection_id):
    # Retrieve the images for the collection
    album_images = []
    results = db.execute("SELECT * FROM user_images WHERE album_id = ?", (collection_id,))
    for result in results:
        album_images.append(result)

    return album_images


@app.route('/delete-collection/<int:collection_id>', methods=['GET', 'POST'])
@login_required
def delete_collection(collection_id):
    # Delete the images associated with the collection
    db.execute('DELETE FROM user_images WHERE album_id = ?', (collection_id,))

    # Delete the collection from the database
    db.execute('DELETE FROM user_albums WHERE id = ?', (collection_id,))

    flash("Collection deleted successfully.")
    return redirect(url_for("profile"))



@app.route('/edit-collection/<int:collection_id>', methods=['GET', 'POST'])
@login_required
def edit_collection(collection_id):
    if request.method == 'GET':
        return render_template("edit-collection.html", collection_id=collection_id)
    else:
        # Retrieve the new title and description from the form
        new_title = request.form.get('new_title')
        new_description = request.form.get('new_description')
        user_id = session["id"]


        # Update the collection information in the database
        db.execute("UPDATE user_albums SET title = :new_title, description = :new_description WHERE id = :collection_id AND user_id = :user_id",
           new_title=new_title, new_description=new_description, collection_id=collection_id, user_id=user_id)


        # Redirect to the collection view page
        flash('Collection information updated successfully!')
        return redirect(url_for('view_collection', collection_id=collection_id))




@app.route('/add-images/<int:collection_id>', methods=['GET', 'POST'])
@login_required
def add_images(collection_id):
    if request.method == 'GET':
        return render_template("add-images.html", collection_id=collection_id)
    else:
        # Get the uploaded files, titles, and descriptions
        image_files = request.files.getlist('image_files[]')
        image_titles = request.form.getlist('image_titles[]')
        image_descriptions = request.form.getlist('image_descriptions[]')

        # Iterate over the uploaded files and save them
        for file, title, description in zip(image_files, image_titles, image_descriptions):
            if file.filename != '':
                user_id = session["id"]
                # Generate a new filename with the user ID (to prevent duplicate filenames)
                filename = secure_filename(f"{user_id}_{file.filename}")

                # Save the file to the appropriate location
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploads', filename))

                # Save the filename and other details to the database
                # Insert image information into user_images table
                db.execute("INSERT INTO user_images (album_id, filename, description, created_at, title) VALUES (?, ?, ?, ?, ?)",
                            collection_id, filename, description, datetime.now(), title)

        flash('Image(s) added successfully!')
        return redirect(url_for('view_collection', collection_id=collection_id))


@app.route('/view-image/<int:image_id>')
def view_image(image_id):
    # Retrieve the image data from the database using the image_id
    image = db.execute("SELECT * FROM user_images WHERE id = ?", image_id)

    # Check if the image exists
    if image is None:
        flash('Image not found!')
        return redirect(url_for('/'))

    # Extract the filename from the image record
    filename = image[0]['filename']

    # Render the template with the image data
    return render_template('view-image.html', filename=filename, image=image, image_id=image_id)



@app.route('/delete-image/<int:image_id>', methods=['GET', 'POST'])
@login_required
def delete_image(image_id):
    collection_id = db.execute('SELECT album_id FROM user_images WHERE id = ?', image_id)
    collection_id = collection_id[0]['album_id']

    # Delete the image associated with the image id
    db.execute('DELETE FROM user_images WHERE id = ?', image_id)

    flash("Image deleted successfully.")
    return redirect(url_for("view_collection", collection_id=collection_id))


@app.route('/edit-image/<int:image_id>', methods=['GET', 'POST'])
@login_required
def edit_image(image_id):
    if request.method == 'GET':
        return render_template("edit-image.html", image_id=image_id)
    else:
        # Retrieve the new title and description from the form
        new_title = request.form.get('new_title')
        new_description = request.form.get('new_description')


        # Update the collection information in the database
        db.execute("UPDATE user_images SET title = :new_title, description = :new_description WHERE id = :image_id",
           new_title=new_title, new_description=new_description, image_id=image_id)



        # Redirect to the collection view page
        flash('Collection information updated successfully!')
        return redirect(url_for('view_image', image_id=image_id))

