'''
Documentation Builder Environments
'''

import logging
import os
import socket
import subprocess
import traceback
from datetime import datetime

from .exceptions import (BuildEnvironmentException, BuildEnvironmentError,
                         BuildEnvironmentWarning)

log = logging.getLogger(__name__)


class BuildCommand(object):
    """Wrap command execution for execution in build environments

    This wraps subprocess commands with some logic to handle exceptions,
    logging, and setting up the env for the build command.

    This acts a mapping of sorts to the API reprensentation of the
    :py:cls:`readthedocs.builds.models.BuildCommandResult` model.

    :param command: string or array of command parameters
    :param cwd: current working path for the command
    :param shell: execute command in shell, default=False
    :param environment: environment variables to add to environment
    :type environment: dict
    :param combine_output: combine stdout/stderr, default=True
    :param input_data: data to pass in on stdin
    :type input_data: str
    :param build_env: build environment to use to execute commands
    :param bin_path: binary path to add to PATH resolution
    :param description: a more grokable description of the command being run
    """

    def __init__(self, command, cwd=None, shell=False, environment=None,
                 combine_output=True, input_data=None, build_env=None,
                 bin_path=None, description=None):
        self.command = command
        self.shell = shell
        if cwd is None:
            cwd = os.getcwd()
        self.cwd = cwd
        self.environment = os.environ.copy()
        if environment is not None:
            self.environment.update(environment)

        self.combine_output = combine_output
        self.input_data = input_data
        self.build_env = build_env
        self.output = None
        self.error = None
        self.start_time = None
        self.end_time = None

        self.bin_path = bin_path
        self.description = ''
        if description is not None:
            self.description = description
        self.exit_code = None

    def __str__(self):
        # TODO do we want to expose the full command here?
        output = u''
        if self.output is not None:
            output = self.output.encode('utf-8')
        return '\n'.join([self.get_command(), output])

    def run(self):
        """Set up subprocess and execute command
        """
        log.info("Running: '%s' [%s]", self.get_command(), self.cwd)

        self.start_time = datetime.utcnow()
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
        stdin = None
        if self.input_data is not None:
            stdin = subprocess.PIPE
        if self.combine_output:
            stderr = subprocess.STDOUT

        environment = {}
        environment.update(self.environment)
        environment['READTHEDOCS'] = 'True'
        if self.build_env is not None:
            environment['READTHEDOCS_VERSION'] = self.build_env.version.slug
            environment['READTHEDOCS_PROJECT'] = self.build_env.project.slug
        if 'DJANGO_SETTINGS_MODULE' in environment:
            del environment['DJANGO_SETTINGS_MODULE']
        if 'PYTHONPATH' in environment:
            del environment['PYTHONPATH']
        if self.bin_path is not None:
            env_paths = environment.get('PATH', '').split(':')
            env_paths.insert(0, self.bin_path)
            environment['PATH'] = ':'.join(env_paths)

        try:
            proc = subprocess.Popen(
                self.command,
                shell=self.shell,
                cwd=self.cwd,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                env=environment,
            )
            cmd_input = None
            if self.input_data is not None:
                cmd_input = self.input_data

            cmd_output = proc.communicate(input=cmd_input)
            (cmd_stdout, cmd_stderr) = cmd_output
            try:
                self.output = cmd_stdout.decode('utf-8', 'replace')
            except (TypeError, AttributeError):
                self.output = None
            try:
                self.error = cmd_stderr.decode('utf-8', 'replace')
            except (TypeError, AttributeError):
                self.error = None
            self.exit_code = proc.returncode
        except OSError:
            self.error = traceback.format_exc()
            self.output = self.error
            self.exit_code = -1
        finally:
            self.end_time = datetime.utcnow()

    def get_command(self):
        """Flatten command"""
        if hasattr(self.command, '__iter__') and not isinstance(self.command, str):
            return ' '.join(self.command)
        else:
            return self.command

    def save(self):
        """Save this command and result via the API"""
        data = {
            'build': self.build_env.build.get('id'),
            'command': self.get_command(),
            'description': self.description,
            'output': self.output,
            'exit_code': self.exit_code,
            'start_time': self.start_time,
            'end_time': self.end_time,
        }
        pass


class BuildEnvironment(object):
    """
    Base build environment

    Placeholder for reorganizing command execution.

    :param project: Project that is being built
    :param version: Project version that is being built
    :param build: Build instance
    :param record: Record status of build object
    """

    def __init__(self, project=None, version=None, build=None, record=True):
        self.project = project
        self.version = version
        self.build = build
        self.record = record
        self.commands = []
        self.failure = None
        self.start_time = datetime.utcnow()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        ret = self.handle_exception(exc_type, exc_value, tb)
        self.update_build(state=BUILD_STATE_FINISHED)
        log.info(LOG_TEMPLATE
                 .format(project=self.project.slug,
                         version=self.version.slug,
                         msg='Build finished'))
        return ret

    def handle_exception(self, exc_type, exc_value, _):
        """Exception handling for __enter__ and __exit__

        This reports on the exception we're handling and special cases
        subclasses of BuildEnvironmentException.  For
        :py:cls:`BuildEnvironmentWarning`, exit this context gracefully, but
        don't mark the build as a failure.  For :py:cls:`BuildEnvironmentError`,
        exit gracefully, but mark the build as a failure.  For all other
        exception classes, the build will be marked as a failure and an
        exception will bubble up.
        """
        if exc_type is not None:
            log.error(LOG_TEMPLATE
                      .format(project=self.project.slug,
                              version=self.version.slug,
                              msg=exc_value),
                      exc_info=True)
            if issubclass(exc_type, BuildEnvironmentWarning):
                return True
            else:
                self.failure = exc_value
                if issubclass(exc_type, BuildEnvironmentError):
                    return True
                return False

    def run(self, *cmd, **kwargs):
        '''Shortcut to run command from environment'''
        return self.run_command_class(cls=self.command_class, cmd=cmd, **kwargs)

    def run_command_class(self, cls, cmd, **kwargs):
        '''Run command from this environment

        Use ``cls`` to instantiate a command

        :param warn_only: Don't raise an exception on command failure
        '''
        warn_only = kwargs.pop('warn_only', False)
        kwargs['build_env'] = self
        build_cmd = cls(cmd, **kwargs)
        self.commands.append(build_cmd)
        build_cmd.run()

        # Save to database
        if self.record:
            build_cmd.save()

        if build_cmd.failed:
            msg = u'Command {cmd} failed'.format(cmd=build_cmd.get_command())

            if build_cmd.output:
                msg += u':\n{out}'.format(out=build_cmd.output)

            if warn_only:
                log.warn(LOG_TEMPLATE
                         .format(project=self.project.slug,
                                 version=self.version.slug,
                                 msg=msg))
            else:
                raise BuildEnvironmentWarning(msg)
        return build_cmd

    @property
    def successful(self):
        '''Is build completed, without top level failures or failing commands'''
        return (self.done and self.failure is None and
                all(cmd.successful for cmd in self.commands))

    @property
    def failed(self):
        '''Is build completed, but has top level failure or failing commands'''
        return (self.done and (
            self.failure is not None or
            any(cmd.failed for cmd in self.commands)
        ))

    @property
    def done(self):
        '''Is build in finished state'''
        return (self.build is not None and
                self.build['state'] == BUILD_STATE_FINISHED)

    def update_build(self, state=None):
        """
        Record a build by hitting the API.

        Returns nothing
        """
        if not self.record:
            return None

        self.build['project'] = self.project.pk
        self.build['version'] = self.version.pk
        self.build['builder'] = socket.gethostname()
        self.build['state'] = state
        if self.done:
            self.build['success'] = self.successful

            # TODO drop exit_code and provide a more meaningful UX for error
            # reporting
            if self.failure and isinstance(self.failure,
                                           BuildEnvironmentException):
                self.build['exit_code'] = self.failure.status_code
            elif len(self.commands) > 0:
                self.build['exit_code'] = max([cmd.exit_code
                                               for cmd in self.commands])

        self.build['setup'] = self.build['setup_error'] = ""
        self.build['output'] = self.build['error'] = ""

        if self.start_time:
            build_length = (datetime.utcnow() - self.start_time)
            self.build['length'] = build_length.total_seconds()

        if self.failure is not None:
            self.build['error'] = str(self.failure)

        # Attempt to stop unicode errors on build reporting
        for key, val in self.build.items():
            if isinstance(val, basestring):
                self.build[key] = val.decode('utf-8', 'ignore')

        try:
            resp = api_v2.build(self.build['id']).put(self.build)
        except Exception:
            log.error("Unable to post a new build", exc_info=True)


class LocalEnvironment(BuildEnvironment):
    '''Local execution environment'''
    command_class = BuildCommand
