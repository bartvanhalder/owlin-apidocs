## Owlin REST API 2.alpha - Java SE Runtime Environment 7 Walkthrough

This is a short quickstart guide to learn how to use our awesome new API.

### Table of contents
- [The REST API documentation](#apidocumentation)
- [Get started](#getstarted)
- [Getting an authorization token](#authtoken)
- [Creating a new search](#newsearch)
- [Retrieving the articles related to a search](#searcharticles)
- [Retrieving the statistics related to a search](#searchstats)

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

http://code.google.com/p/json-simple/

```java
import java.io.BufferedReader;
import java.io.OutputStream;
import java.io.InputStreamReader;
import java.net.URL;
 
import javax.net.ssl.HttpsURLConnection;

import org.json.JSONObject;
import org.json.simple.JSONValue;
import org.json.simple.JSONArray;
```

it is also assumed that you have declared the base_url variable declared as follows,

```java
private final String base_url = "http://api.owlin.com/v2";

```

<div id='authtoken'/>
###Getting an authorization token

The first thing to do is to get an authorization token, it can be done as follows:

```java
String user = "{ \"email\": \"your_email\", \"pw\": \"your_password\", \"duration\": 0 }";

URL request = new URL(BASE_URL + "/tokens");
HttpsURLConnection connection = (HttpsURLConnection) request.openConnection();

connection.setRequestMethod("POST");
connection.setRequestProperty("Content-Type", "application/json");
connection.setDoOutput(true);

OutputStream output = connection.getOutputStream();
output.write(user.getBytes());
output.flush();
output.close();

BufferedReader inputBuffer = new BufferedReader(
               new InputStreamReader(connection.getInputStream())
);

String inputLine;
StringBuffer response = new StringBuffer();

while ((inputLine = inputBuffer.readLine()) != null) {
response.append(inputLine);
}
inputBuffer.close();

String auth_token = response.toString(); 
```

 We store the token in a variable, because it will be a parameter to all our successive REST calls; we assume `auth_token` to contain a valid token in all the following code.
 
<div id='newsearch'/>
### Creating a new search
Once we have the token, things start getting more interesting!

Let's say, as an example, that we want to be up to date with the latest news related to the price fluctuations of some precious metals, namely gold, silver, platinum and palladium. Just typing in the keywords would not be specific enough, because while most of the articles containg the world "gold" are indeed related to the price of gold, Owlin would keep us up to date also about sport champions who just earned a gold medal, and freemium websites that just introduced a new gold membership.
Don't forget, by the way, that our sources go well beyond the mainstream news outlets! 

We then put together an example search, that you can see below.  For more information about the single fields, don't forget to check the API 2.0 reference at the link above.

```java
String example_search = "{ " +
        "\"title\": \"test\", " +
	"\"article_languages\": [ \"en\" ], " +
	"\"should\": [ {" +
	    "\"match\": 1, " +
	    "\"search\": [ \"apple\" ], " +
	    "\"scope\": { \"title\": true, \"description\": false } " +
	"} ], " +
        "\"should_not\": [ { " +
	    "\"match\": 1, " +
	    "\"search\": [ \"test\" ], " +
	    "\"scope\": { \"title\": true, \"description\": false } " +
	"} ], " +
	"\"includes\": [], " +
	"\"excludes\": [], " +
	"\"permissions\": {} " +
    "}";

URL request = new URL(BASE_URL + "/news-searches");
HttpsURLConnection connection = (HttpsURLConnection) request.openConnection();
                        
connection.setRequestMethod("POST");
connection.setRequestProperty("authorization", auth_token);
connection.setRequestProperty("Content-Type", "application/json");
connection.setDoOutput(true);
                        
OutputStream output = connection.getOutputStream();
output.write(example_search.getBytes());
output.flush();
output.close();
			
BufferedReader inputBuffer = new BufferedReader(
    new InputStreamReader(connection.getInputStream())
);

String inputLine;
StringBuffer response = new StringBuffer();
                        
while ((inputLine = inputBuffer.readLine()) != null) {
    response.append(inputLine);
}
inputBuffer.close();
                         
JSONObject search_object = new JSONObject(response.toString());
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

```java
String search_id = search_object.getString("id");

URL request = new URL(BASE_URL + "/news-searches/" + search_id + "/articles");
HttpsURLConnection connection = (HttpsURLConnection) request.openConnection();
 
connection.setRequestMethod("GET");
connection.setRequestProperty("authorization", auth_token);
connection.setRequestProperty("Content-Type", "application/json");
connection.setDoOutput(true);
			
BufferedReader inputBuffer = new BufferedReader(
    new InputStreamReader(connection.getInputStream())
);

String inputLine;
StringBuffer response = new StringBuffer();
 
while ((inputLine = inputBuffer.readLine()) != null) {
    response.append(inputLine);
}
inputBuffer.close();
		
JSONArray articles_response = (JSONArray)JSONValue.parse(response.toString());
```
The variable `articles_response` now contains a 


<div id='searchstats'/>
### Retrieving the statistics related to a search

```java
String bucket = "monthly";

URL request = new URL(BASE_URL + "/news-searches/" + search_id + "/stats/" + bucket);

String search_id = search_object.getString("id");

URL request = new URL(BASE_URL + "/news-searches/" + search_id + "/articles");
HttpsURLConnection connection = (HttpsURLConnection) request.openConnection();
 
connection.setRequestMethod("GET");
connection.setRequestProperty("authorization", auth_token);
connection.setRequestProperty("Content-Type", "application/json");
connection.setDoOutput(true);
			
BufferedReader inputBuffer = new BufferedReader(
    new InputStreamReader(connection.getInputStream())
);

String inputLine;
StringBuffer response = new StringBuffer();
 
while ((inputLine = inputBuffer.readLine()) != null) {
    response.append(inputLine);
}
inputBuffer.close();
		
JSONArray stats_json = (JSONArray)JSONValue.parse(response.toString());
```
