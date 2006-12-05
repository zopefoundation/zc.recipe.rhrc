##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Create a system deployment for an application

$Id: __init__.py 15402 2006-12-01 15:58:08Z jim $
"""

import os, shutil, stat

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        deployment = options.get('deployment')
        if deployment:
            self.name = deployment
            if 'user' not in options:
                options['user'] = buildout[deployment].get('user', '')

        options['scripts'] = '\n'.join([buildout[part]['run-script']
                                        for part in options['parts'].split()
                                        ])
        options['envs'] = '\n'.join([buildout[part].get('env', '')
                                     for part in options['parts'].split()
                                     ])

    def install(self):
        options = self.options
        parts = options['parts'].split()
        if not parts:
            return
        scripts = options['scripts'].split('\n')
        chkconfig = self.options.get('chkconfig')
        user = options.get('user', '')
        if user == 'root':
            user = '' # no need to su to root
        envs = options['envs'].split('\n')
        created = []
        try:
            if len(scripts) == 1:
                # No mongo script
                script = scripts[0]
                if user:
                    script = 'su %s -c \\\n      "%s $*"' % (user, script)
                else:
                    script += ' $*'
                    
                env = envs[0]
                if env:
                    script = env + ' \\\n      ' + script
                if chkconfig:
                    script += ' \\\n      </dev/null'
                self.output(chkconfig, script, self.name, created)
            else:
                cooked = []
                for env, script in zip(envs, scripts):
                    if user:
                        script = 'su %s -c \\\n      "%s $*"' % (user, script)
                    else:
                        script += ' $*'

                    if env:
                        script = env + ' \\\n      ' + script

                    cooked.append(script)
                    
                for part, script in zip(parts, cooked):
                    self.output('', script, self.name+'-'+part, created)

                if chkconfig:
                    cooked = [s + ' \\\n      </dev/null'
                              for s in cooked]
                    
                script = '\n\n    '.join(cooked)
                cooked.reverse()
                rscript = '\n\n    '.join(cooked)
                self.output(chkconfig, script, self.name, created, rscript)
            return created
        except:
            [os.remove(f) for f in created]
            raise

    def output(self, chkconfig, script, ctl, created, rscript=None):
        if rscript is None:
            rscript = script
        rc = rc_template % dict(
            rootcheck = self.options.get('user') and rootcheck or '',
            CHKCONFIG = (chkconfig
                         and (chkconfig_template % chkconfig)
                         or non_chkconfig_template),
            CTL_SCRIPT = script,
            CTL_SCRIPT_R = rscript,
            )
        dest = self.options.get('dest', '/etc/init.d')
        ctlpath = os.path.join(dest, ctl)
        open(ctlpath, 'w').write(rc)
        created.append(ctlpath)
        os.chmod(ctlpath,
                 os.stat(ctlpath).st_mode | stat.S_IEXEC | stat.S_IXGRP)
        if chkconfig:
            chkconfigcommand = self.options.get('chkconfigcommand',
                                                'chkconfig')
            os.system(chkconfigcommand+' --add '+ctl)

    def update(self):
        pass

def uninstall(name, options):
    if options.get('chkconfig'):
        chkconfigcommand = options.get('chkconfigcommand', 'chkconfig')
        os.system(chkconfigcommand+' --del '+name)
    

chkconfig_template = '''\
# the next line is for chkconfig
# chkconfig: %s
# description: please, please work
'''

non_chkconfig_template = '''\
# This script is for adminstrator convenience.  It should
# NOT be installed as a system startup script!
'''

rootcheck = """
if [ $(whoami) != "root" ]; then
  echo "You must be root."
  exit 1
fi
"""

rc_template = """#!/bin/sh 

%(CHKCONFIG)s
%(rootcheck)s
case $1 in 
  stop)
  
    %(CTL_SCRIPT_R)s

    ;;
  restart)

    ${0} stop
    sleep 1
    ${0} start

    ;;
  *) 
  
    %(CTL_SCRIPT)s

    ;;
esac

"""
