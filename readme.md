# Gusto API Microservice
This microservice interacts with the Gusto API, 
## Getting Started
Initially, a secret needs to be stored in AWS Secrets Manager, as plain text json, with the following format and values:
```
{
  "client_id": "your client id",
  "client_secret": "your client secret",
  "redirect_uri": "percent-encoded url you submitted when signing up > for the Gusto API. Should the user accept
  integration, the user will be returned to this url with the code parameter set to the authorization > code."
}
```
________________
## Authentication
Gusto outlines the authentication flow the following way:
* Direct user to authorize
* User authorizes application to access their information
* User redirected to partner site with authorization code
* Exchange authorization code for access/refresh token pair
* Make requests, always including the access token parameter
* Exchange refresh token for new access/refresh tokens

**There are two parts to authenticating with the Gusto API that involve user input:**
1) Call the GET `initial_auth` function and collect the authorization code from the redirect_uri
Once user authorizes the application to access their information. An example url and code is below.
    * https://example.com/callback?code=51d5d63ae28783aecd59e7834be2c637a9ee260f241b191565aa10fe380471db
    * The code needs to be saved in the same secret as before,
    i.e. **'code': '51d5d63ae28783aecd59e7834be2c637a9ee260f241b191565aa10fe380471db'**
2) Make an initial API call within 10 minutes or the authorization code will expire and the process above
will need to be repeated. Access and refresh tokens will be securely saved in AWS Secrets Manager for future use.

________________
## Functions / API Calls
### POST `create_company`
The `create_company` function will, per the Gusto docs:
* Create a new company in Gusto.
* Create a new user in Gusto.
* Make the new user the primary payroll administrator of the new company.
* Send a welcome email to the new user.
The function will return an account claim url from Gusto, which allows a user to complete their account
setup inside of Gusto.

USE CASE--ONLY CERTAIN PARAMETERS SO FAR.
The following is the minimum accepted payload that can be used to create a company. For more fields please see Gusto's
docs.
```
{
  "first_name": "user's first name",
  "last_name": "user's last name",
  "email": "user's email",
  "company_name": "name of user's company"
}
```
### POST `payrolls`
Calling the `payrolls` endpoint will store three json objects in an S3 bucket created upon initial deployment. The three
json files returned are as follows:
- A replica of the entire output from calling the Gusto payrolls endpoint
- A file containing **only** employee compensation information
- A file containing **only** the other payroll details not associated with employee compensation

This endpoint returns all payrolls for a specific company, current and past.

**Pass in the `company_id` in raw json as shown below:**
```
{
 "company_id": "company id"
}
```

-------------------------------------------------
# EXTRA STUFF
### POST `companies`
If you do not know the company id for the company you'd like to fetch payrolls for, call the `companies` route, which
lists all companies and their information, including ids.

You can also obtain all company details about a specific company associated with your account by calling passing in the
company id as raw json, shown below:
```
{
 "company_id": "company id"
}
```

## MAYBE COMPANIES NEEDS TO BE POST?