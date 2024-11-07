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
Now, you try again and see the error have solved.

#
