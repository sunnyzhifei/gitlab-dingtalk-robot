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
        job_id = str(req["builds"][0]["id"])
        job_url = "http://git.xxx.com/" + project + "/-/jobs/" + job_id
        job = "[{job_id}]({job_url})".format(job_id=job_id, job_url=job_url)
               
        if status == "success":
            text = "<font color=#008000  face='Tahoma'>Pipeline Hook: {status}</font>\n\n <font size=1 face='Tahoma'>Project:  {project}</font>\n\n <font size=1 face='Tahoma'>Branch:  {ref}</font>\n\n <font size=1 face='Tahoma'>Author:  {author}</font>\n\n <font size=1 face='Tahoma'>JobId:  {job}</font>\n\n <font size=1 face='Tahoma'>Commit: </font>\n\n > {commit}\n\n <font size=1 face='Tahoma'>[See More in GitLab](http://git.xxx.com/{project}/pipelines/{pipline_id})</font>".format(project=project,author=author,ref=ref,status=status,commit=commit,pipline_id=pipline_id,job=job)
        else:
            text = "<font color=#FF0000  face='Tahoma'>Pipeline Hook: {status}</font>\n\n <font size=1 face='Tahoma'>Project:  {project}</font>\n\n <font size=1 face='Tahoma'>Branch:  {ref}</font>\n\n <font size=1 face='Tahoma'>Author:  {author}</font>\n\n <font size=1 face='Tahoma'>JobId:  {job}</font>\n\n <font size=1 face='Tahoma'>Commit: </font>\n\n > {commit}\n\n <font size=1 face='Tahoma'>[See More in GitLab](http://git.xxx.com/{project}/pipelines/{pipline_id})</font>".format(project=project,author=author,ref=ref,status=status,commit=commit,pipline_id=pipline_id,job=job)
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
    elif head["GITLAB_EVENT"] == "Merge Request Hook":
        app.logger.debug(req)
        file = open("dingUser.json",'r',encoding='utf-8')
        ding_user = json.load(file)
        file.close()

        state = req["object_attributes"]["state"]
        title = req["object_attributes"]["title"]
        description = req["object_attributes"]["description"]
        project = req["project"]["path_with_namespace"]
        mergeUrl = req["object_attributes"]["url"]
        author = req["user"]["name"]
        assignees = req.get("assignees")
        assignee = ''
        atMobiles = []
        atMobiles_string = ''
        if assignees:
            for a in assignees:
                atMobiles.append(ding_user.get(a.get("username")))
                assignee += a.get("name") + " "
        if atMobiles:
            for mobile in atMobiles:
                atMobiles_string += "@" + mobile + " "
        if state == "merged":
            atMobiles_string = ""
        source_branch = req["object_attributes"]["source_branch"]
        target_branch = req["object_attributes"]["target_branch"]
        text = "<font size=1 face='Tahoma'>Merge Request Hook</font>\n\n<font size=1 face='Tahoma'>Title: [{title}]({mergeUrl})</font>\n\n<font size=1 face='Tahoma'>Description:  {description}</font>\n\n<font size=1 face='Tahoma'>Project:  {project}</font>\n\n<font size=1 face='Tahoma'>Author:  {author}</font>\n\n<font size=1 face='Tahoma'>Assignee: {assignee}</font>\n\n<font size=1 face='Tahoma'>Source_branch:  {source_branch}</font>\n\n<font size=1 face='Tahoma'>Target_branch:  {target_branch}</font>\n\n<font size=1 face='Tahoma'>State:  {state}</font>\n\n<font size=1 face='Tahoma'>{atMobiles_string}</font>\n\n".format(title=title,mergeUrl=mergeUrl,description=description,project=project,author=author,assignee=assignee,source_branch=source_branch,target_branch=target_branch,state=state,atMobiles_string=atMobiles_string)
        app.logger.debug(text)
        
        data =  {
                "msgtype": "markdown",
                "markdown": {
                    "title":"gitlab merge request event" ,
                    "text": "{text}".format(text=text)
                    },
                "at": {
                    "atMobiles": atMobiles,
                    "isAtAll": False
                }   
                }
        print(data)
        res = requests.post(url, headers=headers, data=json.dumps(data)).text
    else:
        res = "not supported  Hook type"

    return res


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

