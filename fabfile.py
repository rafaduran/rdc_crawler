import os
import fabric.api as api
import fabric.contrib.files as files
import fabric.operations as operations
import fabric.context_managers as fcm
import fabric.contrib.console as console
from fabric.decorators import roles

HOME = os.getenv('HOME')

# local key files
api.env.key_filename = [
    '{0}/aws/rdc-test.pem'.format(HOME),
]


api.env.roledefs.update({
    'vagrant-host': ['ec2-79-125-34-189.eu-west-1.compute.amazonaws.com']})


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


def update_src(path=None):
    if not path:
        path = api.env.code_dir
    if local_changes():
        if not console.confirm("Not pushed changes have been found, continue?"):
            api.abort("Aborting...")

    with fcm.cd(path):
        api.run('git pull')
        install_venv()
        set_local_settings(dest='rdc_crawler/local/local_settings.py')


def bootstrap(path=None):
    if not path:
        path = api.env.code_dir
    install_external_deps()
    if not files.exists(api.env.code_dir):
        api.run('git clone git://github.com/rafaduran/rdc_crawler.git {0}'.\
                 format(path))
    update_src(path)


###################
# Vagrant methods #
###################
@roles('vagrant-host')
def _get_vagrant_config():
    """
    Parses vagrant configuration and returns it as dict of ssh parameters
    and their values
    """
    result = api.run('vagrant ssh_config', capture=True)
    conf = {}
    for line in iter(result.splitlines()):
        parts = line.split()
        conf[parts[0]] = ' '.join(parts[1:])

    return conf


@roles('vagrant-host')
def vprepare():
    """
    Installs Vagrant and Virtual Box 
    """
    api.put('tools/vprepare.sh','/tmp/',mirror_local_mode=True)
    with fcm.cd('/tmp/'):
        api.sudo('./vprepare.sh')
    
