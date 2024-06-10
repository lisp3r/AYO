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


def load_config():
    with open(os.path.join(dir_path, 'config.json'), 'r') as config_file:
        return json.load(config_file)


def save_config(config_data):
    with open(os.path.join(dir_path, 'config.json'), 'w') as config_file:
        return json.dump(config_data, config_file)


# Source: https://stackoverflow.com/a/57561744
def set_var_config(key_string, value):
    """Given 'platforms.htb', 'path/to/folder', set config_data['platforms']['htb'] = 'path/to/folder'"""

    config_data = load_config()
    keys = key_string.split(".")

    # For every key *before* the last one, we concentrate on navigating through the dictionary.
    for key in keys[:-1]:
        # Try to find here[key]. If it doesn't exist, create it with an empty dictionary. Then,
        # update our `here` pointer to refer to the thing we just found (or created).
        config_data = config_data.setdefault(key, {})

    # Finally, set the final key to the given value
    config_data[keys[-1]] = value
    save_config(config_data)


console = Console()
config_data = load_config()


def banner():
    console.print("""
[cyan]
 ▄▄▄·  ▄· ▄▌      
▐█ ▀█ ▐█▪██▌ ▄█▀▄ 
▄█▀▀█ ▐█▌▐█▪▐█▌.▐▌
▐█▪ ▐▌ ▐█▀·.▐█▌.▐▌
 ▀  ▀   ▀ •  ▀█▄▀▪

[/]                                              
""")


def get_box_data():
    with open(data_file, 'r') as file:
        return json.load(file)


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

    # banner()
    table.add_row(current_box, rhost, domain, platform, status)
    console.print(table) 


def main():
    parser = argparse.ArgumentParser(description='AYO - CTF Manager [Help Menu]')
    subparsers = parser.add_subparsers(dest='command', help='Update or get data')

    parser_new = subparsers.add_parser('new', help='Add new CTF box')
    parser_new.add_argument('--box', '-b', required=True, type=str, dest='ctf_name', help='Name of the CTF Box')
    parser_new.add_argument('--rhost', '-r', required=True, type=str, help='$rhost IP address')
    parser_new.add_argument('--domain', '-d', required=True, type=str, help='Domain Name')
    parser_new.add_argument('--platform', '-p', required=True, type=str, choices=config_data['platforms'].keys(), help='Platform Name')
    parser_new.add_argument('--active', '-a', default='active', choices=['active', 'dead'], help='Status of the CTF (active/dead)')

    parser_get = subparsers.add_parser('get', help='Get CTF box info')
    parser_get.add_argument('info', help='Information to retrieve')

    parser_set = subparsers.add_parser('set', help='Set CTF box info')
    parser_set.add_argument('--var', type=str, help='Variable to set')
    parser_set.add_argument('--value', type=str, help='Value to set')

    parser_conf = subparsers.add_parser('config', help='Configure AYO')
    parser_conf.add_argument('--set', type=str, nargs=2, help='Set a variable into config')
    parser_conf.add_argument('--print', action="store_true", help='Print config')

    args = parser.parse_args()

    if args.command is None:
        banner()
        parser.print_help()
        exit(0)

    if args.command == 'config':
        if args.set:
            path, var = args.set
            set_var_config(path, var)
            exit(0)
        if args.print:
            print(json.dumps(config_data, indent=4))
            exit(0)

    # Check if the user changed htm and thm paths
    if not (os.path.exists(config_data['platforms']['thm']) and
            os.path.exists(config_data['platforms']['htb'])):
        console.print(f"""First of all, set the correct paths for 'HTB' and 'THM folders.'
Current valuables are:
    htb_path: {config_data['platforms']['htb']}
    thm_path: {config_data['platforms']['thm']}

To change them use:
    ayo config --set platforms.htb <value>
    ayo config --set platforms.thm <value>
""")
        exit(0)

    banner()

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

    new_box = HostsEntry(entry_type='ipv4', address=args.rhost, names=[args.domain])
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
    global data_file 

    data = get_box_data()

    if args.info in data:
        print(data[args.info])
    else:
        console.print(f"[red][-] Unsupported info: {args.info} [/]")


def set_info(args):
    global data_file 

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
