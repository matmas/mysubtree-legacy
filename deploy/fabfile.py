import os
import re
import sys
import fabric
from fabric.api import task, run, env, sudo, parallel, put, cd, local, prefix, execute, require
from fabric.context_managers import hide, show
from fabric.colors import green, yellow, blue
from jinja2 import Environment, PackageLoader
from fab.subtasks import (install_postgresql, 
                          install_postfix_gmail,
                          install_tools,
                          install_ssh_keys,
                          install_python_webapp,
                          install_unattended_upgrades,
                          netstat)
from fab.utils import (action,
                       ensure_dir,
                       ensure_user,
                       ensure_file, ensure_files, remove_file,
                       ensure_package, ensure_packages,
                       ensure_virtualenv, virtualenv,ensure_python_packages,
                       ensure_git_clone, update_git_clone,
                       ensure_executable)

import fab.utils
fab.utils.jinja2_env = Environment(loader=PackageLoader(__name__, "."))

env.hostname = "webserver"
env.admin_email = "riesz.martin@gmail.com"
env.gmail_account = "noreply@mysubtree.org"
env.gmail_password = open(os.path.expanduser("~/level1/credentials/%s" % env.gmail_account)).read().strip()
env.postgresql_version = "9.1"
env.default_ssl_certificate = "files/ssl-cert/www.mysubtree.org.pem.combined"
env.default_ssl_certificate_key = "files/ssl-cert/private/mysubtree.org.key"

env.project_name = "mysubtree"
env.project_server_name = "www.mysubtree.org"
env.project_ssl_certificate = "files/ssl-cert/www.mysubtree.org.pem.combined"
env.project_ssl_certificate_key = "files/ssl-cert/private/mysubtree.org.key"
env.project_port = 5000

#env.project_name = "mysubtreedev"
#env.project_server_name = "dev.mysubtree.org"
#env.project_ssl_certificate = "files/ssl-cert/dev.mysubtree.org.pem.combined"
#env.project_ssl_certificate_key = "files/ssl-cert/private/mysubtree.org.key"
#env.project_port = 5001

env.project_user = env.project_name
env.project_database = env.project_name
env.project_dir = "/srv/%s" % env.project_name
env.project_virtualenv = "%s/venv" % env.project_dir
env.project_checkout = "%s/checkout" % env.project_dir
env.project_logdir = "%s/log" % env.project_dir

env.project_repo = "git@bitbucket.org:matmas/mysubtree.git"
env.project_make = "./setup"
env.project_static_dir = "%s/src/mysubtree/web/static" % env.project_checkout
env.project_initdb = "cd src && python main_initdb.py"
env.project_process = "%s/bin/gunicorn -w 4 -b 127.0.0.1:%s --pythonpath src main_production" % (env.project_virtualenv, env.project_port)

env.project_dependencies = [
    "memcached", # cache server
    "libmemcached-dev", # pylibmc build dependency
    "libxslt1-dev", # pyquery build dependency
    "postgresql-server-dev-all", # psycopg2 build dependency
    "libcrack2-dev", # cracklib build dependency
    "tidy", # pytidylib runtime dependency
    "nodejs", # mysubtree wants to spawn node processes
    "unzip", # to be able to unzip famfamfam fonts
    "npm", # to install nodejs libraries
    "node-uglify", # to compress javascript
    "coffeescript", # to compile coffeescript into javascript
    "imagemagick", # to derive famfamfam icons into desaturated, resized, etc.
    "ruby1.9.1", # to be able to install compass
    #"python-lxml", # since compiling lxml demands high amount of memory
]

fabric.state.output.update({"stdout": False, "running": False}) # disable verbose output by default

@task
def staging():
    result = local('vagrant ssh-config', capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(r'IdentityFile\s+([^\n]+)', result)[0]
    env.pip_download_cache = "/vagrant/cache/pip"
    
@task
def production():
    env.hosts = ["ubuntu@www.mysubtree.org"]

@task
def deploy():
    install_tools()
    install_unattended_upgrades()
    ensure_packages(*env.project_dependencies)
    ensure_executable("compass", "sudo gem install compass --no-ri --no-rdoc") # another project dependency
    install_python_webapp()

@task
def test():
    with virtualenv(env.project_virtualenv):
        with cd(env.project_checkout):
            with show("stdout"):
                run("python src/main_testing.py")
