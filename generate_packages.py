#!/usr/bin/env python
from __future__ import print_function

import errno
import logging
import optparse
import os
import platform
import subprocess
import shutil
import sys
import time

script_path = os.path.dirname(os.path.realpath(__file__))

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def run_cmd(cmd, run_env=False, unsafe_shell=False, check_rc=False):
    log = logging.getLogger(__name__)
    # run it
    if run_env == False:
        run_env = os.environ.copy()
    log.debug('run_env: {0}'.format(run_env))
    log.info('running: {0}, unsafe_shell={1}, check_rc={2}'.format(cmd, unsafe_shell, check_rc))
    if unsafe_shell == True:
        p = subprocess.Popen(cmd, env=run_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    else:
        p = subprocess.Popen(cmd, env=run_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    log.info('  stdout: {0}'.format(out.strip()))
    log.info('  stderr: {0}'.format(err.strip()))
    log.info('')
    if check_rc != False:
        if p.returncode != 0:
            log.error(check_rc)
            sys.exit(p.returncode)
    return p.returncode

def prepare_package_directories(package_type):
    log = logging.getLogger(__name__)
    build_dir = 'build-{0}'.format(package_type)
    directories_to_be_packaged = ['etc']
    if package_type == 'deb':
        # apt
        repository_dir = os.path.join(build_dir, 'etc', 'apt', 'sources.list.d')
        mkdir_p(repository_dir)
        shutil.copyfile('renci-irods.deb.list', os.path.join(repository_dir, 'renci-irods.list'))
        tmp_dir = os.path.join(build_dir, 'tmp')
        mkdir_p(tmp_dir)
        shutil.copyfile('irods-signing-key.asc', os.path.join(tmp_dir, 'irods-signing-key.asc'))
        directories_to_be_packaged.extend(['tmp'])
    elif package_type == 'rpm':
        # yum
        repository_dir = os.path.join(build_dir, 'etc', 'yum.repos.d')
        mkdir_p(repository_dir)
        shutil.copyfile('renci-irods.yum.rpm.repo', os.path.join(repository_dir, 'renci-irods.repo'))
        # zypp
        repository_dir = os.path.join(build_dir, 'etc', 'zypp', 'repos.d')
        mkdir_p(repository_dir)
        shutil.copyfile('renci-irods.zypp.rpm.repo', os.path.join(repository_dir, 'renci-irods.repo'))
    else:
        log.error('Cannot prepare directories for package type [{0}]'.format(package_type))
        return 1
    return directories_to_be_packaged


def build_package(package_type, directories_to_be_packaged):
    build_dir = 'build-{0}'.format(package_type)
    package_version = time.strftime("%Y%m%d")
    fpmbinary='fpm'
    run_cmd(['which', fpmbinary], check_rc='fpm not found, try "gem install fpm"')
    os.chdir(script_path)
    package_cmd = [fpmbinary, '-f', '-s', 'dir']
    package_cmd.extend(['-t', package_type])
    package_cmd.extend(['-n', 'renci-irods-repository'])
    package_cmd.extend(['-m', 'iRODS Consortium <packages@irods.org>'])
    package_cmd.extend(['-v', package_version])
    package_cmd.extend(['--vendor', 'iRODS Consortium'])
    package_cmd.extend(['--license', '3-Clause BSD'])
    package_cmd.extend(['--description', 'RENCI iRODS Repository'])
    package_cmd.extend(['--url', 'https://irods.org'])
    if package_type == 'deb':
        package_cmd.extend(['--after-install', 'postinstall'])
        package_cmd.extend(['--before-remove', 'preremove'])
        package_cmd.extend(['--deb-no-default-config-files'])
    package_cmd.extend(['-C', build_dir])
    for d in sorted(directories_to_be_packaged):
        package_cmd.extend([d])
    run_cmd(package_cmd, check_rc='packaging failed')
    print('Building [{0}] Package ... Complete'.format(package_type))

def main():
    # check parameters
    usage = "Usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option('-q', '--quiet', action='store_const', const=0, dest='verbosity', help='print less information to stdout')
    parser.add_option('-v', '--verbose', action="count", dest='verbosity', default=1, help='print more information to stdout')
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    # configure logging
    log = logging.getLogger()
    if options.verbosity >= 2:
        log.setLevel(logging.DEBUG)
    elif options.verbosity == 1:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # produce packages for known package types
    for t in ['deb', 'rpm']:
        log.debug(t)
        d = prepare_package_directories(t)
        log.debug(d)
        build_package(t, d)

if __name__ == '__main__':
    sys.exit(main())

