from flask import Flask
from routes.app_routes import tastenest  # Import the blueprint

app = Flask(__name__, template_folder="templates")

app.secret_key = 'your_secret_key'

# Config for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.secret_key = "your_secret_key"  # Set a secret key for flash messages

# Register the blueprint
app.register_blueprint(tastenest)


if __name__ == '__main__':
    app.run(debug=True)
