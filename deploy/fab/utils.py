import hashlib
import fabric
import inspect
from StringIO import StringIO
from fabric.api import run, sudo, local, env, prefix, cd
from fabric.context_managers import hide, show
from fabric.contrib.files import exists
from fabric.colors import green, yellow, blue
import cuisine
from contextlib import contextmanager

def action(name, result=None):
    print "[%s]" % env.host_string,
    
    #print inspect.stack()[1][3]
    
    if type(result) == bool:
        is_changed = result
        if is_changed:
            print yellow("changed"),
        else:
            print green("ok"),
    else:
        print yellow("done"),
    
    print name

#-------------------------------------------------------------------------------
# Directories:
#-------------------------------------------------------------------------------

def ensure_dir(path, **kwargs):
    is_changed = _ensure_dir(path, **kwargs)
    action("Create directory %s" % blue(path), is_changed)
    
def _ensure_dir(path, owner=None, mode=None, use_sudo=False):
    run_or_sudo = sudo if use_sudo else run
    is_changed = False
    if not exists(path):
        run_or_sudo('mkdir -p "%s"' % path)
        is_changed = True
    
    if owner:
        dir_owner = run('stat -c %%U "%s"' % path)
        if dir_owner != owner:
            sudo('chown %s "%s"' % (owner, path))
            is_changed = True
            
    if mode:
        dir_mode = run('stat -c %%a "%s"' % path)
        if dir_mode != str(mode):
            run_or_sudo('chmod %s "%s"' % (mode, path))
            is_changed = True
    
    return is_changed

#-------------------------------------------------------------------------------
# Files:
#-------------------------------------------------------------------------------

def ensure_files(files, src_dir, dest_dir, **kwargs):
    for file in files:
        ensure_file(
            src="%s/%s" % (src_dir, file),
            dest="%s/%s" % (dest_dir, file),
            **kwargs
        )

def ensure_file(src, dest, on_change=None, **kwargs):
    is_changed = _ensure_file(src, dest, **kwargs)
    action("Put file %s" % blue(dest), is_changed)
    
    if is_changed and on_change:
        on_change()

def _ensure_file(src, dest, owner=None, group=None, mode=None, use_templating=False, use_sudo=False, **kwargs):
    run_or_sudo = sudo if use_sudo else run
    if use_templating:
        src_content = jinja2_env.get_template(src).render(env=env)
    else:
        src_content = open(src, 'rb').read()
    src_hash = hashlib.md5(src_content).hexdigest()
    is_changed = False
    if not exists(dest, use_sudo) or src_hash != _file_md5(dest, use_sudo):
        if use_templating:
            fabric.operations.put(StringIO(src_content), dest, use_sudo=use_sudo, **kwargs)
        else:
            fabric.operations.put(src, dest, mirror_local_mode=True, use_sudo=use_sudo, **kwargs)
        is_changed = True
        assert exists(dest, use_sudo)
        _assertEqual(src_hash, _file_md5(dest, use_sudo))
        
    if owner:
        get_owner_cmd = 'stat -c %%U "%s"' % dest
        dest_owner = run_or_sudo(get_owner_cmd)
        if dest_owner != owner:
            run_or_sudo('chown %s "%s"' % (owner, dest))
            is_changed = True
            dest_owner = run_or_sudo(get_owner_cmd)
            _assertEqual(dest_owner, owner)
    
    if group:
        get_group_cmd = 'stat -c %%G "%s"' % dest
        dest_group = run_or_sudo(get_group_cmd)
        if dest_group != group:
            run_or_sudo('chgrp %s "%s"' % (group, dest))
            is_changed = True
            dest_group = run_or_sudo(get_group_cmd)
            _assertEqual(dest_group, group)
    
    if mode:
        get_mode_cmd = 'stat -c %%a "%s"' % dest
        file_mode = run_or_sudo(get_mode_cmd)
        if file_mode != str(mode):
            run_or_sudo('chmod %s "%s"' % (mode, dest))
            is_changed = True
            file_mode = run_or_sudo(get_mode_cmd)
            _assertEqual(file_mode, str(mode))
    
    return is_changed

def remove_file(path, use_sudo=False, on_change=None):
    run_or_sudo = sudo if use_sudo else run
    is_changed = False
    if exists(path, use_sudo):
        run_or_sudo('rm "%s"' % path)
        assert not exists(path, use_sudo)
        is_changed = True
    action("Remove file %s" % blue(path), is_changed)
    if is_changed and on_change:
        on_change()

#-------------------------------------------------------------------------------
# Packages:
#-------------------------------------------------------------------------------

def ensure_package(package, on_change=None):
    is_changed = not cuisine.package_ensure(package)
    action("Install package %s" % blue(package), is_changed)
    if is_changed and on_change:
        on_change()

def ensure_packages(*packages):
    for package in packages:
        ensure_package(package)

def ensure_ppa_repo(repo, on_change=None):
    """
    Example:
    ensure_package("python-software-properties") # to be able to add ppa repositories
    ensure_ppa_repo("chris-lea/node.js", on_change=update_apt)
    """
    is_changed = False
    distrib_codename = run(". /etc/lsb-release; echo $DISTRIB_CODENAME")
    needed_file = "/etc/apt/sources.list.d/%s-%s.list" % (repo.replace("/", "-").replace(".", "_"), distrib_codename)
    needs_change = not exists(needed_file)
    if needs_change:
        sudo("add-apt-repository --yes ppa:%s" % repo)
        is_changed = True
        assert exists(needed_file)
    action("Add PPA repo %s" % repo, is_changed)
    if is_changed and on_change:
        on_change()


#-------------------------------------------------------------------------------
# Python packages:
#-------------------------------------------------------------------------------

def ensure_virtualenv(path, system_site_packages=False):
    is_missing = not exists(path)
    if is_missing:
        options = "--system-site-packages" if system_site_packages else ""
        run('virtualenv %s --python=python2.7 %s' % (options, path)) # no site packages -- ignore system-wide installed python packages
        assert exists(path)
    action("Create virtualenv in %s" % blue(path), is_missing)

def ensure_python_packages(project_dir):
    """
    Installs python modules from requirements.txt in project_dir into current virtualenv
    """
    test_cmd = "pip install -r %s/requirements.txt | grep -v -e '^Requirement already satisfied' -e '^Cleaning up...'; true" % project_dir
    
    shell_env_vars = {}
    if "pip_download_cache" in env:
        shell_env_vars = {"PIP_DOWNLOAD_CACHE": env.pip_download_cache}
    
    with show("stdout"):
        with shell_env(**shell_env_vars):
            if run(test_cmd) == "":
                is_changed = False
            else:
                is_changed = True
            _assertEqual(run(test_cmd), "")
            action("Install python packages from requirements.txt in %s" % blue(project_dir), is_changed)

#-------------------------------------------------------------------------------
# Git:
#-------------------------------------------------------------------------------

def ensure_git_clone(path, repo, on_change=None):
    is_missing = not exists(path)
    is_changed = False
    if is_missing:
        run('git clone %s %s' % (repo, path))
        assert exists(path)
        is_changed = True
    action("Create git clone of %s in %s" % (blue(repo), blue(path)), is_changed)
    if is_changed and on_change:
        with cd(path):
            on_change()

def update_git_clone(path, on_change=None):
    assert exists(path)
    with cd(path):
        run("git clean -fd") # forget local modifications
        no_change_result = "Already up-to-date."
        is_changed = run("git pull") != no_change_result # download and merge remote changes
        if is_changed:
            _assertEqual(run("git pull"), no_change_result)
        action("Update git clone", is_changed)
        if is_changed and on_change:
            on_change()

#-------------------------------------------------------------------------------
# Postgresql:
#-------------------------------------------------------------------------------

def ensure_postgresql_user(user, superuser=False):
    test_cmd = "psql -tAc 'SELECT rolname FROM pg_roles'"
    users = sudo(test_cmd, user="postgres").split()
    is_changed = False
    if user not in users:
        sudo("createuser -s '%s'" % user, user="postgres")
        is_changed = True
        users = sudo(test_cmd, user="postgres").split()
        assert user in users

    test_cmd = 'psql -tAc "SELECT rolsuper FROM pg_roles WHERE rolname=\'%s\'"' % user
    is_superuser = sudo(test_cmd, user="postgres") == "t"
    if is_superuser != superuser:
        flag = "SUPERUSER" if superuser else "NOSUPERUSER"
        sudo("psql -c 'ALTER USER %s WITH %s;'" % (user, flag), user="postgres")
        is_changed = True
        is_superuser = sudo(test_cmd, user="postgres") == "t"
        _assertEqual(is_superuser, superuser)
        
    action("Create postgresql user %s" % blue(user), is_changed)

def ensure_postgresql_db(database):
    test_cmd = "psql -tAc 'SELECT datname FROM pg_database'"
    databases = sudo(test_cmd, user="postgres").split()
    is_changed = False
    if database not in databases:
        sudo("createdb '%s'" % database, user="postgres")
        is_changed = True
        databases = sudo(test_cmd, user="postgres").split()
        assert database in databases
    action("Create postgresql database %s" % blue(database), is_changed)

def ensure_postgresql_cluster(version, locale, should_ask_before_change):
    test_cmd = "psql -tAc 'SHOW LC_COLLATE'"
    lc_collate = sudo(test_cmd, user="postgres")
    needs_change = lc_collate != locale
    
    if needs_change:
        if should_ask_before_change and not fabric.contrib.console.confirm("Are you sure you want to recreate the whole postgresql cluster?"):
            sys.exit()
        sudo("pg_dropcluster --stop %s main" % version)
        sudo("pg_createcluster --locale=%s --start %s main" % (locale, version))
        lc_collate = sudo(test_cmd, user="postgres")
        _assertEqual(lc_collate, locale)
    action("Create postgresql cluster", needs_change)

#-------------------------------------------------------------------------------
# User:
#-------------------------------------------------------------------------------

def ensure_user(user):
    test_cmd = "getent passwd | egrep '^%s:'" % user
    is_changed = False
    needs_change = not run(test_cmd, quiet=True).succeeded
    if needs_change:
        sudo("useradd '%s'" % user)
        is_changed = True
        assert run(test_cmd, quiet=True).succeeded
    action("Add user %s" % blue(user), is_changed)

def ensure_group_membership(user, group):
    test_cmd = "groups '%s' | egrep '\\b%s\\b'" % (user, group)
    is_changed = False
    needs_change = not run(test_cmd, quiet=True).succeeded
    if needs_change:
        sudo("gpasswd -a '%s' '%s'" % (user, group))
        is_changed = True
        assert run(test_cmd, quiet=True).succeeded
    action("Add user %s to the group %s" % (blue(user), blue(group)), is_changed)

#-------------------------------------------------------------------------------
# Custom commands:
#-------------------------------------------------------------------------------

def ensure_executable(executable, command, use_sudo=False):
    run_or_sudo = sudo if use_sudo else run
    is_changed = False
    test_cmd = 'type -P "%s" &>/dev/null || ls "%s" &>/dev/null' % (executable, executable)
    is_missing = not run(test_cmd, quiet=True).succeeded
    if is_missing:
        run_or_sudo(command)
        is_changed = True
        is_missing = not run(test_cmd, quiet=True).succeeded
        assert not is_missing
    action("install executable %s" % executable, is_changed)

#-------------------------------------------------------------------------------
# Context managers:
#-------------------------------------------------------------------------------

@contextmanager
def virtualenv(path):
    with prefix("source %s/bin/activate" % path):
        yield

@contextmanager
def shell_env(**env_vars):
    def set_shell_env(**env_vars):
        env_vars_str = ' '.join('{0}={1}'.format(key, value)
                            for key, value in env_vars.items())
        env['shell'] = '{0} {1}'.format(env_vars_str, env["shell"])
    orig_shell = env['shell']
    set_shell_env(**env_vars)
    yield
    env['shell'] = orig_shell
    
#-------------------------------------------------------------------------------
# Utils:
#-------------------------------------------------------------------------------

def _file_md5(path, use_sudo=False):
    run_or_sudo = sudo if use_sudo else run
    return run_or_sudo('md5sum "%s"' % (path)).split()[0].strip()

def _assertEqual(a, b):
    if a != b:
        print "%s != %s" % (a, b)
    assert a == b