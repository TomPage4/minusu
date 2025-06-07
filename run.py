from app import create_app

# Create the Flask application using the factory
app = create_app()

if __name__ == '__main__':
    # Run in debug mode if DEBUG is True in config
    app.run(debug=app.config['DEBUG'])