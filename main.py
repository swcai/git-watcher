#!/usr/bin/env python
# file: main.py
# desc: a process to check remote git repo regularly and make an automatic build
# author: swcai

import os
import time
import smtplib
import daemon
from email.mime.text import MIMEText

def run_without_output(cmd):
   os.popen(cmd)
   

def run_with_output(cmd):
   with os.popen(cmd) as f:
      return f.readlines()
   return []


PROJECT_NAME = "TeamEventApp"
PROJECT_DIR = os.getcwd()
PROJECT_SRC_DIR = "%s/src/TeamEventApp" % PROJECT_DIR
PROJECT_LOG_DIR = "%s/log" % PROJECT_DIR

def send_mail(commit, desc, email):
   msg = MIMEText(''.join(run_with_output('git log -1 %s' % commit)))
   me = 'stanley.w.cai@intel.com'
   to_list = ['stanley.w.cai@intel.com', 'yong.hu@intel.com', 'kaining.yuan@intel.com', 'fanjiang.pei@intel.com', 'jun.feng.lu@intel.com', 'qinghui.jian@intel.com', 'shidong.ren@intel.com']
   msg['subject'] = "New commit for %s project from %s" % (PROJECT_NAME, email)
   try:
      s = smtplib.SMTP()
      s.connect("localhost")
      s.sendmail(me, to_list, msg.as_string())
      s.close()
   except Exception, e:
      print str(e)

class builder:
   FIRST_COMMIT='49b8521d4422606b17e21ebd4347823293c579c2'
   last_commit='d7d93111b56b76e042359d9f129e96ab29aadb6f'
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

   def build(self, commit):
      cmd = 'git checkout %s -b tmp' % commit[0]
      run_without_output(cmd)
      cmd = 'android update project -p . -n %s' % PROJECT_NAME  
      run_without_output(cmd)
      cmd = 'ant debug'
      run_without_output(cmd)
      cmd = 'cp bin/%s-debug.apk %s/%s-debug-%s.apk' % (PROJECT_NAME, PROJECT_LOG_DIR, PROJECT_NAME, commit[0])
      run_without_output(cmd)
      cmd = 'git checkout master'
      run_without_output(cmd)
      cmd = 'git branch -D tmp'
      run_without_output(cmd)

   def build_and_publish_new_commits(self):
      pwd = os.getcwd()
      os.chdir(PROJECT_SRC_DIR)
      self.fetch()
      self.commits_since_lasttime()
      for commit in self.commits:
         self.build(commit)
         self.publish('%s-debug-%s.apk' % (PROJECT_NAME, commit[0]), commit[0], commit[1], commit[2] ) 
         send_mail(*commit)
      os.chdir(pwd) 

   def publish(self, filename, commit, description, email):
      with open("%s/apks.html" % PROJECT_LOG_DIR, 'a+') as f:
         f.write('\n')
         f.write('<li><a href="%s">%s.apk</a></li>' % (filename, PROJECT_NAME))
         f.write('<li>Email: %s</li>' % email)
         f.write('<li>Commit: %s</li>' % commit)
         f.write('<li>Title:\n%s</li>' % description)

def main():
   instance = builder()  
   while True:
      instance.build_and_publish_new_commits()
      time.sleep(30)

if __name__ == '__main__':
   with daemon.DaemonContext():
      main()
