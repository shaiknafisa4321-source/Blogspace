# BlogSpace – Blog Platform with Comments

##  Project Overview

BlogSpace is a beginner-friendly full-stack blogging platform developed using Python Flask, MySQL, HTML, and CSS.

It allows users to register, log in, create and manage blog posts, and interact with other users through comments.

The project also provides REST API endpoints to perform CRUD operations on blog posts and manage comments.

## Features

### User Management
- User registration
- User login and logout
- Secure password hashing
- Session-based authentication

### Blog Management
- Create new blog posts
- View published posts
- Edit existing posts
- Delete posts

### Comment Management
- Add comments to blog posts
- View comments associated with a post

### REST API
- Retrieve all blog posts
- Retrieve a single blog post
- Create a blog post
- Update a blog post
- Delete a blog post
- Retrieve comments
- Add comments

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| MySQL | Database management |
| HTML | Website structure |
| CSS | Website styling |
| Postman | API testing |
| Werkzeug | Password hashing |

## Project Structure

```text
blogspace/
│
├── app.py
├── database.sql
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── create.html
│   ├── edit.html
│   └── post.html
│
└── static/
    └── style.css
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/BlogSpace-Blogging-Platform.git
```

### 2. Open the Project Folder

```bash
cd BlogSpace-Blogging-Platform
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up the MySQL Database

Open MySQL Command Line and execute the SQL commands in `database.sql`.

This creates the `blogspace` database and the following tables:

- users
- posts
- comments

### 6. Configure Environment Variables

Set your MySQL password and Flask secret key in PowerShell:

```powershell
$env:DB_PASSWORD="your_mysql_password"
$env:SECRET_KEY="your_random_secret_key"
```

Replace the example values with your own credentials.

**Important:** Never upload your actual database password or secret key to GitHub.

### 7. Run the Application

```bash
python app.py
```

Open your browser and visit:

http://127.0.0.1:5000

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts` | Get all posts |
| GET | `/api/posts/<post_id>` | Get a single post |
| POST | `/api/posts` | Create a post |
| PUT | `/api/posts/<post_id>` | Update a post |
| DELETE | `/api/posts/<post_id>` | Delete a post |
| GET | `/api/posts/<post_id>/comments` | Get post comments |
| POST | `/api/posts/<post_id>/comments` | Add a comment |

Protected API endpoints require an authenticated session.

## API Testing

Postman was used to test the REST API endpoints, including GET, POST, PUT, and DELETE requests.

## Project Objectives

- Understand full-stack web development.
- Learn Flask application development.
- Connect a Python application with MySQL.
- Implement user authentication.
- Perform CRUD operations.
- Develop and test REST APIs.
- Understand the interaction between frontend and backend technologies.

## Author

Developed as part of a Full Stack Development Internship project 

## License

This project is developed for educational and internship purposes.
