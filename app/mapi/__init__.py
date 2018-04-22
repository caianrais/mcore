# -*- coding: utf-8 -*-

# Standard library
import os

# Modules
from mapi.utils import Exit

# 3rd-party libraries
try:
    from flask import Flask
    from flask_migrate import Migrate
    from flask_sqlalchemy import SQLAlchemy

except ImportError as error:
    Exit.with_fail('Impossible to import 3rd-party libraries\n'
                   'Latest traceback: {0}' . format(error.args[0]))

# What kind of configuration should be used?
if os.environ.get('TEST_ENVIRON'):
    from config import Development as Config

else:
    from config import Production as Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from mapi import routes
from mapi import models
