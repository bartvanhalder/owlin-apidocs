# Owlin API 2.0 tutorial

### Table of contents
- [API url](#apiurl)
- [Getting an authorization token](#authtoken)
- [Creating a new search](#newsearch)
- [Retrieving the articles related to a search](#searcharticles)
- [Retrieving the statistics related to a search](#searchstats)

This is a short quickstart guide to learn how to use our awesome new API!

<div id='apiurl'/>
###API URL

The Owlin API 2.0 online reference can be reached at the following URL:

```
base_url = "http://jsapi.devstar.owlin.com"
```
Here you can:
* find a detailed reference of the REST methods and their parameters
* see the JSON schema to pass along the PUT, POST and PATCH calls
* test all the methods directly from the browser!

The code snippets below all assume the *base_url* variable to be declared as above.

<div id='authtoken'/>
###Getting an authorization token

The first thing to do is to get an authorization token, it can be done as follows:

```
user_data = {
  "pw": "your_password",
  "email": "your_email",
  "duration": 0             # it should be left to 0 for now
}

auth_token = requests.post("{0}/tokens".format(base_url), data=json.dumps(user_data)).text
```

 We store the token in a variable, because it will be a parameter to all our successive REST calls; we assume *auth_token* to contain a valid token in all the following code snippets.

<div id='newsearch'/>
### Creating a new search
Once we have the token, things start getting more interesting!

Let's say, as an example, that we want to be up to date with the latest news related to the price fluctuations of some precious metals, namely gold, silver, platinum and palladium. Just typing in the keywords would not be specific enough, because while most of the articles containg the world "gold" are indeed related to the price of gold, Owlin would keep us up to date also about sport champions who just earned a gold medal, and freemium websites that just introduced a new gold membership.
Don't forget, by the way, that our sources go well beyond the mainstream news outlets! 

We then put together an example search, that you can see below.  For more information about the single fields, don't forget to check the API 2.0 reference at the link above!

```
example_search = {
  "title": "Precious metals",                                   
  "article_languages": ["en", "nl", "de", "fr", "es", "pl"],
  "keyword_language": "en",                                    
  "should": [
    {
      "match": "1",                                            
      "search": ["gold", "silver", "palladium", "platinum"],
      "scope": {"title": True, "description": False}
    },
    {
      "match": "2",
      "search": ["price", "corporation", "stocks", "futures", "options", 
                 "bearish", "bullish", "commodit*", "market*", "mining", "analyst*"],
      "scope": {"title": True, "description": True}
    }
  ],
  "should_not": [
    {
      "match": "all",
      "search": ["medal*", "olympic*", "world cup", "championship*", "gold coast", "pendant", 
                 "necklace", "marketing", "jewel*", "gold membership", "silver membership"],
      "scope": {"title": True, "description": True}
    }
  ],
  "includes": [],
  "excludes": [],
  "permissions": {}
}

search_response = requests.post("http://jsapi.devstar.owlin.com:80/news-searches", data=json.dumps(example_search), headers={"authorization": auth_token}).text
search_dict = json.loads(search_response)
```

The keywords we used to define the search are divided between two tags: *should* and *should not*; the names are pretty self-explanatory.

A rule is defined by a minimum number of matching terms (can be set to "all" too!), a list of search terms, two boolean values that tell our back-end if to look for the specified terms just in the title of the article, just in the body, or in both.  Note that you can have multiple rules within the *should* or the *should not* tag.

While defining the keywords withing each tag you can use the asterisk within a word as a *wildcard*: it will match with any amount of characters of any sort.  In our example, we wanted to match the words *market* and *markets*, but not the word *marketing*; we then added *market*\* under a *should* rule, and *marketing* under a *should not* rule.

The tags *includes* and *excludes* are used to chain searches: you can add there one or more search ids to expand on them.  The search ids are part of the object returned by the POST call, as we will see just now.

<div id='searcharticles'/>
### Retrieving the articles related to a search

Having our personal search saved into the system is a nice first step, but we may as well be interested in getting some actual content. The first step, as suggested above, is to extract the id of the search we just created from the output of the POST call.

```
search_id = search_dict["id"]
articles_json = requests.get("{0}/news-searches/{1}/articles".format(base_url,search_id), params={} ,headers={"authorization": auth_token})
```


<div id='searchstats'/>
### Retrieving the statistics related to a search

```
bucket = "monthly"
stats_json = requests.get("{0}/news-searches/{1}/stats/{2}".format(base_url,search_id,bucket), params={} ,headers={"authorization": auth_token})
```
