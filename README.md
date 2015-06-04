
![alt text](http://owlin.com/images/homelogo.png "Owlin")
## REST API 2.alpha - Python 2.7+ Walkthrough

This is a short quickstart guide to learn how to use our awesome new API.

### Table of contents
- [The REST API documentation](#apidocumentation)
- [Get started](#getstarted)
- [Getting an authorization token](#authtoken)
- [Creating a new search](#newsearch)
- [Retrieving the articles related to a search](#searcharticles)
- [Retrieving the statistics related to a search](#searchstats)
- [Retrieving information about a topic](#topic)
- [Wrapping up](#wrappingup)

<div id='apidocumentation'/>
### The REST API documentation
The Owlin API 2.alpha interactive reference documentation can be reached at the following URL: https://api.owlin.com/documentation

There you can:
* find a detailed reference of the REST methods and their parameters;
* see the JSON schema to pass along the PUT, POST and PATCH calls;
* test all the methods directly from the browser!

<div id='getstarted'/>
### Get started
All code snippets in this tutorial assume you have the following libraries installed and loaded:

```python
import json, requests   # if you don't have requests installed, "pip install requests" will do
```

It is also assumed that you have declared and initialized the `base_url` variable:

```python
base_url = "https://api.owlin.com/v2"
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

We then put together an example search, that you can see below.  For more information about the single fields, don't forget to check the API 2.alpha reference at the link above.

```python
example_search = {
  "title": "Precious metals",                                   
  "article_languages": ["en", "nl", "de", "fr", "es", "pl"],
  "should": [
    {
      "match": "1",                                            
      "search": ["gold", "silver", "palladium", "platinum"],
      "scope": {"english_title": True, "english_description": False}
    },
    {
      "match": "2",
      "search": ["price", "corporation", "stocks", "futures", "options", 
                 "bearish", "bullish", "commodit*", "market*", "mining", "analyst*"],
      "scope": {"english_title": True, "english_description": True}
    }
  ],
  "should_not": [
    {
      "match": "all",
      "search": ["medal*", "olympic*", "world cup", "championship*", "gold coast", "pendant", 
                 "necklace", "marketing", "jewel*", "gold membership", "silver membership"],
      "scope": {"english_title": True, "english_description": True}
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
* a `match` field, whose value is a string with the minimum number of terms we want our rule to match. We can also use *"all"* if we want the rule to match all the terms.<sup>[1](#footnote1)</sup>
* a `search` field, that contains a list of search expressions, each encoded as a string. __?__ and __*__ can be used as wildcards, where _?_ represents any single (non empty) character and _*_ any sequence of characters, including the empty one. Another important feature is what we call *proximity search*: using `"{gold AND~4 price}"` as search expression will match with a sentence having the words *gold* and *price* with at most 3 words separating them;
* a `scope` field, which tells our API where to look for the expressions, more specifically:
  * if `title` and/or `description` are set to True, it will look in the title and/or the body of the news articles, respectively;
  * if `english_title` and/or `english_description` are set to True, it will look for the expressions in the translated version of the title and/or the body. Our back-end translates every article to English!<sup>[2](#footnote2)</sup>

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
Each article contains fields like `title` and `description`, containing respectively its title and its full-text. It also contains a `topic_id`, which we will show you how to use in a little while.

For more information, once again, refer to the API documentation.

<div id='searchstats'/>
### Retrieving the statistics related to a search

We can get some statistics about the articles matching a search by using the following method:

```python
bucket = "monthly"
epoch_from = 1401926400   # equivalent to midnight UTC of 05/06/2014
epoch_to = 1433462400     # equivalent to midnight UTC of 05/06/2015
stats_response = requests.get("{0}/news-searches/{1}/stats/{2}".format(base_url,search_id,bucket), headers={"authorization": auth_token}, params={"from": epoch_from, "to": epoch_to})
stats_dict = json.loads(stats_response)
```
Since our statistics refer to time periods of constant length *(buckets)*, the first thing to do is to choose the size of the *bucket* we want to investigate.  The available values are `hourly`,`daily`,`weekly`,`monthly` and `yearly`.  We can also choose a time window for our buckets, by specifying the values of the `from` and `to` parameters as Unix epochs.<sup>[3](#footnote3)</sup>

We then pass the `search_id` along, and what we get back is the number of articles matching that search that we gathered for each bucket, starting at `epoch_from` and ending at `epoch_to`.  

<div id='topic'/>
### Retrieving information about a topic

Once we lay our hands on a `topic_id`, we can get all sorts of useful information about a specific topic.
Loosely said, different articles share the same topic when they talk about the same news event. In other words, when our system analyzes multiple articles that share enough keywords, it groups them under the same `topic_id`.

```python
topic_id = articles_dict[0]["topic_id"]   # topic_id of the 1st matching article
topic_response = requests.get("{0}/news-topics/{1}".format(base_url,topic_id), headers={"authorization": auth_token}).text
topic_dict = json.loads(topic_response)
```
Aside from the usual `id`, and a list of `article_id` sharing the specified topic contained in the `articles` field, the return object contains some slightly more cryptic fields:

* `epoch` is the Unix timestamp in which the article was published;
* `activity` is our proprietary ranking system, calculated on how often a news article is reported and on how quickly it spreads across the Web. This can be used, for instance, if you would like to know which were the biggest stories over the past year;
* `buzz` is obtained by simply adding the epoch to the activity score;
* `latest` is the timestamp in which an article referring to this topic was last spotted.

<div id='wrappingup'/>
### Wrapping up

In this brief tutorial we have gone through some of the most important methods of our API.
You should now be able to create a search, get the resulting articles and play around with topics. Now it's up to you!
Draw inspiration from the visualizations we created with our API<sup>[4](#footnote4)</sup>, or come up with something totally new - as they use to say, the sky is the limit!

Should you still have any questions, feel free to mail us at support@owlin.com. :-)


***

<div id='Footnotes'/>
##### Footnotes

<div id="footnote1"/>
<sup>1: Note that matching a single term equals to a logical *OR*, while matching all the terms works like a logical *AND* between them.</sup>
<div id="footnote2"/>
<sup>2: If the original text is in English, the `english_title` and `english_description` fields will simply contain a copy of the original fields. The parameters are all optional, and if none is specified they default to: `{title: True, description: True, english_title: False, english_description: False}`</sup>
<div id="footnote3"/>
<sup>3: http://www.unixtimestamp.com/</sup>
<div id="footnote4"/>
<sup>4: you can find them on https://owlin.github.io/</sup>

