from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

import os

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
}

@app.route('/identify', methods=['POST'])
def identify():
    print(os.getenv('DB_HOST'),
    os.getenv('DB_USER'),
    os.getenv('DB_PASSWORD'),
    os.getenv('DB_NAME'),
    int(os.getenv('DB_PORT')))

    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')

    if not email and not phone_number:
        return jsonify({"error": "At least email or phoneNumber is required"}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Get all matching contacts by email or phoneNumber
        cursor.execute("""
            SELECT * FROM Contact
            WHERE email = %s OR phoneNumber = %s   
        """, (email, phone_number))  #This is parameterized to only take the input as a string in order to prevent SQL injection attacks
        matches = cursor.fetchall()
        
        for contact in matches:
            if contact['email'] == email and contact['phoneNumber'] == phone_number:  # Checking for a match in both email and phone number
                return format_response(contact['id'], matches)
            
        if matches:  #Case where either the email or phone number matches 
            # Look for the primary contact
            cursor.execute("SELECT * FROM Contact")
            database = cursor.fetchall()
            #Searching for a primary contact with either the same email or the same phone number
            primary_contact = min(database, key=lambda v: v['createdAt'] if v['linkPrecedence'] == 'primary' 
                                  and (v['email']==contact['email'] or v['phoneNumber']==contact['phoneNumber'])else datetime.max)
            primary_id = primary_contact['id'] if primary_contact['linkPrecedence'] == 'primary' else primary_contact['linkedId']

            # The request has to be treated as a new entry to the database
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO Contact (email, phoneNumber, linkedId, linkPrecedence, createdAt, updatedAt)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, phone_number, primary_id, 'secondary', now, now))
            connection.commit()

            # Re-fetch all related contacts
            cursor.execute("""
                SELECT * FROM Contact
                WHERE id = %s OR linkedId = %s
            """, (primary_id, primary_id))
            related_contacts = cursor.fetchall()

            return format_response(primary_id, related_contacts)

        # Case 3: No match — new contact, set as primary
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO Contact (email, phoneNumber, linkedId, linkPrecedence, createdAt, updatedAt)
            VALUES (%s, %s, NULL, %s, %s, %s)
        """, (email, phone_number, 'primary', now, now))
        connection.commit()

        new_id = cursor.lastrowid
        return format_response(new_id, [{
            'id': new_id,
            'email': email,
            'phoneNumber': phone_number,
            'linkedId': None,
            'linkPrecedence': 'primary',
            'createdAt': now,
            'updatedAt': now
        }])

    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

#Creating an array of all the affiliated emails, phone numbers and ID's 
def format_response(primary_id, database):
    emails = []
    phones = []
    secondary_ids = []
    primary_email = ''
    primary_phone = ''

    #Iterate through the database looking for all affiliated accounts and their details (e.g. emails, phone numbers, id's etc)
    for contact in database:
        if contact['email'] and contact['email'] not in emails:
            emails.append(contact['email'])
        if contact['phoneNumber'] and contact['phoneNumber'] not in phones:
            phones.append(contact['phoneNumber'])

        if contact['linkPrecedence'] == 'secondary':
            secondary_ids.append(contact['id'])
        elif contact['id'] == primary_id:
            primary_email = contact['email']
            primary_phone = contact['phoneNumber']

    # Putting the primary email or phone number first
    if primary_email in emails:
        emails.remove(primary_email)
    emails.insert(0, primary_email)

    if primary_phone in phones:
        phones.remove(primary_phone)
    phones.insert(0, primary_phone)

    return jsonify({
        "contact": {
            "primaryContatctId": primary_id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
