import fabric.api as fapi
import fabric.contrib.files as files
import fabric.context_managers as fcm

def set_local_settings(settings=None, path="/tmp/local_settings.py"):
    if not settings:
        if fapi.env.has_key('broker_port'):
            fapi.env.broker_port = int(fapi.env.broker_port)
            settings = fapi.env
    files.upload_template('rdc_crawler/local/local_settings.py.template', 
                     path, context=settings,use_jinja=True)


def install_venv(path=None):
    if path:
        fapi.run('cd {0}'.format(path))
    fapi.run('python tools/install_venv.py')


def bootstrap():
    if not files.exists(fapi.env.code_dir):
        fapi.run('git clone git://github.com/rafaduran/rdc_crawler.git {0}'.\
                 format(fapi.env.code_dir))

    with fcm.cd(fapi.env.code_dir):
        fapi.run('git pull')
        install_venv()
        set_local_settings(path='{0}/local/local_settings.py'.\
                           format(fapi.env.code_dir))