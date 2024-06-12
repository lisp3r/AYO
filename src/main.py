#!/usr/bin/python3 

"""
> 'AYO' is a simple application to store box information when playing ctfs
> Store box data and receive them instantly 
"""

import os
import sys
import argparse 
import json

import python_hosts.exception
from python_hosts import Hosts, HostsEntry
from rich.console import Console 
from rich.table import Table

dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = os.path.join(dir_path, "machine_data.json")


class Config:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.load()

    def save(func):
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            self = args[0]

            with open(self.config_path, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)

            return result
        return inner

    def __load(self):
        try:
            with open(self.config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except json.decoder.JSONDecodeError as err:
            console.print(f'[red][!] Cannot parse config file: {err}')
            exit(1)

    def load(self):
        self.__load()
        self.__repair()

    # TODO: it is kinda ugly so maybe rewrite it later
    @save
    def __repair(self):
        """ Repairs broken config file.
        First of all, we want to have 'platforms' nested dict being not empty. The function will create it and fill
        with default data.
        :return: None
        """
        if not self.config.get('platforms'):
            self.config['platforms'] = {
                'htb': '/home/user/htb',
                'thm': '/home/user/thm'
            }

    @save
    def rm(self, key_string: str):
        """ Removes key from config
        Example:
            self.config = {'platforms': { 'htb': 'path/to/htb' }, 'user': { 'name': 'alex' }}

            1. key_string: 'platforms.htb'
               result: {'platforms': {}, 'user': {'name': 'alex'}}
            2. key_string: 'user'
               result: {'platforms': { 'htb': 'path/to/htb' }}

        :param key_string: key or list of keys joined with '.', e.g. 'platforms.htb'
        :return: None
        """
        here = self.config
        keys = key_string.split('.')
        for key in keys[:-1]:
            here = here.setdefault(key, {})
        del here[keys[-1]]

    @save
    def set(self, key_string: str, value: str):
        """ Adds value to config
        Example:
            self.config = {}

            key_string: 'platforms.htb', value: 'path/to/htb'
            result: {'platforms': {'htb': 'path/to/htb'}}

        :param key_string: key or list of keys joined with '.', e.g. 'platforms.htb'
        :param value: value
        :return: None
        """
        here = self.config
        keys = key_string.split('.')
        for key in keys[:-1]:
            here = here.setdefault(key, {})
        here[keys[-1]] = value


console = Console()

BANNER = """
[cyan]
 ▄▄▄·  ▄· ▄▌      
▐█ ▀█ ▐█▪██▌ ▄█▀▄ 
▄█▀▀█ ▐█▌▐█▪▐█▌.▐▌
▐█▪ ▐▌ ▐█▀·.▐█▌.▐▌
 ▀  ▀   ▀ •  ▀█▄▀▪

[/]                                              
"""


def get_box_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError as err:
        console.print(f'[red][!] {err}')
        exit(1)


def print_box_info():
    with open(data_file, 'r') as file:
        data = json.load(file)
    current_box = data['current_box']
    status = data['status']
    rhost = data['rhost']
    domain = data['domain']
    platform = data['platform']

    table = Table(title="AYO - CTF Manager") 
    table.add_column("BOX", style="blue")
    table.add_column("RHOST", style="blue")
    table.add_column("DOMAIN", style="green")
    table.add_column("PLATFORM", style="blue") 
    table.add_column("STATUS", style="blue") 

    table.add_row(current_box, rhost, domain, platform, status)
    console.print(table) 


def update_config(args, config, print_help):
    if args.set:
        path, var = args.set
        config.set(path, var)
    elif args.print:
        print(json.dumps(config.config, indent=4))
    elif args.rm:
        config.rm(args.rm)
    else:
        print_help()
    exit(0)


def config_validation(config: Config):
    """ Validate config data: 1) make user to solve errors found on config loading; 2) check paths to project dirs

    :param config: Config object
    :return: None
    """
    wrong_dirs = []
    for platform_dir_name, platform_dir_path in config.config['platforms'].items():
        if not os.path.exists(platform_dir_path):
            wrong_dirs.append((platform_dir_name, platform_dir_path))
    if wrong_dirs:
        console.print(f'Set the correct paths for project folders.\n\nCurrent valuables are:')
        for i in wrong_dirs:
            console.print(f'\t{i[0]}: {i[1]}')
        console.print(f'\nTo change them use "config" command:\n\tayo config set platforms.{wrong_dirs[0][0]} <value>')
        exit(0)


def main():
    config_data = Config(os.path.join(dir_path, '../config.json'))

    parser = argparse.ArgumentParser(description=f'{BANNER}AYO - CTF Manager [Help Menu]')
    subparsers = parser.add_subparsers(dest='command', help='Update or get data')

    parser_new = subparsers.add_parser('new', help='Add new CTF box')
    parser_new.add_argument('--box', '-b', required=True, type=str, dest='ctf_name', help='Name of the CTF Box')
    parser_new.add_argument('--rhost', '-r', required=True, type=str, help='$rhost IP address')
    parser_new.add_argument('--domain', '-d', required=True, type=str, help='Domain Name')
    parser_new.add_argument('--platform', '-p', required=True, type=str, choices=config_data.config.get('platforms', {}).keys(), help='Platform Name')
    parser_new.add_argument('--active', '-a', default='active', choices=['active', 'dead'], help='Status of the CTF (active/dead)')

    parser_get = subparsers.add_parser('get', help='Get CTF box info')
    parser_get.add_argument('info', help='Information to retrieve')

    parser_set = subparsers.add_parser('set', help='Set CTF box info')
    parser_set.add_argument('--var', type=str, help='Variable to set')
    parser_set.add_argument('--value', type=str, help='Value to set')

    parser_conf = subparsers.add_parser('config', help='Configure AYO')
    parser_conf.add_argument('--set', type=str, nargs=2, help='Set a variable into config')
    parser_conf.add_argument('--rm', type=str, help='Remove a variable from config')
    parser_conf.add_argument('--print', action="store_true", help='Print config')

    COMMANDS_TO_SKIP_CONFIG_VALIDATION = ['config']

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(0)

    if args.command not in COMMANDS_TO_SKIP_CONFIG_VALIDATION:
        config_validation(config_data)

    if args.command == 'config':
        update_config(args, config_data, parser_conf.print_help)
    if args.command == 'new':
        new_box(args)
    if args.command == 'get':
        get_info(args)
    if args.command == 'set':
        set_info(args)


def new_box(args):
    console.print(f"[green][+] Adding a new box '{args.ctf_name}'...[/]")
    data = get_box_data()

    data['current_box'] = args.ctf_name
    data['rhost'] = args.rhost
    data['domain'] = args.domain
    data['platform'] = args.platform
    data['status'] = args.active

    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)

    console.print(f"[green][+] Adding '{args.rhost}  {args.domain}' into /etc/hosts...[/]")

    new_box = HostsEntry(entry_type='ipv4', address=args.rhost, names=[args.domain], comment="added by AYO")
    hosts = Hosts(path='/etc/hosts')
    hosts.add([new_box])

    try:
        hosts.write()
    except python_hosts.exception.UnableToWriteHosts:
        console.print(f'[red][!] Cannot write to /etc/hosts: Permission denied')
        exit(1)

    print_box_info()
    
    create_dir = console.input(f"[green]Create a directory for {args.ctf_name}? (y/n): [/]")
    if create_dir in ["y", "yes"]:
        ctf_path = os.path.join(args.platform, args.ctf_name)

        try:
            os.makedirs(ctf_path)
            console.print(f"[green][+] Directory '{ctf_path}' created successfully.[/]")
        except FileExistsError:
            print(f"Directory '{ctf_path}' already exists.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        console.print(f"[green][+] No directory was created for {args.ctf_name}!")

    console.print(f"[green][+] {args.ctf_name} box added! [/]") 


def get_info(args):
    data = get_box_data()

    if args.info in data:
        print(data[args.info])
    else:
        console.print(f"[red][-] Unsupported info: {args.info} [/]")


def set_info(args):
    data = get_box_data() 
    if args.var and args.value:
        data[args.var] = args.value

        with open(data_file, 'w') as file:
            json.dump(data, file, indent=4)

        console.print(f"[green][+] Set {args.var} to {args.value} [/]")
    else:
        console.print("[red][-] Please provide both [bold]--var[/] and [bold]--value arguments[/][red] for setting a variable [/]")
        sys.exit()


if __name__ == "__main__":
    main()
