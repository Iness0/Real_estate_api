# Real_estate_api
API for managing real estate Sales

For security reasons change private and public keys in corespondent .pem files. You will need ES256 alg if u're willing to use this api. 
Same goes for secret key in .env/variable at your deployment
+ you will need to specify DATABASE_URL at the same place (or sqlite will be used by default)
Routes go as follow:

/api/customers
GET to get list of all customers
POST to create new one

/api/customers/id
GET to get customer with specified id
PUT to change customer's data / add as applicant to chosen house (for id)
DELETE to delete customer

/api/houses
GET to get all houses
POST to create new house

/api/houses/id
GET to get house with specified id
PUT to change house parameters / mark house as SOLD
DELETE to delete house

