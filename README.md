# Owlin REST API

##### Table of contents
- [The URL Scheme](#url-scheme)
	- [Input / Sending data](#input—sending-data)
	- [Output / Receiving data](#output—receiving-data)
- [General definitions](#general_definitions)
	- [filter rule definitions](#filter_rules)
	- [stream_id definitions](#stream_id_definitions)
- [API Methods](#api_methods)
	- [get_articles](#get_articles)
	- [stats](#stats)
- [filter.get](#filterget)
- [filter.save](#filtersave)
- [invite.generate_token](#invitegenerate_token)
- [signup.token](#signuptoken)
- [signup](#signup)
- [password.update](#passwordupdate)
- [Undocumented Methods](#undocumented-methods)
	
======================

### URL Scheme
The request url of the Owlin API is constructed as follows,

#### Input / Sending data:
Both GET and POST are supported for the same type of requests. However, whenever an extra-parameter is longer than 1024 bytes, you should use POST headers.

##### For GET requests with e.g. 2 parameters:
``https://newsroom.owlin.com/api/v1/method/value?extra-parameter_1=extra-value_2&extra-parameter_2=extra-value_2``

##### For POST requests with e.g. 1 parameter: 
``https://newsroom.owlin.com/api/v1/method``
``value=value&extra-parameter=extra-value``

The value parameter is optional for most methods, both for POST and GET requests. Some methods however require a certain value to be set. 

##### Multi-dict parameters
When a method requires a dictionary as an extra-value, encode it as JSON and add two brackets behind [extra-parameter] i.e.
``https://newsroom.owlin.com/api/v1/method/value?extra-parameter[]=extra-value``

#### Output / Receiving data:
The API will always respond JSON.

##### JSONP Callbacks
To request a JSONP Callback from the API, to be used for instance in javascript, use ``?callback=callback_function_name``

**Output example:**
```javascript
typeof callback_function_name === 'function' && callback_function_name({ /* .. your data .. */ })
```

==============

### Authentication
Almost every request requires authentication. It is a two-step process. 

##### 1. Firstly, you request a secret_key. 
Each time you request a secret_key a new session is started. 
You request a secret_key using the method generate_secret. The method requires 2 parameters, ``email`` and ``password``. If you are using the newsroom, you can use the same credentials here. 

The required url is:
``https://newsroom.owlin.com/api/v1/generate_secret?email=email@example.com&password=password``

**Minimize the number of sessions! Generate the secret key only when necessary and store it in your database.** 
This is because every time you generate a secret key, a new session is started and your password is sent over the internet. This is less secure, even though https encryption used.

##### 2. Hash the secret key to generate an access key
Authenticating all api requests in a session requires the following parameters:
	- access_key
	- session_id
	- nonce
	- time

You should generate a new access key for each API request you make, based on the secret_key which you created in the beginning of your session.
You generate the access key by making a sha256 hash from your secret_key + nonce + time, where + implies concatenation.

##### Nonce
The nonce variable is a random string. 
**You should generate a different nonce for each request.**

##### Time
Time is the unix timestamp in seconds evaluated at the moment of generating the key.


Summarizing, your access key should look like this:
``access_key = sha256( secret_key + nonce + time )``

**Do not pass the secret_key in normal api requests, the secret key is only to be used with the generate_secret method.** 

=========

# Methods
    
### get_articles	
Use the get_articles method to obtain articles from a news filter. 

The following url will return all articles from the Apple filter with the filter_id ``82512822dfe111e2a6d2001143dc2095``:
``https://newsroom.owlin.com/api/v1/get_articles/filter:82512822dfe111e2a6d2001143dc2095?access_key=access_key&nonce=new_nonce&time=authenticate_time``

The value parameter ``filter:82512822dfe111e2a6d2001143dc2095`` is an example of a stream_id. For different stream_id options see the stream_id options paragraph in the description of the facets method. 
		
##### Additional parameters:
- ``hits``
 - default: 25
 - number between 0 and 200 
 - Using the hits parameter you can change the amount of articles returned	
- ``sort``
	- Using the 'sort' parameter you can define in which manner the articles are be sorted.	
	- default: scored:desc
	- Value can be 
		- decaying_activity
		- activity
		- epoch
- ``range``
	- Use the range parameter to filter out articles from a specific time or ranking range. The value is an object with the key you want to filter on, followed by a ``from`` and/or ``to`` field. Like: ``range = {"epoch":{"from":1389861184,"to":1391070784}}``
	- By default, the range goes from 2 weeks ago to the current time.
	- Fields of which you can set a range are:
		- decaying_activity
		- activity
		- epoch
- ``group_by``	
	- Using the group_by parameter, you can filter the results on unique values for that field. Saying ``group_by=topic`` will return you a list of only unique topics.
	- Fields you can group by are:
		- topic
		- none
	- ``stats``
		- If you set this value to ``true``, we will apply the [stats method](#stats) to each topic in the results on the key ``stats``.

##### Output
```javascript
[
    {
      "url": "http://thenextweb.com/twitter/2014/01/30/the-original-owner-of-n-still-hasnt-got-his-twitter-account-back-someone-else-snapped-it-up/",
      "topic": "1b2b4384c061442e78e0d89363d1d482",
      "epoch": 1391068768,
      "decaying_activity": 1391068768,
      "urlhash": "f760702ee6a5a81cf515d6f29d6cfc32",
      "header": "The original owner of @N still hasn’t got his Twitter account back – someone else snapped it up",
      "topic_epoch": 1390986023,
      "activity": 0,
      "domain": "thenextweb.com",
      "language": "en",
      "read": false
    }
	/* .. truncated ..*/
]
```

============

### stats 
Use this method to get statistics about articles in a news filter.

The following url will return an array with amount of articles posted per minute, each minute, over the past 14 days,
``https://newsroom.owlin.com/api/v1/stats/filter:82512822dfe111e2a6d2001143dc2095?access_key=[access_key]&nonce=[nonce]&time=[time]``

*As for the get_article method the value parameter is a stream_id.*

#### Additional parameters:
- ``interval``
	- default: ``60``
	- number of seconds, length of the binning time intervals. 
	- Using the 'interval' parameter you can define the amount of seconds to group the statistics on.
- ``date_from``
	- Using the 'from' parameter you can define the begin date in epoch to select the articles from.
	- default: ``epoch(time - 2 weeks ago)``
- ``date_to``
	- Using the 'date_to' parameter you can define the end range of the statistics. Based on article publish date.
	- default: ``now``

##### Output
```javascript
[
	/* … truncated … */
	{
		"key": 1382400000,
		"count": 55163
	},
	{
		"key": 1391040000,
		"count": 97
	}
]
```

============

### filter.get
Use this method to get filters by their ids.

This method always returns the title of the filter, the alert settings, last modified, created, creator and if you are allowed acces it also gives the search rules which determine the filter's output.  
The following url will return a list with the contents of the apple filter
``https://newsroom.owlin.com/api/v1/filter.get_filter_by_ids/82512822dfe111e2a6d2001143dc2095?access_key=access_key&nonce=nonce&time=time``

##### Multiple filters:
Separate multiple filter_ids by commas

##### Advanced parameters:
This method has no advanced options.

##### Output:
```javascript
{
    "vfzowgkpkrupafspxscilgfmqwrcgqnh": {
        "filter_id": "vfzowgkpkrupafspxscilgfmqwrcgqnh",
        "stream_id": "filter:vfzowgkpkrupafspxscilgfmqwrcgqnh",
        "creator": "7e7eecc0534611e2bc97001143dc2095",
        "created": 1390401909.438,
        "rules": [
            {
                "value": "\"albert heijn\" \"albert hein\" \"appie\"",
                "type": "search"
            }
        ],
        "title": "Albert Heijn",
        "sort": "decaying_activity",
        "group_by": "topic",
        "last_modified": 1390401941.274,
        "edit": true,
        "alert": false
    }
}
```

**Note that each requested filter is nested in an object with its filter_id as key.**

============

### filter.save
Use this method to create or edit a filter.

The following url will create a filter searching for apple:
``https://newsroom.owlin.com/api/v1/filter.save/new?title=Apple&rules[]=[{“type":"search","value":"apple"}]&access_key=access_key&nonce=nonce&time=time``
		
**Creating a new filter**
Pass the value ``new``  to create a new filter.

**Editing an existing filter**
Pass the filter_id in the ``value`` parameter in order to save an existing filter. This requires permissions to edit this filter.
		
##### Advanced parameters:
- ``title``
	- Defines the title for the filter
	- This field is required
- ``alert``
	- Sends an email to the user whenever a new article matches the filter
	- Default: false
- ``rules``
	- Define here on what queries your filter should search. Read more about rules [here](#filter-rules)

##### Example output:
```javascript
{
	"filter_id": "vfzowgkpkrupafspxscilgfmqwrcgqnh",
	"stream_id": "filter:vfzowgkpkrupafspxscilgfmqwrcgqnh",
	"creator": "7e7eecc0534611e2bc97001143dc2095",
	"created": 1390401909.438,
	"rules": [
		{
			"value": "\"albert heijn\" \"albert hein\" \"appie\"",
			"type": "search"
		}
	],
	"title": "Albert Heijn",
	"sort": "decaying_activity",
	"group_by": "topic",
	"last_modified": 1390401941.274,
	"edit": true,
	"alert": false
}
``` 		
============

### invite.generate_token
Generate a token you can use to create a new user account. 

The following url will create a token to create a new user account:
``https://newsroom.owlin.com/api/v1/invite.generate_token?access_key=access_key&nonce=nonce&time=time``

**Note: This method is not available to everyone and will be activated upon request.** 
**Note: Signup tokens expire after 60 days**

##### Advanced parameters:
- email
	- This assigns the invite token to be only used by the defined email address. 

##### Example output:
```javascript
{
    "token_id": "swysriumctlbfbpecxlshhwysfhtelxx",
    "inviter": "7e7eecc0534611e2bc97001143dc2095",
    "user_id": false,
    "created": 1390989876.013,
    "email": ""
  }
```

============

### signup.token
Retrieve information about a signup token.

The following url will return information about a given signup token:
``https://newsroom.owlin.com/api/v1/signup.token/[token_id]``

##### Advanced parameters:
This method has no advanced options.

##### Example output:
```javascript
{
    "token_id": "swysriumctlbfbpecxlshhwysfhtelxx",
    "inviter": "7e7eecc0534611e2bc97001143dc2095",
    "user_id": false,
    "created": 1390989876.013,
    "email": ""
  }
```

============

### signup
This creates a new user account you can use to login into the newsroom or make API requests with.

The following URL will create a new user account
``https://newsroom.owlin.com/api/v1/signup?name=Luke%20Skywalker&email=luke.skywalker@jediorder.gov&password=usetheforce111&phone=063FE4823&invite_token=swysriumctlbfbpecxlshhwysfhtelxx&access_key=access_key&nonce=nonce&time=time``

- ``name``
	- Your name
- ``email``
	- Your email address
- ``password``
	- Your password, should be at least 6 characters
- ``phone``
	- Your phone number
- ``invite_token``
	- Your invite token you generated before using the [invite.generate_token function](#invitegenerate_token)

##### Output:
```javascript
{
    "secret_key": "voqiwzxhmcnswgnhtkmvqegbulalmsib",
    "session_id": "glkltchg0qnnehiqjcrdjyednyniuaso",
    "creation_date": 1390990917,
    "last_used_date": 1390990917,
    "user_id": "mwfhnhnpwitwpkuvxnjjbzztjwphcmtk",
    "server_time": 1390990917
  }
```

============

### password.update
This allows you to change the password for your user account when you still remember the old password.

The following url will change your password:
``https://newsroom.owlin.com/api/v1/password.update?old_password=usetheforce111&new_password=I_miss_my_dad82&access_key=access_key&nonce=nonce&time=time``

- ``old_password``
	- Please verify your old password for extra verification
- ``new_password``
	- Your new password, should be at least 6 characters long.

##### Example output:
```javascript
{
    "success": true,
    "user_id": "mwfhnhnpwitwpkuvxnjjbzztjwphcmtk"
  }
```

============

# General Definitions

### Filter Rules:
When saving the filter, you can attach rules to the must and must_not parameters. You can use the following rules:
	
- search
	- Yields articles matching the query string
	- Example: `` { "type" : "search, "value" : "apple" } ``
	- Parameters
		- ``value``: Query in the Lucene query language
- should
	- Yields articles containing at least 2 terms
	- Example: ``{ "type" : "should", "value" : "apple samsung nokia", "n" : 2 }``
	- Parameters:
		- ``value``: query in the Lucene query language
		- ``n``: minimum amount of terms, ranging between 1 and 10
- language
	- Yields articles of only these languages
	- Example: ``{ "type" : "lang", "value" : [ "nl" ] }``
	- Default: all languages
	- Parameters:
		- ``value``: Language code of language, can be ``nl``, ``fr``, ``en``, ``de`` or ``pl``
- translate
	- Defines to search in the original or translated text (or both).
	- Example: ``{ "type" : "translate", "value" : ["original", "translated"] }``
	- Default: ``[original]``
	- Parameters:
		- ``value``: list of text editions to search in ``[ original, translated ]``
- fields
	- Defines in which fields to search
	- Example: ``{ "type" : "fields", "value" : ["header", "description"] }``
	- Default = [ header, description ]
	- Parameters:
		- ``value``: list of fields to search in ``[ header, description ]``
- filter
	- Includes the search queries from another filter. 
	- Example: ``{ "type" : "filter", "value" : "filter:82512822dfe111e2a6d2001143dc2095" }``
	- Parameters:
		- ``value``: stream_id you want to in/exclude

### stream_id options:	
The required value parameter for the ``get_articles`` and ``stats`` methods is a stream_id associated to a search. The stream_id can take several different forms:

- filter:filter_id
	- Will return all articles contained in that filter
- thread:topic_id
	- Will return all articles inside a topic.
- group:group_id
	- Will return all articles merged from a group of filters		

# Undocumented methods:
The following methods exist but are not documented yet, if you have any questions about this, please contact richard@owlin.com or browse [the Owlin newsroom](https://newsroom.owlin.com)’s browser console network log. 
- user_info
- invite.email
- group.get
- group.save
- group.add
- group.remove
- password.reset
- change_password
- highlight
- read.get
- read.save
	
