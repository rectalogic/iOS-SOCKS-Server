import ifaddr
from collections import defaultdict
import socket


def filter_ipv4(ips):
    return [ip.ip for ip in ips if isinstance(ip.ip, str)]


# We want the WiFi address so that clients know what IP to use.
# We want the non-WiFi (cellular?) address so that we can force network
#  traffic to go over that network. This allows the proxy to correctly
#  forward traffic to the cell network even when the WiFi network is
#  internet-enabled but limited (e.g. firewalled)
def find_addresses():
    proxy_host = "172.20.10.1"
    connect_host = None

    interfaces = ifaddr.get_adapters()
    iftypes = defaultdict(list)
    for iface in interfaces:
        if not iface.ips:
            continue
        if iface.name.startswith('lo'):
            continue
        # TODO IPv6 support someday
        if iface.addr.family != socket.AF_INET:
            continue
        # XXX implement better classification of interfaces
        if iface.name.startswith('en'):
            iftypes['en'].append(iface)
        elif iface.name.startswith('bridge'):
            iftypes['bridge'].append(iface)
        else:
            iftypes['cell'].append(iface)

    if iftypes['bridge']:
        iface = iftypes['bridge'][0]
        ips = filter_ipv4(iface.ips)
        print("Assuming proxy will be accessed over hotspot (%s) at %s" %
                (iface.name, ips))
        proxy_host = ips
    elif iftypes['en']:
        iface = iftypes['en'][0]
        ips = filter_ipv4(iface.ips)
        print("Assuming proxy will be accessed over WiFi (%s) at %s" %
                (iface.name, ips))
        proxy_host = ips
    else:
        print('Warning: could not get WiFi address; assuming %s' % proxy_host)

    if iftypes['cell']:
        iface = iftypes['cell'][0]
        ips = filter_ipv4(iface.ips)
        print("Will connect to servers over interface %s at %s" %
                (iface.name, ips))
        connect_host = ips

    return proxy_host, connect_host