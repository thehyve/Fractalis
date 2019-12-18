Fractalis
=========

|Build status|

.. |Build status| image:: https://travis-ci.org/thehyve/Fractalis.svg?branch=dev
   :alt: Build status
   :target: https://travis-ci.org/thehyve/Fractalis/branches


*This repository is used to add improvements and features developed at The Hyve and contribute them to the original `Fractalis <https://github.com/LCSB-BioCore/Fractalis>`__ repository.*

About
~~~~~

This is the back-end component of the Fractalis project. It is a
computational node that is responsible for the MicroETL process and the
execution of analytical tasks. See https://fractalis.lcsb.uni.lu/

Demo
~~~~

Please have a look at this playlist to see a demo of the visual aspects
of Fractalis:
`Playlist <https://www.youtube.com/playlist?list=PLNvp9GB9uBmH1NNAf-qTyj_jN2aCPISFU>`__.

Installation (Docker)
~~~~~~~~~~~~~~~~~~~~~

The easiest and most convenient way to deploy Fractalis is using Docker.
All necessary information can be found `here <https://github.com/thehyve/Fractalis/tree/dev/docker>`__.

Installation (Manual)
~~~~~~~~~~~~~~~~~~~~~

If you do not want to use docker or want a higher level of control of
the several components, that's fine. In fact it isn't difficult to setup
Fractalis manually:

-  Install and run `Redis <https://redis.io/>`__, which is available on
   most Linux distributions. This instance must be accessible by the web
   service and the workers.
-  Install and run `RabbitMQ <https://www.rabbitmq.com/>`__, which is
   available on most Linux distributions. This instance must be
   accessible by the web service and the workers.
-  Install Fractalis via ``pip3 install fractalis``. Please note that
   Fractalis requires Python3.4 or higher. This must be installed on all
   machines that will run the web service or the workers.
-  Install required all required R packages. We won't list these
   packages excplicitely, as they can change frequently. Please refer
   instead to the
   `Dockerfile <https://git-r3lab.uni.lu/Fractalis/fractalis/blob/master/docker/Dockerfile>`__,
   which is *always* up-to-date, as a new version of Fractalis is only
   released when the Docker image passes all tests. This must be
   installed on all machines that will run the web service or the
   workers.
-  Run and expose the Fractalis web service with whatever tools you
   want. We recommend **gunicorn** and **nginx**, but others should
   work, too.
-  Run the celery workers on any machine that you want within the same
   network. (For a simple setup this can be the very same machine that
   the web service runs on).

Note: The `docker-compose.yml <https://github.com/thehyve/Fractalis/tree/dev/docker/docker-compose.yml>`__ describes
how the different services are started and how they connect with each
other.

Configuration
~~~~~~~~~~~~~

Use the environment variable ``FRACTALIS_CONFIG`` to define the
configuration file path. This variable must be a) a valid python file
(.py) and b) be available on all instances that host a Fractalis web
service or a Fractalis worker.

Tip: Use the `default settings <https://github.com/thehyve/Fractalis/tree/dev/fractalis/config.py>`__ as an example
for your own configuration file. Please note, that all this files
combines `Flask settings <http://flask.pocoo.org/docs/0.12/config/>`__,
`Celery
settings <http://docs.celeryproject.org/en/latest/userguide/configuration.html>`__,
and Fractalis settings, which are all listed and documented within this
file. Please don't overwrite default settings if you don't know what you
are doing. This might have severe implications for security or might
cause Fractalis to not work correctly.

See a sample configuration in `tests <https://github.com/thehyve/Fractalis/tree/dev/tests/config>`__ directory.


Data services
^^^^^^^^^^^^^

Required part of the configuration is a list of all supported data sources, together with a mapping to a handler type:

.. code-block::

    DATA_SERVICES = {
        'data_services': {
            '<name-of-service-1>': {
                'handler': '<handler-type-1>',
                'server': '<service-1-url>'
            },
            '<name-of-service-2>': {
                'handler': '<handler-type-2>',
                'server': '<service-2-url>'
            }
        }
    }


Data services config model is defined in `data_services_config.py <https://github.com/thehyve/Fractalis/tree/dev/fractalis/data_services_config.py>`__.
Name of the service is a one of the required parameters of data request (see the swagger API documentation).


Authorization
^^^^^^^^^^^^^

Configuration options for authorization, currently specific to the
transmart handler:

+---------------------------+-----------------+-----------------------------------------------------------------------------------------------------------+
| Configuration             | Default value   | Description                                                                                               |
+===========================+=================+===========================================================================================================+
| AUTHORIZATION\_DISABLED   | False           | Disable validation of an access token from a request. Disabling is not recommended!                       |
+---------------------------+-----------------+-----------------------------------------------------------------------------------------------------------+
| OIDC\_OFFLINE\_TOKEN      | None            | OIDC refresh token enabling an offline access. Used to refresh user tokens to prevent early expiration.   |
+---------------------------+-----------------+-----------------------------------------------------------------------------------------------------------+
| OIDC\_SERVER\_URL         |                 | OIDC server URL, including the realm e.g. https://keycloak-example.com/auth/realms/transmart-realm/       |
+---------------------------+-----------------+-----------------------------------------------------------------------------------------------------------+
| OIDC\_CLIENT\_ID          |                 | ID of the OIDC client                                                                                     |
+---------------------------+-----------------+-----------------------------------------------------------------------------------------------------------+

Add support for new services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to `this document <https://github.com/thehyve/Fractalis/tree/dev/fractalis/data>`__.

Citation
~~~~~~~~

Manuscript is in preparation.
