from flask import Flask , render_template , request , redirect
from flask.views import View


import os
import subprocess
import validators
import pathlib
from pathlib import Path
import time
import json
import httplib2
import logging

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import requests

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

# from authentication.login import gcloudlogin
# from authentication.logout import gcloudlogout

app =  Flask(__name__)

deployment_list=[1,2,3,7,9,11]
resourse_list = [4,8,10]

content = None
credentials = ServiceAccountCredentials.from_json_keyfile_name('new-key.json',scopes='https://www.googleapis.com/auth/cloud-platform')

http = httplib2.Http()
http = credentials.authorize(http)

service = build("tasks", "v1", http=http)

Deployments_dict = {
    "Deployment_message":"The below resources were added successfully"
}

class get_parse:
  def get_projects():
      try:
        projects = (str(subprocess.check_output('gcloud projects list',shell=True))).split('\\r\\n')

        for i in range(1,len(projects)):
            projects_parsed.append(re.sub('  +', '\n', projects[i]))

        for j in range(0,len(projects_parsed)-1):
            Projects_dict.update( {"Projects "+str(j+1) : projects_parsed[j].split('\n')} )

        projects_json= json.dumps(Projects_dict)
        return projects_json
      except:
          logging.error('Could not get the project list')


  def get_deployment_output(cmnd):
      try:
        deployments_parse = (str(subprocess.check_output(cmnd,shell=True))).split('\\r\\n')
        Deployments_dict.update( {"Resources Added": deployments_parse[1:len(deployments_parse)-1]} )
        deployments_json = json.dumps(Deployments_dict)
        return deployments_json
      except:
          logging.error('Error in getting or parsing the deployments list')



@app.context_processor
def inject_user():
    try:
        account = (((str(subprocess.check_output('gcloud auth list',shell=True))).split('\\r\\n'))[2].split())[1]
    except:
        account=None
        logging.error('Error in getting the signed in account')
    return dict(value=account)


class deployment_page(View):
  def dispatch_request(self):
    try:
      return render_template('HTML/index.html')
    except:
      logging.error('Error rendering the template')

app.add_url_rule('/', view_func=deployment_page.as_view('deployment_page'))


class my_deployment_post(View):
  methods = ['POST']
  def dispatch_request(self):
    try:
        conf_file = request.form['config-file']
        instance = request.form['instance-name']

        valid=validators.url(conf_file)
        if(valid==True):
          clone = conf_file.split('/')
          git_url = clone[0]+'/'+clone[1]+'/'+clone[2]+'/'+clone[3]+'/'+clone[4]+'.git'
          print(git_url)
          dirpath = Path(os.path.abspath(os.getcwd()),clone[4])
          print(dirpath)
          if not (dirpath.exists() and dirpath.is_dir()):
            os.system("git clone "+git_url)
            time.sleep(5)
          for i in range(4, len(clone)-1):
            isFile = (os.path.isfile(clone[i]) or os.path.isdir(clone[i]))
            if(isFile):  
              os.chdir(clone[i])
              os.system('pwd')
              time.sleep(1)
          cmnd = "gcloud deployment-manager deployments create "+instance+" --config "+clone[len(clone)-1]
          print(["=" for i in range(0)])
          try: 
            print(get_parse.get_deployment_output(cmnd))
          except:
                Deployments_dict.update( {"Deployment_message":"Could not deploy your instance check logs for error"} )
                print(json.dumps(Deployments_dict))

        else:
            f = request.files['file']
            f.save(secure_filename(f.filename))
            cmnd ="gcloud deployment-manager deployments create "+instance+" --config "+ f.filename
            print(["=" for i in range(30)])
            try: 
                print(get_parse.get_deployment_output(cmnd))
            except:
                    Deployments_dict.update( {"Deployment_message":"Could not deploy your instance check logs for error"} )
                    print(json.dumps(Deployments_dict))
            #content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+instance,method="GET")
            #new_obj = json.loads(content[1])
            #print(new_obj)

        return render_template('HTML/response.html',response=Deployments_dict)
    except:
        logging.error('Error in my_deployment_post()')
app.add_url_rule('/', view_func=my_deployment_post.as_view('my_deployment_post'))


class api_calls(View):
  def dispatch_request(self):
    try:
      return render_template('HTML/apicalls.html')
    except:
      logging.error('Error rendering apicalls Template')
app.add_url_rule('/apicalls', view_func=api_calls.as_view('api_calls'))


class api_calls_post(View):
  methods = ['POST']
  def dispatch_request(self):
      try:
        x = request.form['select-api']
        project = request.form['project-name']
        deployment = request.form['deployment-name']
        resource = request.form['resource-name']

        if((int(x)) in deployment_list):
          if(int(x)==1):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="POST")
            

          elif(int(x)==2):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="DELETE")
            

          elif(int(x)==3):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="GET")
            new_obj = json.loads(content[1])
            

          elif(int(x)==7):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="PATCH")
            

          elif(int(x)==9):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment+'/setIamPolicy',method="POST")
            

          elif(int(x)==11):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="PUT")
            
            
        elif(int(x) in resourse_list):
          if(int(x)==4):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+resource+'/getIamPolicy',method="GET")
            

          if(int(x)==8):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+resource+'/setIamPolicy',method="POST")
            

          if(int(x)==10):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+resource+'/testIamPermissions',method="POST")
            

        else:
          if(int(x)==5):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments',method="POST")
            
          if(int(x)==6):
            content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments',method="GET")
            #json_data = eval(content)
        print(type(content))
        #new_obj = json.loads(content[1])
        #print(new_obj)#['deployments'][0]['name']
        return render_template('HTML/response.html',response=content)
      except:
          logging.error('Error in api_calls_post() method')
app.add_url_rule('/apicalls', view_func=api_calls_post.as_view('api_calls_post'))




class api_calls_project(View):
  def dispatch_request(self,project,id):
    try:
        x = id
        if(int(x)==5):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments',method="POST")
              

        if(int(x)==6):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments',method="GET")    
        return content
    
    except:
        logging.error("Error in api_calls_project() class")

app.add_url_rule('/apicalls/<project>/<int:id>', view_func=api_calls_project.as_view('api_calls_project'))

class api_calls_proj_deploy(View):
  def dispatch_request(self,project,deployment,id):
    try:
        x = id

        if(int(x)==1):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="POST")
          

        elif(int(x)==2):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="DELETE")
          

        elif(int(x)==3):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="GET")
          new_obj = json.loads(content[1])
          

        elif(int(x)==7):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="PATCH")
          

        elif(int(x)==9):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment+'/setIamPolicy',method="POST")
          

        elif(int(x)==11):
          content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+deployment,method="PUT")
        return content
    except:
        logging.error("Error in api_calls_proj_deploy() method")
    
app.add_url_rule('/apicalls/<project>/<deployment>/<int:id>', view_func=api_calls_proj_deploy.as_view('api_calls_proj_deploy'))


class api_calls_proj_resource(View):
  def dispatch_request(self,project,resource,id):
    try:
      x = id
      if(int(x)==4):
        content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+resource+'/getIamPolicy',method="GET")
        

      if(int(x)==8):
        content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+resource+'/setIamPolicy',method="POST")
        

      if(int(x)==10):
        content = http.request('https://www.googleapis.com/deploymentmanager/v2/projects/'+project+'/global/deployments/'+resource+'/testIamPermissions',method="POST")
        

      return render_template('HTML/apicalls.html')
    except:
      logging.error("Error in api_calls_proj_resource() method")

app.add_url_rule('/apicalls/<project>/<resource>/<int:id>', view_func=api_calls_proj_resource.as_view('api_calls_proj_resource'))


class gcloudlogin(View):
    def dispatch_request(self):
        try:
            os.system("gcloud auth login prudhvicareers@gmail.com")
            return render_template('HTML/index.html')
        except:
            logging.error("Error Trying to login")

app.add_url_rule('/gcloudlogin', view_func=gcloudlogin.as_view('gcloudlogin'))



class gcloudlogout(View):
    def dispatch_request(self):
        try:
            os.system("gcloud auth revoke")
            return render_template('HTML/index.html')
        except:
            logging.error("Error Trying to log out")
app.add_url_rule('/gcloudlogout', view_func=gcloudlogout.as_view('gcloudlogout'))


if __name__ == '__main__':
    app.run(debug = True,host="localhost",port=3000)
