# FluxKart-Customer-Affiliation

This is a web service hosted on Render that receives HTTP POST requests in the following format:
```json
{
	"email": string,
	"phoneNumber": number
}

The API connects to a MySQL database hosted on Aiven, which has the database Fluxkart with a column Contact:
The table has the following properties:
```json
{
	id                   Int                   
  phoneNumber          String
  email                String
  linkedId             Int 
  linkPrecedence       "secondary"|"primary"
  createdAt            DateTime              
  updatedAt            DateTime             
  deletedAt            DateTime
}
```

The purpose of the API is to process the request as a user who has placed an order. It checks the database for existing records with the same details and accordingly matches the details to track the customers who use slightly different credentials (e.g. same phone number but different email or vice versa).

Example:-
Database state:
```json
{
	id                   1                   
  phoneNumber          "123456"
  email                "lorraine@hillvalley.edu"
  linkedId             null
  linkPrecedence       "primary"
  createdAt            2023-04-01 00:00:00.374+00              
  updatedAt            2023-04-01 00:00:00.374+00              
  deletedAt            null
},
{
	id                   23                   
  phoneNumber          "123456"
  email                "mcfly@hillvalley.edu"
  linkedId             1
  linkPrecedence       "secondary"
  createdAt            2023-04-20 05:30:00.11+00              
  updatedAt            2023-04-20 05:30:00.11+00              
  deletedAt            null
}
```

POST request at /identify endpoint
```json
{
	"email": "2015wassupposedtohaveflyingcars@futureemail.com",
	"phoneNumber": "123456"
}
```

API Response
```json
{
		"contact":{
			"primaryContatctId": 1,
			"emails": ["lorraine@hillvalley.edu", "mcfly@hillvalley.edu", "2015wassupposedtohaveflyingcars@futureemail.com"\]
			"phoneNumbers": ["123456"\]
			"secondaryContactIds": [23,24\]
		}
}
```

Please note: If the phone number of the primary contact is not mentioned, it is returned as an empty string ("")
