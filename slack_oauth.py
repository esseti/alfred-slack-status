import logging
import os
log = logging.getLogger()

# just creates the oauth with correct permission, manually so we skip 1 library
# there's a function on google functions to handle the rest of the flow.
# this url is 
client_id='3091729876.2525836761175'
scopes="user_scope=dnd:write,users.profile:write,users:write"
url = "https://slack.com/oauth/v2/authorize?client_id="+client_id+"&scope=&"+"scopes"
print(url)
