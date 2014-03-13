import time
from owlin import owlin

owl = owlin({ 
    "email"     : "richard@owlin.com", 
    "password"  : "redacted" 
})

articles = owl.request({
    "method" : "get_articles",
    "value" : "filter:82512822dfe111e2a6d2001143dc2095",
    "args" : {
        "range" : {
            "epoch" : {
                "from" : time.time()-(86400*3)
                }
            }
        }
    })

for article in articles:
    print article['header']
