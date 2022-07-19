#!/usr/bin/python3

import argparse
import asyncio
import json
import socket
import subprocess

import aiohttp.client_exceptions
from aiohttp import ClientSession


def start():
    parser = argparse.ArgumentParser(description="DNS Recon tool")
    parser.add_argument("-d", "--domain", help="Investigate all NS for a given domain.")
    parser.add_argument("--server", "-s", help="Investigate only this NS.")
    parser.add_argument("--subdomain", help="Check subdomains.")
    parser.add_argument("--output", "-o", help="Save results in file.")
    parser.add_argument("--verbose", "-v", help="Show additional info about script flow.", action="store_true")
    args = parser.parse_args()
    parser.print_help()
    return args


def get_ns(domain):
    out = ""
    out = subprocess.check_output(['dig', domain, '-t', 'ns', '+short'])
    return out.decode('ascii').rstrip().split('\n')


def get_real_name(ns_start):
    ns = '@' + ns_start
    out = subprocess.check_output(['dig', ns, 'hostname.bind.', 'txt', 'chaos', '+short'])
    out = out.decode('ascii').rstrip().replace('"', '')

    return out


def get_version(ns_start):
    ns = '@' + ns_start
    out = subprocess.check_output(['dig', ns, 'version.bind.', 'txt', 'chaos', '+short'])
    out = out.decode('ascii').rstrip().replace('"', '')

    return out


def get_ip(name, domain=''):
    try:
        ip = socket.gethostbyname(name)
    except Exception:
        try:
            if domain:
                ip = socket.gethostbyname(name + '.' + domain)
            else:
                ip = ''
        except Exception:
            ip = ''

    return ip


def verbose(extra_data):
    if data_start.verbose:
        print(extra_data)


def result_all(data, subdomains):
    return json.dumps((data, subdomains), indent=4, sort_keys=True)


def launch_check(domain, server):
    if not domain and not server:
        exit()


def save_data(output, data, sub):
    with open(output, "a") as file_input:
        file_input.write(result_all(data, sub))
    file_input.close()


async def fetch(url, wordlist):
    subdomains = ""
    for subdomain in wordlist:
        for r in (("\n", ""), ("#", "")):
            subdomain = subdomain.replace(*r)
        addr = "https://" + subdomain + "." + url + "/"
        async with ClientSession(trust_env=True) as session:
            try:
                await session.get(addr, timeout=0)
                subdomains += addr + "\n"
            except aiohttp.client_exceptions.ClientConnectorError:
                pass
    return subdomains


async def check_domain(url, wordlist):
    sub = await fetch(url, wordlist)
    return sub


if __name__ == "__main__":
    REQUESTS_PER_NS = 25
    data_start = start()
    launch_check(data_start.domain, data_start.server)
    ip = get_ip(data_start.domain)
    if data_start.subdomain:
        with open(data_start.subdomain, "r") as file:
            job = asyncio.get_event_loop()
            subdomain_out = job.run_until_complete(check_domain(data_start.domain, file.readlines()))
            file.close()

    if data_start.domain:
        ns_list = get_ns(data_start.domain)
        verbose("; Found next NS for domain '%s': %s" % (data_start.domain, str(ns_list)))
        verbose("")
    else:
        if data_start.server:
            ns_list = [data_start.server]

    if data_start.verbose:
        comment = "; Final results in JSON:"
        print(comment)

    ns_dict = dict()
    subdomains_data = dict()

    for ns in ns_list:
        verbose("; Work started for NS '%s'" % ns)
        real_names_list = []
        real_versions_list = []

        for i in range(REQUESTS_PER_NS):
            try:
                real_name = get_real_name(ns)
                real_ip = get_ip(real_name, data_start.domain)

                real_version = get_version(ns)
                if real_version and real_version not in real_versions_list:
                    real_versions_list.append(real_version)

                ns_record = {'name': real_name, 'ip': real_ip}
                if real_name and ns_record not in real_names_list:
                    real_names_list.append(ns_record)

            except Exception as e:
                if data_start.verbose:
                    comment = "; " + str(e)
                    print(comment)
                break

        ns_ip = get_ip(ns)
        verbose("; Found next servers for given NS '%s' (%s): %s" % (ns, ns_ip, str(real_names_list)))
        verbose("; Associated versions: %s" % (str(real_versions_list)))
        verbose("")
        ns_dict[ns] = {'ip': ns_ip, 'servers': real_names_list, 'versions': real_versions_list}
    if data_start.subdomain:
        for number_subdomain in range(len(subdomain_out.split("\n"))):
            for data_sub in subdomain_out.split("\n"):
                if data_sub != "":
                    index_sub = subdomain_out.split("\n").index(data_sub) + 1
                else:
                    index_sub = 0
                subdomains_data[index_sub] = {'Domain:': data_start.domain, 'Subdomain:': data_sub}
    if data_start.output:
        save_data(data_start.output, ns_dict, subdomains_data)
    else:
        print(result_all(ns_dict, subdomains_data))
