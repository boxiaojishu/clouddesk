from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from novaclient import client
from deskclient.v1 import client as desk
from keystoneclient.auth.identity import v3
from keystoneclient import session
import os
import json

def get_keystone_creds():
        d = {}
        d['username'] = 'admin'
        d['password'] = 'admin'
        d['auth_url'] = 'http://192.168.0.70:35357/v3'
        d['project_name'] = 'admin'
        d['project_domain_id'] = "default"
        d['user_domain_id'] = "default"
        return d
def getNova():
        kd_creds = get_keystone_creds()
        auth = v3.Password(**kd_creds)
        sess = session.Session(auth=auth)
        nova = client.Client(2,session=sess)
        return nova

def getDesk():
    kd_creds = get_keystone_creds()
    auth = v3.Password(**kd_creds)
    sess = session.Session(auth=auth)
    deskapi=desk.Client('desk','desk','service','http://192.168.0.70:35357/v3')
    return deskapi

nova = getNova()
deskapi = getDesk()

class UserForm(forms.Form):
    username = forms.CharField(label='user',max_length=100)
    password = forms.CharField(label='password',widget=forms.PasswordInput())

def login(req):
    print req
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            opts = {"user_name": username}
            user = deskapi.users.get_user_by_name(opts);
            if user['deskusers'][0]['password'] == password:
                virtuald = deskapi.uservirtuals.get_virtual_by_user(opts);
                virtuals = virtuald['uservirtuals']
                return render_to_response('virtuallist.html',  {'data':virtuals},context_instance=RequestContext(req))
            #user = User.objects.filter(username__exact = username,password__exact = password)
            else:
                return HttpResponseRedirect('/login/')
    else:
        uf = UserForm()
    return render_to_response('login.html',{'uf':uf},context_instance=RequestContext(req))

def logincs(req):
    print req
    if req.method == 'POST':
        body=json.loads(req.body)
        print req.body
    if req.method == 'GET':
        print "it is hello"
    print "it is :"
    print req.body
    #body = urllib.unquote(req.body)
    print body
    username=body.get('username','')
    password=body.get('password','')
    print password
    opts = {"user_name": username}
    user = deskapi.users.get_user_by_name(opts)
    print user['deskusers'][0]['password']
    if user['deskusers'][0]['password'] == password:
        virtuald = deskapi.uservirtuals.get_virtual_by_user(opts);
        virtuals = virtuald['uservirtuals']
        resp = json.dumps(virtuals)
        return HttpResponse(resp)
    else:
        return HttpResponse("") 

def index(req):
    username = req.COOKIES.get('username','')
    return render_to_response('index.html' ,{'username':username})

def logout(req):
    response = HttpResponse('logout !!')
    response.delete_cookie('username')
    return response

def getspices(req):
    print req
    virtual=req.GET
    print virtual
    virtualid=virtual.get('id','')
    print virtualid
    #nova.servers.start(virtualid)
    spices = nova.servers.get_spice_console(virtualid,'spice')
    spice=spices.get('console','')
    print spice
    resp = json.dumps(spice)
    print resp
    return HttpResponse(resp)
    #nova.servers.start('086e6358-d166-47e0-96fd-8204dc4275b0')
