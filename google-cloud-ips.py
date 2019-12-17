#!/usr/bin/env python

import dns.resolver, subprocess, os, sys

import yaml
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def __main__():
  if len(sys.argv) < 2:
    list_ips()
  else:
    gcp_firewall_update(sys.argv[1])


def gcp_firewall_update(name):
  cur = gcp_firewall_describe(name)

  new = []
  seen = {}
  for ip in cur['sourceRanges']:
    seen[ip] = True
    new.append(ip)

  for ip in get_ips():
    if ip not in seen:
      new.append(ip)

  r = subprocess.run(['gcloud', 'compute', 'firewall-rules', 'update', name,
    '--source-ranges=' + ",".join(new)], stdout=subprocess.PIPE)
  print(r)

def gcp_firewall_describe(name):
  r = subprocess.run(['gcloud', 'compute', 'firewall-rules', 'describe', name], stdout=subprocess.PIPE)
  fd = StringIO(r.stdout.decode("utf-8"))
  return yaml.load(fd)


def list_ips():
  for ip in get_ips():
    print(ip)


def get_ips():
  blocks = resolve_txt("_cloud-netblocks.googleusercontent.com")

  ips = set()

  for block in blocks.split():
    parts = block.split(b':')
    if len(parts) > 1 and parts[0] == b'include':
      block_ips = resolve_txt(parts[1].decode("utf-8"))
      for block_ip in block_ips.split():
        bip_parts = block_ip.split(b':')
        if len(bip_parts) > 1 and bip_parts[0] == b'ip4':
          ips.add(bip_parts[1].decode("utf-8"))

  return sorted(ips)


def resolve_txt(host):
  return dns.resolver.query(host,"TXT").response.answer[0][-1].strings[0]


__main__()
