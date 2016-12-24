# -*- coding: utf-8 -*-

from flask import current_app
from flask.ext.script import Manager

from schoool.app import create_app


manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=True)


@manager.shell
def make_shell_context():
    return {
        'app': current_app,
    }


if __name__ == '__main__':
    manager.run()
