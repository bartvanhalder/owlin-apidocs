## Owlin REST API 2.alpha - Python 2.7+ Walkthrough

This is a short quickstart guide to learn how to use our awesome new API.

### Table of contents
- [The REST API documentation](#apidocumentation)
- [Get started](#getstarted)
- [Getting an authorization token](#authtoken)
- [Creating a new search](#newsearch)
- [Retrieving the articles related to a search](#searcharticles)
- [Retrieving the statistics related to a search](#searchstats)
- [Retrieving information about a topic](#topic)

<div id='apidocumentation'/>
### The REST API documentation
The Owlin API 2.0 interactive reference documentation can be reached at the following URL: http://jsapi.devstar.owlin.com/documentation

There you can:
* find a detailed reference of the REST methods and their parameters
* see the JSON schema to pass along the PUT, POST and PATCH calls
* test all the methods directly from the browser!

<div id='getstarted'/>
### Get started
All code snippets in this tutorial assume you have the following libraries installed and loaded:

```python
import json, requests   # if you don't have requests installed, "pip install requests" will do
```

It is also assumed that you have declared and initialized the `base_url` variable:

```python
base_url = "http://jsapi.devstar.owlin.com"
```

<div id='authtoken'/>
###Getting an authorization token

The first thing to do is to get an authorization token, it can be done as follows:

```python
user_data = {
  "pw": "your_password",
  "email": "your_email",
  "duration": 0             # it should be left to 0 for now
}

auth_token = requests.post("{0}/tokens".format(base_url), data=json.dumps(user_data)).text
```

 We store the token in a variable, because it will be a parameter to all our successive REST calls; we assume `auth_token` to contain a valid token in all the following code.
 
<div id='newsearch'/>
### Creating a new search
Once we have the token, things start getting more interesting!

Let's say, as an example, that we want to be up to date with the latest news related to the price fluctuations of some precious metals, namely gold, silver, platinum and palladium. Just typing in the keywords would not be specific enough, because while most of the articles containg the world "gold" are indeed related to the price of gold, Owlin would keep us up to date also about sport champions who just earned a gold medal, and freemium websites that just introduced a new gold membership.
Don't forget, by the way, that our sources go well beyond the mainstream news outlets! 

We then put together an example search, that you can see below.  For more information about the single fields, don't forget to check the API 2.0 reference at the link above.

```python
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

search_response = requests.post("{0}/news-searches".format(base_url), data=json.dumps(example_search), headers={"authorization": auth_token}).text
search_dict = json.loads(search_response)
```

The keywords we used to define the search are divided between two tags: `should` and `should not`; the words in `should` are the ones we want in our articles, the ones in `should not` are the ones we would like to filter out. A single tag contains a list of rules.

A rule is defined by:
* a `match` field, whose value is a string with the minimum number of terms we want our rule to match. We can also use *"all"* if we want the rule to match all the terms. Note that matching a single term equals to a logical *OR*, while matching all the terms works like a logical *AND* between them.
* a `search` field, that contains a list of search expressions, each encoded as a string. __?__ and __*__ can be used as wildcards, where _?_ represents any single character and _*_ any sequence of characters. 
* a `scope` field, with two boolean values that tell our back-end if to look for the specified expressions just in the title of the article, just in the body, or in both.  

We actually used wildcards in our example search: we wanted to match the words *market* and *markets*, but not the word *marketing*; we then added *market*\* under a `should` rule, and *marketing* under a `should not` rule.

The tags `includes` and `excludes` are used to chain searches: you can add there one or more search ids to expand on them.  The search ids are part of the object returned by the POST call, as we will see just now.

<div id='searcharticles'/>
### Retrieving the articles related to a search

Having our personal search saved into the system is a nice achievement in itself, but we may as well be interested in getting some actual content. The first step, as suggested above, is to extract the *id* of the search we just created from the output of the POST call.

```python
search_id = search_dict["id"]
articles_response = requests.get("{0}/news-searches/{1}/articles".format(base_url,search_id), headers={"authorization": auth_token}).text
articles_dict = json.loads(articles_response)
```
The variable `articles_response` now contains a list of articles, as they are saved into our system.
Each article contains fields like `title` and `description`, containing respectively its title and its full-text. It also contains a `topic_id`, which is shared among all the articles that talk about the same news within a two-days window. 

For more information, once again, refer to the API documentation.

<div id='searchstats'/>
### Retrieving the statistics related to a search

```python
bucket = "monthly"
stats_response = requests.get("{0}/news-searches/{1}/stats/{2}".format(base_url,search_id,bucket), headers={"authorization": auth_token})
stats_dict = json.loads(stats_response)
```

<div id='topic'/>
### Retrieving information about a topic

Once we lay our hands on a `topic_id`, we can get all sort of useful information about a specific topic.
```python
topic_id = articles_dict[0]["topic_id"]
topic_response = requests.get("{0}/news-topics/{1}".format(base_url,topic_id), headers={"authorization": auth_token}).text
topic_dict = json.loads(topic_response)
```
Aside from the usual `id`, and a list of `article_id` sharing the specified topic contained in the `articles` field, the return object contains some slightly more cryptic fields:

* `activity` test
* `buzz` test
* `epoch` test
* `latest` test
