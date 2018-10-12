# -*- coding: utf-8 -*-

"""Console script for acl_stats."""
import sys
import click
from acl_stats import acl_stats

@click.group()
def main():
    click.echo(click.style('ACL Stats', fg='blue', bold=True))
    pass

@main.command()
@click.option('--acl-file', default=None, prompt='ACL File', help='File containing the output of the show acess-list _name_ command', required=True)
@click.option('--acl-brief', default=None, prompt='ACL Brief File', help='File containing the output of the show acess-list _name_ brief command', required=True)
@click.option('--output', default="csv", help='Choose an output format: json, csv. Defaults to csv', required=False)
@click.option('--write-to', default="", help='Write the output to a file', required=False)
def static(acl_file, acl_brief, output, write_to):
    """Use static files instead of connection to a device"""

    click.echo(click.style('Using Static Files', fg='green'))

    print(acl_file)
    print(acl_brief)
    print(output)
    print(write_to)

    ACLStats = acl_stats.ACLStats(acl_file=acl_file, acl_brief=acl_brief, output=output, write_to=write_to)

    ACLStats.process_live()

    return 0

@main.command()
@click.option('--hostname', default=None, prompt='Hostname', help='Hostname or IP of device to connect', required=True)
@click.option('--port', default=443, help='port to use when connection to a device', required=True)
@click.option('--username', default=None, prompt='Username', help='username to use when connection to a device', required=True)
@click.option('--password', default=None, prompt='Password', help='password to use when connection to a device', required=True)
@click.option('--acl-name', default=None, prompt='ACL Name', help='Name of target ACL', required=True)
@click.option('--output', default="csv", help='Choose an output format: json, csv. Defaults to csv', required=False)
@click.option('--write-to', default=None, help='Write the output to a file', required=False)
def device(hostname, port, username, password, acl_name, output, write_to):
    """Connect to a device to fech ACLs"""

    click.echo(click.style('Using Device {}'.format(hostname), fg='green'))

    ACLStats = acl_stats.ACLStats(hostname=hostname, port=port, username=username,
                                  password=password, acl_name=acl_name, output=output, write_to=write_to)

    ACLStats.process_live()

    return 0



if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
