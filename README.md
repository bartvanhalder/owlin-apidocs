# Owlin REST API

## Methods
- get_articles


### URL Scheme
The Owlin request url of the Owlin API is constructed as follows,

#### Input:
Both GET an POST are supported for the same type of requests. However, whenever an extra-parameter is longer than 1024 bytes, you should use POST headers.

##### For GET requests with e.g. 2 parameters:
``https://newsroom.owlin.com/api/v1/method/value?extra-parameter_1=extra-value_2&extra-parameter_2=extra-value_2``

##### For POST requests with e.g. 1 parameter: 
``https://newsroom.owlin.com/api/v1/method``
``value=value&extra-parameter=extra-value``

The value parameter is optional in general, both for POST and GET requests, some methods however require a certain value to be set. 

#### Output:
The API will always respond JSON.

#### JSONP Callbacks
To request a JSONP Callback from the API, to be used for instance in javascript, use ``?callback=callback_function_name``

#### Multidict parameters
When a method requires a dictionary as an extra-value, encode it as JSON and add two brackets behind [extra-parameter] i.e.
``https://newsroom.owlin.com/api/v1/method/value?extra-parameter[]=extra-value``

#### Authentication
Almost every request requires authentication. It is a two-step process. 

1.  ##### Firstly, you request a secret_key. 
Each time you request a secret_key a new session is started. 
You request a secret_key using the method generate_secret. The method requires 2 parameters, ``email`` and ``password``. If you are using the newsroom, you can use the same credentials here. 

The required url is:
``https://newsroom.owlin.com/api/v1/generate_secret?email=email@example.com&password=password``

**Please keep the number of sessions to a minimum since for each new session you have send your password over the internet. Even though this happens in an encrypted manner (https) it is less secure. We highly recommend you to store this key into your database.**

2. ##### Hash the secret key to generate an access key
Authenticating all api requests in a session requires the following parameters:
	- access_key
	- session_id
	- nonce
	- time

You should generate a new access key for each API request you make, based on the secret_key which you created in the beginning of your session.
You generate the access key by making a sha256 hash from your secret_key + nonce + time, where + implies concatenation.

	The nonce variable is a random string. 
	You should generate a different nonce for each request.
	Time is the unix timestamp in seconds evaluated at the moment of generating the key.

	Summarizing, your access key should look like this:
		sha256( secret_key + nonce + time )

**Do not pass the secret_key in normal api requests, the secret key is only to be used with the generate_secret method.** 


# Methods
    
## get_articles	
Use the get_articles method to obtain articles from a news filter. 
The following url will return all articles from the Apple filter with the filter_id ``82512822dfe111e2a6d2001143dc2095``:
``https://newsroom.owlin.com/api/v1/get_articles/filter:82512822dfe111e2a6d2001143dc2095?access_key=access_key&nonce=new_nonce&time=authenticate_time``

The value parameter ``filter:82512822dfe111e2a6d2001143dc2095`` is an example of a stream_id. For different stream_id options see the stream_id options paragraph in the description of the facets method. 
		
#### Additional parameters:
- hits
>- default: 25
>- number between 0 and 200 
>- Using the hits parameter you can change the amount of articles returned	
- sort
>- default: scored:desc
>- Value can be 
>>- decaying_activity
>>- activity
>>- epoch

>- Using the 'sort' parameter you can define in which manner the articles are be sorted.	
		- from 
			- default: time - 2 weeks 	
			- number representing scored, score, epoch depending on the method of sorting. 
			- Using the 'from' parameters, you can define the minimal value of the range within which the articles are sorted.
		- to 
			- default: none
			- number representing scored, score, epoch depending on the method of sorting.
			- Using the 'to' parameter, you can define the maximum value of the range within which the articles are sorted.

	facets 
		Use this method to get statistcs about articles in a news filter.
		The following url will return an array with amount of articles posted per minute, each minute, over the past 14 days,
		https://newsroom.owlin.com/api/v1/filter.get_article_count/filter:82512822dfe111e2a6d2001143dc2095?access_key=[access_key]&nonce=[nonce]&time=[time]
		As for the get_article method the value parameter is a stream_id.

		Additional parameters:
		- interval
			- default: 60
			- number of seconds, length of the binning time intervals. 
			- Using the 'interval' parameter you can define the amount of seconds to group the statistics on.
		- date_from
			- default: time - 2 weeks ago
			- Using the 'from' parameter you can define the begin date in epoch to select the articles from.
		- date_to
			- default: now
			- Using the 'date_to' parameter you can define the end range of the statistics. Based on article publish date.

		stream_id options:	
		The required value parameter for the get_articles and facets methods is a stream_id associated to a search.
		The stream_id can take several different forms:
		- filter:filter_id
			- Will return all articles contained in that filter
		- filter:filter_id_A;filter:filter_id_B
			- Will return all articles which match both filter_A and filter_B
		- filter:filter_id_A;iphone
			- Will return all articles which match the filter and the phrase "iphone"
		- thread:topic_id
			- Will return all articles inside a topic.
		- search:apple
			- Will do a quick-search, returning all articles matching the phrase "apple"
		- apple
			- Shortcut for search:apple
		- rules:{"must":[{"type":"search","value":"apple"}]}
			- Will return all articles matching the phrase apple, explore the filter.save documentation to see more possibilties using rules.
		Future planned stream-id's in development:
		- group:group_id
			- Will return all articles merged from a group of filters				
    
	filter.get_filter_by_ids
		Use this method to get filters by their ids.
		This method always returns the title of the filter, the alert settings, last modified, created, creator and if you are allowed acces it also gives the search rules which determine the filter's output.  
		The following url will return a list with the contents of the apple filter
		https://newsroom.owlin.com/api/v1/filter.get_filter_by_ids/82512822dfe111e2a6d2001143dc2095?access_key=access_key&nonce=nonce&time=time
		Multiple filters:
		Separate multiple filter_ids by commas
		Advanced parameters:
		This method has no advanced options

	filter.get_user_filters
		Method to obtain all the filter_ids the authenticated user is subscribed to.

	filter.save
		Only if you have permissions you can use this method to add or edit a filter.
		The following url will create a filter searching for apple:
		https://newsroom.owlin.com/api/v1/filter.save?title=Apple&must[]=[{"type":"search","value":"apple"}]&access_key=access_key&nonce=nonce&time=time
		
		Editing an existing filter
		Pass the filter_id in the 'value' parameter in order to save an existing filter.
		Advanced parameters:
		- alert
			- default: false
			- boolean
			- Sends an email to the user whenever a new article matches the filter
		
		Rules:
		When saving the filter, you can attach rules to the must and must_not parameters. 
		You can use the following rules:	
		- search
			Yields articles matching the query string
			value	= query in the lucene query language
			Example: { "type" : "search, "value" : "apple" } 
		- should
			Yields articles containing at least 2 terms
			Parameters:
			value	= query in the lucene query language
			n		= minimum amount of terms, ranging between 1 and 10
			Example: { "type" : "should", "value" : "apple samsung nokia", "n" : 2 }
		- lang
			Yields articles of only these languages
			value	= language code of language, can be nl, fr, en, de
			default	=  all possible languages 
			Example: { "type" : "lang", "value" : [ "nl" ] }
		- translate
			Defines to search in the original or translated text (or both).
			value	= list of text editions to search in [ original, translated ]
			default = [original]
			Example: { "type" : "translate", "value" : ["original", "translated"] }
		- fields
			Defines in which fields to search
			value	= list of fields to search in [ header, description ]
			default = [ header, description ]
			Example: { "type" : "fields", "value" : ["header", "description"] }
		- filter
			Includes the search queries from another filter. 
			value	= stream_id you want to in/exclude
			Example: { "type" : "filter", "value" : "filter:82512822dfe111e2a6d2001143dc2095" }

	filter.delete_subscription
		Use this method to unsubscribe a filter. Unused filters will be deleted.
		The following url will unsubscribe the authenticated user from a filter.
		https://newsroom.owlin.com/api/v1/filter.delete_subscription/82512822dfe111e2a6d2001143dc2095?access_key=[access_key]&nonce=[nonce]&time=[time]

	generate_secret:
		Use this method to generate a new secret key.
		The following url will unsubscribe the authenticated user from a filter.
		https://newsroom.owlin.com/api/v1/filter.delete_subscription/82512822dfe111e2a6d2001143dc2095?access_key=[access_key]&nonce=[nonce]&time=[time]
		
		Your application is supposed to store the secret key once, only regenerate whenever your key has been expired or deactivated.
		You should never transfer your secret key within your request.
	
	Undocumented methods:
	- user_info
	- stats.hour
	- stats.days
	- stats.queues
	- invite.email
	- invite.get_token
	- invite.generate_token
	- filter.get_filter_subscribers
	- filter.add_subscription
	- signup
	- password.reset
	- change_password	
	