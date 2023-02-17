import ifaddr
from collections import defaultdict
import logging

log = logging.getLogger(__name__)


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
        ips = filter_ipv4(iface.ips)
        if not ips:
            continue
        if iface.name.startswith('lo'):
            continue
        log.info("Found %s with ips %s", iface.name, ips)
        # XXX implement better classification of interfaces
        if iface.name.startswith('en'):
            iftypes['en'].extend(ips)
        elif iface.name.startswith('bridge'):
            iftypes['bridge'].extend(ips)
        else:
            iftypes['cell'].extend(ips)

    if iftypes['bridge']:
        ip = iftypes['bridge'][0]
        log.info("Assuming proxy will be accessed over hotspot (%s) at %s", iface.name, ip)
        proxy_host = ip
    elif iftypes['en']:
        ip = iftypes['en'][0]
        log.info("Assuming proxy will be accessed over WiFi (%s) at %s", iface.name, ip)
        proxy_host = ip
    else:
        log.warning('Warning: could not get WiFi address; assuming %s', proxy_host)

    if iftypes['cell']:
        ip = iftypes['cell'][0]
        log.info("Will connect to servers over interface %s at %s", iface.name, ip)
        connect_host = ip

    return proxy_host, connect_host


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    log.info(find_addresses())