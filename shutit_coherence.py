"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class shutit_coherence(ShutItModule):


	def build(self, shutit):
		# Some useful API calls for reference. See shutit's docs for more info and options:
		#
		# ISSUING BASH COMMANDS
		# shutit.send(send,expect=<default>) - Send a command, wait for expect (string or compiled regexp)
		#                                      to be seen before continuing. By default this is managed
		#                                      by ShutIt with shell prompts.
		# shutit.multisend(send,send_dict)   - Send a command, dict contains {expect1:response1,expect2:response2,...}
		# shutit.send_and_get_output(send)   - Returns the output of the sent command
		# shutit.send_and_match_output(send, matches) 
		#                                    - Returns True if any lines in output match any of 
		#                                      the regexp strings in the matches list
		# shutit.run_script(script)          - Run the passed-in string as a script
		# shutit.install(package)            - Install a package
		# shutit.remove(package)             - Remove a package
		# shutit.login(user='root', command='su -')
		#                                    - Log user in with given command, and set up prompt and expects.
		#                                      Use this if your env (or more specifically, prompt) changes at all,
		#                                      eg reboot, bash, ssh
		# shutit.logout(command='exit')      - Clean up from a login.
		# 
		# COMMAND HELPER FUNCTIONS
		# shutit.add_to_bashrc(line)         - Add a line to bashrc
		# shutit.get_url(fname, locations)   - Get a file via url from locations specified in a list
		# shutit.get_ip_address()            - Returns the ip address of the target
		#
		# LOGGING AND DEBUG
		# shutit.log(msg,add_final_message=False) -
		#                                      Send a message to the log. add_final_message adds message to
		#                                      output at end of build
		# shutit.pause_point(msg='')         - Give control of the terminal to the user
		# shutit.step_through(msg='')        - Give control to the user and allow them to step through commands
		#
		# SENDING FILES/TEXT
		# shutit.send_file(path, contents)   - Send file to path on target with given contents as a string
		# shutit.send_host_file(path, hostfilepath)
		#                                    - Send file from host machine to path on the target
		# shutit.send_host_dir(path, hostfilepath)
		#                                    - Send directory and contents to path on the target
		# shutit.insert_text(text, fname, pattern)
		#                                    - Insert text into file fname after the first occurrence of 
		#                                      regexp pattern.
		# ENVIRONMENT QUERYING
		# shutit.host_file_exists(filename, directory=False)
		#                                    - Returns True if file exists on host
		# shutit.file_exists(filename, directory=False)
		#                                    - Returns True if file exists on target
		# shutit.user_exists(user)           - Returns True if the user exists on the target
		# shutit.package_installed(package)  - Returns True if the package exists on the target
		# shutit.set_password(password, user='')
		#                                    - Set password for a given user on target
		java_rpm = 'jdk-8u45-linux-x64.rpm'
		fmw_pkg = 'fmw_12.1.3.0.0_coherence_Disk1_1of1.zip'
		fmw_jar = 'fmw_12.1.3.0.0_coherence.jar'
		fmw_dir = 'coherence12130'
		coherence_home = '/u01/' + fmw_dir + '/coherence'
		shutit.install('git wget')
		shutit.send('cd /opt')
		shutit.send('git clone https://github.com/brunoborges/coherence-docker.git')
		shutit.send('cd coherence-docker')
		# Install and configure Oracle JDK 8u25
		# -------------------------------------
		shutit.send_host_file('/' + java_rpm + '.aa','context/' + java_rpm + '.aa')
		shutit.send_host_file('/' + java_rpm + '.ab','context/' + java_rpm + '.ab')
		shutit.send_host_file('/' + java_rpm + '.ac','context/' + java_rpm + '.ac')
		shutit.send('cat /' + java_rpm + '.* > /' + java_rpm)
		shutit.send('rpm -i /' + java_rpm)
		shutit.add_to_bashrc('export JAVA_HOME=/usr/java/default')
		shutit.send('export JAVA_HOME=/usr/java/default')
		shutit.add_to_bashrc('export CONFIG_JVM_ARGS=-Djava.security.egd=file:/dev/./urandom')
		shutit.send('export CONFIG_JVM_ARGS=-Djava.security.egd=file:/dev/./urandom')
		# Setup required packages (unzip), filesystem, and oracle user
		# ------------------------------------------------------------
		shutit.install('unzip')
		shutit.send('mkdir /u01 && chmod a+xr /u01')
		shutit.send('useradd -b /u01 -m -s /bin/bash oracle')
		shutit.send('echo oracle:oracle | chpasswd')

		# Copy files required to build this image
		shutit.send('cp config/oraInst.loc /u01/oraInst.loc')
		shutit.send('cp config/install.file /u01/install.file')
		shutit.send_host_file('/u01/' + fmw_pkg,'context/' + fmw_pkg)
		shutit.send_host_file('/' + fmw_pkg + '.aa','context/' + fmw_pkg + '.aa')
		shutit.send_host_file('/' + fmw_pkg + '.ab','context/' + fmw_pkg + '.ab')
		shutit.send('cat /' + fmw_pkg + '.* > /' + fmw_pkg)
		shutit.send('unzip /u01/' + fmw_pkg + ' -d /u01/oracle/ > /dev/null')
		shutit.send('rm -f ' + fmw_pkg)
		shutit.send('chown oracle:oracle -R /u01')

		shutit.login(user='oracle')
		shutit.send('mkdir /u01/oracle/.inventory')
		shutit.send('cd /u01/oracle')
		shutit.send('java -jar ' + fmw_jar + ' -silent -responseFile /u01/install.file -invPtrLoc /u01/oraInst.loc -jreLoc $JAVA_HOME')
		shutit.send('rm -f ' + fmw_jar)
		shutit.send('ln -s /u01/oracle/' + fmw_dir + ' /u01/oracle/coherence')

		shutit.logout()
		shutit.send('rm -f /u01/oraInst.loc /u01/install.file')
		shutit.send('yum erase -y unzip')
		shutit.send('yum clean all')

		shutit.send('rm -f /' + java_rpm)
		if shutit.cfg[self.module]['dev']:
			shutit.send('touch /tmp/dev')
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is 
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		shutit.get_config(self.module_id, 'dev', default=False)
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


def module():
	return shutit_coherence(
		'shutit.tk.shutit_coherence.shutit_coherence', 782914092.00,
		description='',
		maintainer='',
		depends=['shutit.tk.setup']
	)

