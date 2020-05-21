# 导入Flask类
from flask import Flask
from flask import render_template
from flask import request
import requests
import json

app = Flask(__name__)

@app.route('/hook/<token>', methods = ['GET', 'POST'])
def deal_request(token):
    # GITLAB webhook配置： http://192.168.10.221:5000/hook/dc0c6bba93f0a63bce287d359cc465a4578113e9c1eafe60e9b8af886366c1b9
    if request.method == "GET":
        return 'not support get method'
    elif request.method == "POST":
        GITLAB = {}
        req = request.data
        GITLAB["CONTENT_TYPE"] = request.environ["CONTENT_TYPE"]
        GITLAB["GITLAB_EVENT"] = request.environ["HTTP_X_GITLAB_EVENT"]
        GITLAB_BODY = request.data.decode()
        app.logger.debug(GITLAB)
        app.logger.debug(GITLAB_BODY) 
        res = post_ding(token, GITLAB, json.loads(GITLAB_BODY))
        app.logger.debug(res)

        return res

def post_ding(token, head, req):
    headers={}
    headers['Content-Type']='application/json'
    url = "https://oapi.dingtalk.com/robot/send?access_token=%s" %token

    if head["GITLAB_EVENT"] == "Pipeline Hook":
        project = req["project"]["path_with_namespace"]
        commit = "[{sha}]({commit_url}): {message}".format(sha=req["commit"]["id"][0:8],commit_url=req["commit"]["url"],message=req["commit"]["message"])
        author = req["user"]["name"]
        ref = req["object_attributes"]["ref"]
        status = req["object_attributes"]["status"]
        pipline_id = req["object_attributes"]["id"]
               
        if status == "success":
            text = "<font color=#008000  face='Tahoma'>Pipeline Hook: {status}</font>\n\n <font size=1 face='Tahoma'>Project:  {project}</font>\n\n <font size=1 face='Tahoma'>Branch:  {ref}</font>\n\n <font size=1 face='Tahoma'>Author:  {author}</font>\n\n <font size=1 face='Tahoma'>Commit: </font>\n\n > {commit}\n\n <font size=1 face='Tahoma'>[See More in GitLab](http://git.iwellmass.com/{project}/pipelines/{pipline_id})</font>".format(project=project,author=author,ref=ref,status=status,commit=commit,pipline_id=pipline_id)
        else:
            text = "<font color=#FF0000  face='Tahoma'>Pipeline Hook: {status}</font>\n\n <font size=1 face='Tahoma'>Project:  {project}</font>\n\n <font size=1 face='Tahoma'>Branch:  {ref}</font>\n\n <font size=1 face='Tahoma'>Author:  {author}</font>\n\n <font size=1 face='Tahoma'>Commit: </font>\n\n > {commit}\n\n <font size=1 face='Tahoma'>[See More in GitLab](http://git.iwellmass.com/{project}/pipelines/{pipline_id})</font>".format(project=project,author=author,ref=ref,status=status,commit=commit,pipline_id=pipline_id)
        app.logger.debug(text)
        data =  {
                "msgtype": "markdown",
                "markdown": {
                    "title":"gitlab pipline %s" %status,
                    "text": "{text}".format(text=text)
                    }   
                }
        if status == "success" or status == "failed":
            res = requests.post(url, headers=headers, data=json.dumps(data)).text
        else:
            res = "pipline status is not success or failed"

    elif head["GITLAB_EVENT"] == "Push Hook":
        project = req["project"]["path_with_namespace"]
        ref = req["ref"].split("/")[-1]
        author = req["user_name"]
        commits_str = ''
        for commit in req["commits"]:
            short_id = commit["id"][0:8]
            message = commit["message"].split("\n\n")[0]
            commit_url = commit["url"]
            commits_str += " > [{short_id}]({commit_url}): {message} \n\n".format(short_id=short_id,commit_url=commit_url,message=message)
        text = "<font size=1 face='Tahoma'>Push Hook</font>\n\n<font size=1 face='Tahoma'>Project: {project}</font>\n\n<font size=1 face='Tahoma'>Branch:  {ref}</font>\n\n<font size=1 face='Tahoma'>Author:  {author}</font>\n\n<font size=1 face='Tahoma'>Commit: </font>\n\n{commits_str}".format(project=project,author=author,ref=ref,commits_str=commits_str)
        app.logger.debug(text)
        data =  {
                "msgtype": "markdown",
                "markdown": {
                    "title":"gitlab push info",
                    "text": "{text}".format(text=text)
                    }      
                }
        res = requests.post(url, headers=headers, data=json.dumps(data)).text
    else:
        res = "not supported  Hook type"

    return res


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

