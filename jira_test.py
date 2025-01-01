import re

from jira import JIRA
from config.auto_search_dir import data_config
from send_to_telegram_email.send_to_TG_email import send_to_telegram
import urllib3


JiraLogin = data_config["JiraOptions"]["JiraLogin"]
JiraPassword = data_config["JiraOptions"]["JiraPassword"]
JiraAddress = data_config["JiraOptions"]["JiraAddress"]
jira = JIRA(JiraAddress,basic_auth=(JiraLogin, JiraPassword))


# Get an issue.
issue = jira.issue("GSAA-128727", fields='comment')

# Find all comments made by Atlassians on this issue.
atl_comments = [
    comment
    for comment in issue.fields.comment.comments
    if re.search(r"fokinkv$", comment.author.key)
]
print(atl_comments)