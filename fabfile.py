import fabric.api as api
import fabric.contrib.files as files
import fabric.operations as operations
import fabric.context_managers as fcm
import fabric.contrib.console as console
from fabric.decorators import roles
import fabric.contrib.project as project

api.env.roledefs = {}

for role in api.env.myroles.split():
    api.env.roledefs[role] = []

###################
# Vagrant methods #
###################
def _get_vagrant_hosts(path=None):
    if not path:
        path = api.env.vagrant_path

    result = api.local("cd {path} && vagrant status".format(path=path),
                       capture=True)
    hosts = []
    api.env.host_alive = {}
    for line in iter(result.splitlines()[2:-4]):
        parts = line.split()
        hosts.append(parts[0])
        api.env.host_alive[parts[0]] =\
            True if parts[1] == 'running' else False
    return hosts


def _get_vagrant_config(path=None):
    """
    Parses vagrant configuration and returns it as dict of ssh parameters
    and their values
    """
    if not path:
        path = api.env.vagrant_path
    hosts = _get_vagrant_hosts(path)
    conf = {}
    for host in hosts:
        if not api.env.host_alive[host]:
            api.local('cd {path} && vagrant up {host}'.format(host=host,
                                                           path=path))

        result = api.local('cd {path} && vagrant ssh_config {host}'.format(
                            host=host, path=path), capture=True)
        conf[host] = {}
        for line in iter(result.splitlines()):
            parts = line.split()
            conf[host][parts[0]] = ' '.join(parts[1:])

    return conf


def _vagrant():
    print("llega")
    api.env.settings = 'vagrant'
    api.env.conf = conf = _get_vagrant_config()
    api.env.key_filename = []
    api.env.hostnames = []
    for host in conf.keys():
        for role in api.env.roledefs.keys():
            hoststring = "{user}@{host}:{port}".format(
                        user=conf[host]['User'], host=conf[host]['HostName'],
                        port=conf[host]['Port'])
            if host.startswith(role):
                api.env.roledefs[role].append(hoststring)
        api.env.key_filename.append(conf[host]['IdentityFile'])
        api.env.all_hosts.append(hoststring)


def checks():
    with api.settings(warn_only=True):
        api.local("rm *.txt")
        api.local("tools/run_checks.sh")


def set_local_settings(settings=None, src='rdc_crawler/local/'
                       'local_settings.py.template',
                       dest='/tmp/local_settings.py'):
    if not settings:
        if api.env.has_key('broker_port'):
            api.env.broker_port = int(api.env.broker_port)
            settings = api.env
    files.upload_template(src, dest, context=settings,use_jinja=True)


def install_venv(path=None):
    if path:
        api.run('cd {0}'.format(path))
    api.run('python tools/install_venv.py')


def install_external_deps():
    operations.sudo("apt-get -y install libmemcached-dev libmysqlclient-dev"
             " libsqlite3-dev git")


def local_changes():
    branch = api.local("git branch",capture=True)[2:]
    remote = api.local("git remote show",capture=True)
    return bool(api.local("git diff {0}/{1}".format(remote,branch),
                           capture=True))

@api.roles('worker')
def update_src(path=None):
    project.rsync_project(remote_dir=api.env.code_dir,
                      exclude=("*.pyc", ".crawler-venv"))


def bootstrap(path=None):
    if not path:
        path = api.env.code_dir
    install_external_deps()
    if not files.exists(api.env.code_dir):
        api.run('git clone git://github.com/rafaduran/rdc_crawler.git {0}'.\
                 format(path))
    update_src(path)


@roles('vagrant-host')
def vprepare():
    """
    Installs Vagrant and Virtual Box 
    """
    api.put('tools/vprepare.sh','/tmp/',mirror_local_mode=True)
    with fcm.cd('/tmp/'):
        api.sudo('./vprepare.sh')


def show_settings(enviro=None, *args, **kwargs):
    if not enviro is None:
        globals()[enviro](*args, **kwargs)
    print(api.env)
