import fabric.api as fapi
import fabric.contrib.files as files
import fabric.operations as operations
import fabric.context_managers as fcm
import fabric.contrib.console as console


def checks():
    fapi.local("rm *.txt")
    fapi.local("tools/run_checks.sh")


def set_local_settings(settings=None, src='rdc_crawler/local/'
                       'local_settings.py.template',
                       dest='/tmp/local_settings.py'):
    if not settings:
        if fapi.env.has_key('broker_port'):
            fapi.env.broker_port = int(fapi.env.broker_port)
            settings = fapi.env
    files.upload_template(src, dest, context=settings,use_jinja=True)


def install_venv(path=None):
    if path:
        fapi.run('cd {0}'.format(path))
    fapi.run('python tools/install_venv.py')


def install_external_deps():
    operations.sudo("apt-get -y install libmemcached-dev libmysqlclient-dev"
             " libsqlite3-dev git")


def local_changes():
    branch = fapi.local("git branch",capture=True)[2:]
    remote = fapi.local("git remote show",capture=True)
    return bool(fapi.local("git diff {0}/{1}".format(remote,branch),
                           capture=True))


def update_src(path=None):
    if not path:
        path = fapi.env.code_dir
    if local_changes():
        if not console.confirm("Not pushed changes have been found, continue?"):
            fapi.abort("Aborting...")

    with fcm.cd(path):
        fapi.run('git pull')
        install_venv()
        set_local_settings(dest='rdc_crawler/local/local_settings.py')


def bootstrap(path=None):
    if not path:
        path = fapi.env.code_dir
    install_external_deps()
    if not files.exists(fapi.env.code_dir):
        fapi.run('git clone git://github.com/rafaduran/rdc_crawler.git {0}'.\
                 format(path))
    update_src(path)
