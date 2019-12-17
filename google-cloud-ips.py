#!/usr/bin/env python

import dns.resolver


def __main__():
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

  for ip in sorted(ips):
    print(ip)

def resolve_txt(host):
  return dns.resolver.query(host,"TXT").response.answer[0][-1].strings[0]

__main__()
