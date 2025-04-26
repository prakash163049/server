from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from flask_mail import Mail,Message
# Disable Flask's CLI and dotenv loading
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Create Flask app
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME']= 'prakash160904@gmail.com'
app.config['MAIL_PASSWORD']= 'jzyd ixii ngaw dujc'
app.config['MAIL_DEFAULT_SENDER']= 'prakash160904@gmail.com'
mail = Mail(app)
# Enable CORS for all routes
CORS(app)


# MongoDB connection - hardcoded connection string
mongo_uri = 'mongodb+srv://prakash:prakash16@cluster-personel.pcshs.mongodb.net/portfolio_db'
print(f"Using MongoDB connection string: {mongo_uri}")

# Global variable to track if MongoDB is connected
mongodb_connected = False
mail = Mail(app)
try:
    # Try to connect to MongoDB Atlas
    print("Connecting to MongoDB...")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
    db = client['portfolio_db']
    contacts_collection = db['contacts']
    mongodb_connected = True
except Exception as e:
    print(f"MongoDB connection error: {e}")
    print("WARNING: Application will run but contact form will not work!")

@app.route('/api/contact', methods=['POST'])
def contact():
    if not mongodb_connected:
        return jsonify({'error': 'Database connection is not available'}), 503
        
    try:
        # Print request data for debugging
        print("Received contact form submission")
        data = request.json
        print(f"Request data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create contact document
        contact_data = {
            'name': data['name'],
            'email': data['email'],
            'message': data['message'],
            'created_at': datetime.utcnow()
        }
        print(f"Contact data to be inserted: {contact_data}")
        msg = Message('Notification', recipients=['prakashsarvaiya1609@gmail.com'], body=f"{contact_data}This is data from user they will try to connect with you")
        mail.send(msg)
        # Insert into MongoDB
        try:
            result = contacts_collection.insert_one(contact_data)
            if result.inserted_id:
                print(f"Successfully inserted document with ID: {result.inserted_id}")
                return jsonify({
                    'message': 'Message sent successfully',
                    'id': str(result.inserted_id)
                }), 201
            else:
                print("Failed to insert document")
                return jsonify({'error': 'Failed to send message'}), 500
        except Exception as db_error:
            print(f"Database error: {db_error}")
            return jsonify({'error': 'Database error: Could not save your message'}), 500
            
    except Exception as e:
        print(f"Error in contact endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# Add a test endpoint to verify the API is working
@app.route('/api/test', methods=['GET'])
def test():
    status = {
        'message': 'API is working!',
        'mongodb_connected': mongodb_connected
    }
    return jsonify(status), 200

# Run the app directly without using Flask CLI
if __name__ == '__main__':
    print(f"Starting Flask server on port 5000...")
    # Use the werkzeug server directly instead of Flask's run method
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_debugger=True, use_reloader=True) 