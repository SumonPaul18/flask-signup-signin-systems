# Error and Solutions on Signup/Signin System in Flask

### 1. Error: authlib.jose.errors.InvalidClaimError: invalid_claim: Invalid claim "iss"
#### Solution:
Remove the `openid` value from `scope` section.

From Line: ` client_kwargs={'scope': 'openid email profile'},`

Please remove the `openid` vaule from scope option.

Now, you try again and see the error have solved.

#
### 2. Error: RuntimeError: Missing "jwks_uri" in metadata for flask and Google authlib
#### Solution:
Please add bellow line in `oauth = oauth.register` section.
~~~
server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
~~~
Or
~~~
jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
~~~

#### Solution Code:
~~~
# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=client_id,
    client_secret=client_secret,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'email profile'},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)
~~~
Now, you try again and see the error have solved.

#
