from fabric.api import task, show, local, run, sudo, require, env, cd
from fabric.colors import blue
from fabric.contrib.files import exists
from fab.utils import (action, shell_env,
                       ensure_dir,
                       ensure_file, ensure_files, remove_file,
                       ensure_user, ensure_group_membership,
                       ensure_package, ensure_packages,
                       ensure_virtualenv, virtualenv,ensure_python_packages,
                       ensure_postgresql_user, ensure_postgresql_db, ensure_postgresql_cluster,
                       ensure_git_clone, update_git_clone,
                       ensure_executable)

@task
def netstat():
    with show("stdout"):
        sudo("netstat -ltupn")

def install_unattended_upgrades():
    require("admin_email")

    ensure_packages(
        "unattended-upgrades",
        "update-notifier-common", # not sure it it is needed (it provides the default /etc/apt/apt.conf.d/10periodic)
    )
    ensure_file(
        src="templates/apt.conf.d/10periodic",
        dest="/etc/apt/apt.conf.d/10periodic",
        owner="root",
        group="root",
        use_sudo=True,
    )

    ensure_file(
        src="templates/apt.conf.d/50unattended-upgrades",
        dest="/etc/apt/apt.conf.d/50unattended-upgrades",
        owner="root",
        group="root",
        use_sudo=True,
        use_templating=True,
    )
    
    ensure_package("apticron")

    ensure_file(
        src="templates/apticron.conf",
        dest="/etc/apticron/apticron.conf",
        owner="root",
        group="root",
        use_sudo=True,
        use_templating=True,
    )

#def install_nagios_client():
    #require("nagios_server_ip")
    
    #ensure_package("nagios-nrpe-server")
    
    #def nagios_nrpe_server_reload():
        #action("Reaload nagios nrpe server", sudo("service nagios-nrpe-server reload"))
    
    #ensure_file(
        #src="templates/nagios/nrpe.cfg",
        #dest="/etc/nagios/nrpe.cfg",
        #use_sudo=True,
        #use_templating=True,
        #owner="root",
        #group="root",
        #on_change=nagios_nrpe_server_reload
    #)
    
    #env.root_device = run("mount | grep 'on / ' | sed 's| .*||'")
    #assert env.root_device.startswith("/") and exists(env.root_device)
    
    #ensure_file(
        #src="templates/nagios/custom.cfg",
        #dest="/etc/nagios/nrpe.d/custom.cfg",
        #use_sudo=True,
        #use_templating=True,
        #owner="root",
        #group="root",
        #on_change=nagios_nrpe_server_reload
    #)

def vagrant_up():
    with show("stdout"):
        action("Vagrant up", local("vagrant up"))

def uname():
    with show("stdout"):
        run("uname -a")

def update_apt():
    action("APT update", sudo("apt-get update"))

def install_postgresql():
    require("postgresql_version", "project_user")
    
    def _ensure_utf8_postgresql_cluster(should_ask_before_change=False):
        ensure_postgresql_cluster(version=env.postgresql_version, locale="en_US.utf8", should_ask_before_change=should_ask_before_change)
    
    ensure_package("postgresql", on_change=_ensure_utf8_postgresql_cluster)
    
    _ensure_utf8_postgresql_cluster(should_ask_before_change=True)
    
    def restart_postgresql():
        action("Postgresql restart", sudo("service postgresql restart"))
    
    ensure_files([
            "postgresql.conf",
            "pg_hba.conf",
        ],
        src_dir="templates/postgresql",
        dest_dir="/etc/postgresql/%s/main" % env.postgresql_version,
        use_sudo=True,
        use_templating=True,
        owner="postgres",
        group="postgres",
        on_change=restart_postgresql,
    )

def install_postfix_gmail():
    
    require("hostname", "gmail_account", "gmail_password")
    
    ensure_packages(
        "postfix", # to send e-mail
        "ca-certificates", # to send e-mail through GMail
        "mailutils", # Testing:
                     #    echo message_body | mail --to SOME.ADDRESS@gmail.com -s message_subject
                     # Show postfix queue:
                     #    mailq
                     # Empty queue:
                     #    sudo postsuper -d ALL
                     # Print what is going on:
                     #    sudo tail -f /var/log/mail.log
    )
    
    def restart_postfix():
        action("Restart postfix", sudo("service postfix restart"))
    
    ensure_file(src="templates/postfix/main.cf", dest="/etc/postfix/main.cf", use_sudo=True, use_templating=True, owner="root", group="root", on_change=restart_postfix)
    
    def rehash_sasl_passwd():
        action("Rehash sasl_passwd", sudo("postmap hash:/etc/postfix/sasl_passwd"))
    
    ensure_file(src="templates/postfix/sasl_passwd", dest="/etc/postfix/sasl_passwd", use_sudo=True, mode=600, owner="root", group="root", use_templating=True, on_change=rehash_sasl_passwd)

def install_advanced_tools():
    def update_apt_file():
        action("Update apt-file", sudo("apt-file update"))
    
    ensure_package("apt-file", on_change=update_apt_file)

def install_tools():
    ensure_packages(
        "vim",  # text editor
        "htop", # process viewer
        "lynx", # web browser
        "mutt", # e-mail client
    )

def install_ssh_keys():
    ensure_files(["known_hosts", "id_rsa", "id_rsa.pub"], src_dir="files", dest_dir=".ssh", mode=600)

def install_python_webapp():
    require(
        "project_dir", "project_virtualenv", "project_checkout", "project_repo", "project_name", "project_user", "project_process", "project_static_dir",
        "project_server_name", "project_ssl_certificate", "project_ssl_certificate_key", "project_database", "project_make", "project_initdb", "project_port", "project_logdir",
        "default_ssl_certificate", "default_ssl_certificate_key"
    )
    
    ensure_user(env.project_user)
    
    install_postgresql()
    ensure_postgresql_user(env.user, superuser=True)
    ensure_postgresql_db("test")
    ensure_postgresql_user(env.project_user)
    ensure_postgresql_db(env.project_user)
    

    install_postfix_gmail()
    
    install_ssh_keys()
    
    ensure_packages(
        "nginx", # reverse proxy webserver
        "git-core", # to get the code
        "python-virtualenv", # to create virtualenv
        "supervisor", # for keeping the gunicorn running
        "python-dev", # dependency of many python libraries
    )
    
    ensure_dir(
        env.project_dir,
        owner=env.user,
        use_sudo=True,
    )
    
    ensure_dir(
        env.project_logdir,
        owner=env.user,
    )
    
    ensure_virtualenv(env.project_virtualenv)
    
    def restart_nginx():
        action("Restart nginx", sudo("service nginx restart"))
    
    remove_file("/etc/nginx/sites-enabled/default", use_sudo=True, on_change=restart_nginx)
    
    def reload_supervisord():
        action("Supervisord reload", sudo("supervisorctl reread && supervisorctl update"))
        action("Supervisord restart all", sudo("supervisorctl restart all"))
        

    def make_project():
        with virtualenv(env.project_virtualenv):
            ensure_python_packages(env.project_checkout)
        
        with show("stdout"):
            with virtualenv(env.project_virtualenv):
                with cd(env.project_checkout):
                    action("Making project with %s" % blue(env.project_make), run(env.project_make))
                    
                    with shell_env(DATABASE_URI="postgresql:///%s" % env.project_database):
                        action("Initdb project with %s as user %s" % (blue(env.project_initdb), blue(env.project_user)), sudo(env.project_initdb, user=env.project_user))

        reload_supervisord()
    
    ensure_git_clone(
        env.project_checkout,
        env.project_repo,
        on_change=make_project,
    )
    
    # project SSL certificate
    ensure_file(
        src=env.project_ssl_certificate,
        dest="%s/ssl.pem" % env.project_dir,
        on_change=restart_nginx,
    )

    # project SSL private key
    ensure_file(
        src=env.project_ssl_certificate_key,
        dest="%s/ssl.key" % env.project_dir,
        owner="root",
        group="ssl-cert",
        mode=640,
        use_sudo=True,
        on_change=restart_nginx,
    )
    
    # default SSL certificate
    ensure_file(
        src=env.default_ssl_certificate,
        dest="/etc/ssl/certs/default.pem",
        owner="root",
        group="root",
        use_sudo=True,
        on_change=restart_nginx,
    )

    # default SSL private key
    ensure_file(
        src=env.default_ssl_certificate_key,
        dest="/etc/ssl/private/default.key",
        owner="root",
        group="ssl-cert",
        mode=640,
        use_sudo=True,
        on_change=restart_nginx,
    )
    
    ensure_dir("/srv/default", use_sudo=True)
    ensure_file(
        src="templates/nginx/index.html",
        dest="/srv/default/index.html",
        use_sudo=True,
        on_change=restart_nginx,
    )
    
    ensure_file(
        src="templates/nginx/default.conf",
        dest="/etc/nginx/conf.d/_default.conf",
        use_templating=True,
        use_sudo=True,
        on_change=restart_nginx,
    )
    
    ensure_file(
        src="templates/nginx/project.conf",
        dest="/etc/nginx/conf.d/%s.conf" % env.project_name,
        use_templating=True,
        use_sudo=True,
        on_change=restart_nginx,
    )
    
    ensure_file(
        src="templates/supervisord.conf",
        dest="/etc/supervisor/conf.d/%s.conf" % env.project_name,
        use_sudo=True,
        owner="root",
        group="root",
        use_templating=True,
        on_change=reload_supervisord,
    )
    
    update_git_clone(env.project_checkout, on_change=make_project)
    make_project()
    