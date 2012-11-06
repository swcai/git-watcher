#!/usr/bin/env python
# file: main.py
# desc: a process to check remote git repo regularly and make an automatic build
# author: swcai

import os
import time
import smtplib
import daemon
import config
from email.mime.text import MIMEText

def run_without_output(cmd):
   os.popen(cmd)

def run_with_output(cmd):
   with os.popen(cmd) as f:
      line = f.readline()
      while line:
         yield line
         line = f.readline()

def send_mail(commit, desc, email):
   msg = MIMEText(''.join(run_with_output('git log -1 %s' % commit)))
   msg['subject'] = "New commit for %s project from %s" % (config.PROJECT_NAME, email)
   try:
      s = smtplib.SMTP()
      s.connect("localhost")
      s.sendmail(config.PROJECT_ADMIN, config.PROJECT_TO_LIST, msg.as_string())
      s.close()
   except Exception, e:
      print str(e)

class checker:
   last_commit = ''

   def init(self):
      self.fetch()

   def fetch(self):
      cmd = 'git fetch origin'
      run_without_output(cmd)

   def commits_since_lasttime(self):
      cmd = 'git log origin/master ' + self.last_commit + '.. --format="%H__SPLIT__%s__SPLIT__%ae"'
      self.commits = map(lambda line: line.rstrip().split('__SPLIT__'), run_with_output(cmd))
      if len(self.commits) > 0:
         self.last_commit = self.commits[0][0]

   def check_and_send_new_commits(self):
      pwd = os.getcwd()
      os.chdir(config.PROJECT_SRC_DIR)
      self.fetch()
      if self.last_commit != '':
         self.commits_since_lasttime()
         for commit in self.commits:
            send_mail(*commit)
      else:
         cmd = 'git log -l origin/master --format="%H"'
         self.last_commit = run_with_output(cmd).next()
      os.chdir(pwd) 

def main():
   instance = checker()
   while True:
      instance.check_and_send_new_commits()
      time.sleep(30)

if __name__ == '__main__':
   with daemon.DaemonContext():
      main()
