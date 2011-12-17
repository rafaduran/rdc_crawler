#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
rdc-crawler Fabric deployment script
"""
import sys
import fabric.api as api
import fabric.contrib.files as files
import fabric.operations as operations
import fabric.context_managers as context
import fabric.contrib.console as console
from fabric.decorators import roles, parallel, runs_once, task
import fabric.contrib.project as project

try:
    import fabricrc
except ImportError:
    print("No fabricrc.py configuration file could be found,"
          "  please provide one")
    sys.exit()

# Source configuration
for flag in dir(fabricrc):
    if not flag.startswith('__'):
        api.env[flag.lower()] = getattr(fabricrc, flag)
api.env.settings = 'global'
api.env.no_keys = True
api.env.no_agent = True


def value_or_take_from_env(value, string):
    if value is None:
        value = string.format(**api.env)
    return value


@task
def checks():
    """
    Runs pep8 and pylint checkers
    """
    with api.settings(warn_only=True):
        api.local("rm *.txt")
        api.local("tools/run_checks.sh")

@task
def vagrant_prepare():
    """
    Installs Vagrant and Virtual Box
    """
    api.local('sudo tools/vprepare.sh')


@task
@roles('worker')
@parallel
def configure_workers(src=None, dest=None,**kwargs):
    """
    Updates local_settings.py on worker nodes. Default values are taken from
    configuration file and any given keyword argument will override default
    settings.
    """
    src = value_or_take_from_env(src,
        'rdc_crawler/local/local_settings.py.template')
    dest = value_or_take_from_env(dest,
        '{code_dir}/rdc_crawler/local/local_settings.py')
    conf = api.env
    if kwargs:
        conf.update(kwargs)
    files.upload_template(src, dest, context=conf, use_jinja=True)


@task
@roles('worker')
@parallel
def update_src(path=None, src=None, delete=False):
    """
    Synchronizes workers with local changes via rsync
    """
    path = value_or_take_from_env(path, "{code_dir}")
    project.rsync_project(local_dir='.', remote_dir=path, delete=delete,
                      exclude=("*.pyc", "whoosh", ".crawler-venv", ".git",
                               "deploy", ".gitmodules", ".settings*",
                               "rdc_crawler/local/*"))


@task
def show_settings(*args):
    """
    Prints settings
    """
    if args:
        for arg in args:
            print('{arg}: {value}'.format(arg=arg, value=api.env[arg]))
    else:
        print(api.env)


@task
@roles('worker')
@parallel
def celery(command='start'):
    """
    Manages celery workers daemon
    """
    operations.require('settings', provided_by=[api.env.enviro])
    api.sudo("service celery {command}".format(command=command))

@task
@parallel
@roles('worker')
def log():
    """
    Shows workers Celery log until Ctrl-c is pressed
    """
    try:
        api.run("tail -f /var/log/celery/celery.log")
    except KeyboardInterrupt:
        pass

@task
def test(apps=['crawler']):
    """
    Run tests for selected applications, default just 'crawler'
    """
    api.local("tools/with_venv.sh python rdc_crawler/manage.py test {apps}".\
              format(apps=' '.join([app for app in apps])))
