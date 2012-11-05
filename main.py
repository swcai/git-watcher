#!/usr/bin/env python
# file: main.py
# desc: a process to check remote git repo regularly and make an automatic build
# author: swcai

import os

def run_without_output(cmd):
   os.popen(cmd)
   

def run_with_output(cmd):
   with os.popen(cmd) as f:
      return f.readlines()
   return []


class git_helper:
   FIRST_COMMIT='49b8521d4422606b17e21ebd4347823293c579c2'
   last_commit='009e3a0a7ebb25ec770f3c196fa7869aef829cb6'

   def init(self):
      # cmd = 'git fetch origin'
      # run_without_output(cmd)
      pass

   def commits_since_lasttime(self):
      cmd = 'git log origin/master ' + self.last_commit + '.. --format="%H__SPLIT__%B__SPLIT__%ae"'
      self.commits = map(lambda line: line.rstrip().split('__SPLIT__'), run_with_output(cmd))
      self.last_commit = self.commits[-1][0]

   def auto_build(self):
      self.commits_since_lasttime()
      for commit in self.commits:
         cmd = 'git checkout %s -b tmp' % commit[0]
         run_without_output(cmd)
         cmd = 'android update project -p . -n TeamEventApp'  
         run_without_output(cmd)
         cmd = 'ant debug'
         run_without_output(cmd)
         cmd = 'cp bin/TeamEventApp-debug.apk ./TeamEventApp-debug-%s.apk' %commit[0]
         run_without_output(cmd)
         cmd = 'git checkout master'
         run_without_output(cmd)
         cmd = 'git branch -d tmp'
         run_without_output(cmd)
         self.pre_publish('TeamEventApp-debug-%s.apk' % commit[0], commit[0], commit[1], commit[2] ) 
      self.publish()

   def pre_publish(self, filename, commit, description, email):
      cmd = 'cp %s /var/www/' % filename
      run_without_output(cmd)
      with open("/var/www/apks.txt", 'a+') as f:
         f.write('\n')
         f.write('<a href="%s">%s</a>' % (filename, filename))
         f.write('email: %s' % email)
         f.write('description:\n<pre>%s</pre>' % description)

   def publish(self):
      cmd = "cat head.html > apks.html"
      run_without_output(cmd)
      cmd = "cat apks.txt >> apks.html"
      run_without_output(cmd)
      cmd = "cat tail.html >> apks.html"
      run_without_output(cmd)
      
def main():
   helper = git_helper()  
   helper.auto_build()

if __name__ == '__main__':
   main()
