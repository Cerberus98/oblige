import re
import sys
import MySQLdb
import time
import melange_objs as melange
import netaddr
import quark_objs as quark
import logging

from datetime import datetime, timedelta
from uuid import uuid4

from utils import _br  # removes leading 'br-'s
from utils import translate_netmask
from utils import to_mac_range
from utils import make_offset_lengths
from utils import make_cidr
from utils import mysqlize
from utils import get_config
from utils import paginate_query
from utils import create_schema
from utils import handle_null
from utils import escape
from utils import stringer
from utils import dater
from utils import nuller

LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(funcName)s: %(lineno)s - %(levelname)s - %(message)s',
        filename='debug.log', filemode='w', level=logging.DEBUG)

NULL = ["NULL", "Null", "null", None, False, 0]

class Oblige(object):
    def __init__(self):
        config = get_config()
        self.db_source = {} # melange
        self.db_destination = {} # quark
        self.db_source['host'] = config.get('source', 'host')
        self.db_source['user'] = config.get('source', 'user')
        self.db_source['pass'] = config.get('source', 'pass')
        self.db_source['db'] = config.get('source', 'db')
        self.db_destination['host'] = config.get('destination', 'host')
        self.db_destination['user'] = config.get('destination', 'user')
        self.db_destination['pass'] = config.get('destination', 'pass')
        self.db_destination['db'] = config.get('destination', 'db')
        
        self.start_time = time.time()
        self.debug = False
        create_schema(self.db_destination)
        conn = MySQLdb.connect(host = self.db_source['host'],
                               user = self.db_source['user'],
                               passwd = self.db_source['pass'],
                               db = self.db_source['db'])
        cursor = conn.cursor()
        cursor.execute("select * from interfaces")
        ifaces = cursor.fetchall()
        self.interfaces = {}
        for interface in ifaces:
            self.interfaces.update({interface[0]: melange.Interface(
                id=interface[0], vif_id_on_device=interface[1],
                device_id=interface[2], tenant_id=interface[3],
                created_at=interface[4])})
        print("Got {} interfaces...".format(len(self.interfaces)))
        cursor.execute("select * from ip_addresses")
        self.ip_addresses = {}
        ipaddrs = cursor.fetchall()
        for ip in ipaddrs:
            self.ip_addresses.update({ip[0]: melange.IpAddress(
                id = ip[0], address = ip[1], interface_id = ip[2],
                ip_block_id = ip[3], used_by_tenant_id = ip[4],
                created_at = ip[5],  # 6 = updated_at
                marked_for_deallocation = handle_null(ip[7]),
                deallocated_at = ip[8], allocated = handle_null(ip[9]))})
        print("Got {} ip_addresses...".format(len(self.ip_addresses)))
        cursor.execute("select * from mac_addresses")
        self.mac_addresses = {} 
        macaddrs = cursor.fetchall()
        for mac in macaddrs:
            self.mac_addresses.update({mac[0]: melange.MacAddress(
                id = mac[0], address = mac[1], mac_address_range_id = mac[2],
                interface_id = mac[3], created_at = mac[4], updated_at = mac[5])})
            self.interfaces[mac[3]].mac_address = mac[1]
        print("Got {} mac_addresses...".format(len(self.mac_addresses)))
        cursor.execute("select * from mac_address_ranges")
        self.mac_address_ranges = {}
        mars = cursor.fetchall()
        for mar in mars:
            self.mac_address_ranges.update({mar[0]: melange.MacAddressRange(
                id = mar[0], cidr = mar[1], next_address = mar[2],
                created_at = mar[3])})
        print("Got {} mac_address_ranges...".format(len(self.mac_address_ranges)))
        cursor.execute("select * from allocatable_macs")
        self.allocatable_macs = {}
        allmacs = cursor.fetchall()
        for amac in allmacs:
            self.allocatable_macs.update({amac[0]: melange.AllocatableMac(
                id = amac[0], mac_address_range_id = amac[1], address = amac[2],
                created_at = amac[3])})
        print("Got {} allocatable_macs...".format(len(self.allocatable_macs)))
        cursor.execute("select * from ip_blocks")
        ipb = cursor.fetchall()
        self.ip_blocks = {}
        for ip_block in ipb:
            self.ip_blocks.update({ip_block[0]: melange.IpBlock(
                id=ip_block[0], network_id=ip_block[1], cidr=ip_block[2],
                created_at=ip_block[3], updated_at = ip_block[4],
                _type=ip_block[5], tenant_id=ip_block[6],
                gateway=ip_block[7], dns1=ip_block[8],
                dns2=ip_block[9], allocatable_ip_counter=ip_block[10],
                is_full=handle_null(ip_block[11]), policy_id=ip_block[12],
                parent_id=ip_block[13], network_name=ip_block[14],
                omg_do_not_use=handle_null(ip_block[15]),
                max_allocation=ip_block[16])})
        print("Got {} ip_blocks...".format(len(self.ip_blocks)))
        cursor.execute("select * from ip_routes")
        self.ip_routes = {}
        iprs = cursor.fetchall()
        for ipr in iprs:
            self.ip_routes.update({ipr[0]: melange.IpRoute(
                id = ipr[0], destination = ipr[1], netmask = ipr[2],
                gateway = ipr[3], source_block_id = ipr[4],
                created_at = ipr[5])})
        print("Got {} ip_routes...".format(len(self.ip_routes)))
        cursor.execute("select * from policies")
        self.policies = {}
        pols = cursor.fetchall()
        for pol in pols:
            self.policies.update({pol[0]: melange.Policy(
                id = pol[0], name = pol[1], tenant_id = pol[2],
                description = pol[3], created_at = pol[4])})
        print("Got {} policies...".format(len(self.policies)))
        cursor.execute("select * from ip_octets")
        self.ip_octets = {}
        ipoc = cursor.fetchall()
        for ipo in ipoc:
            self.ip_octets.update({ipo[0]: melange.IpOctet(
                id = ipo[0], octet = ipo[1], policy_id = ipo[2],
                created_at = ipo[3])})
        print("Got {} ip_octets...".format(len(self.ip_octets)))
        cursor.execute("select * from ip_ranges")
        self.ip_ranges = {}
        iprns = cursor.fetchall()
        for iprn in iprns:
            self.ip_ranges.update({iprn[0]: melange.IpRange(
                id = iprn[0], offset = iprn[1], length = iprn[2],
                policy_id = iprn[3], created_at = iprn[4])})
        print("Got {} ip_ranges...".format(len(self.ip_ranges)))
        cursor.close()
        conn.close()
        
        self.quark_ip_addresses = {}
        self.quark_port_ip_address_associations = {}
        self.quark_ports = {}
        self.quark_mac_addresses = {}
        self.quark_mac_address_ranges = {}
        self.quark_tags = {}
        self.quark_networks = {}
        self.quark_tag_associations = {}
        self.quark_subnets = {}
        self.quark_dns_nameservers = {}
        self.quark_routes = {}
        self.quark_ip_policies = {}
        self.quark_ip_policy_cidrs = {}
        self.quark_nvp_stuff = {}
        self.quark_quotas = {}
        self.policy_ids = {}
        self.interface_network = {}
        self.interface_ip = {}
        self.port_cache = {}
        self.interface_tenant = {}
        self.pubpriv = {}
        print("\tInitialization complete in {:.2f} seconds.".format(
            time.time() - self.start_time))
        
        
    def migrate_networks(self):
        print("Migrating networks...")
        networks = {}
        cell_regex = re.compile("\w{3}-\w{1}\d{4}")
        preprod_cell_regex = re.compile("\w{7}-\w{3}-\w{1}\d{4}")
        m = 0
        prv_rax = quark.QuarkNetwork(id='11111111-1111-1111-1111-111111111111',
                                     tenant_id='rackspace',
                                     created_at=datetime.utcnow(),
                                     name='private',
                                     network_plugin='UNMANAGED',
                                     ipam_strategy='BOTH')
        LOG.info("prv_rax created: {}".format(stringer(prv_rax)))
        pub_rax = quark.QuarkNetwork(id='00000000-0000-0000-0000-000000000000',
                                     tenant_id='rackspace',
                                     created_at=datetime.utcnow(),
                                     name='public',
                                     network_plugin='UNMANAGED',
                                     ipam_strategy='BOTH_REQUIRED')

        LOG.info("pub_rax created: {}".format(stringer(pub_rax)))
        self.quark_networks.update({prv_rax.id: prv_rax})
        self.quark_networks.update({pub_rax.id: pub_rax})
        LOG.info("Added prv_rax and pub_rax to self.quark_networks:"
                " {}".format(stringer(self.quark_networks)))
        LOG.info("Looping over blocks...")
        for block_id, block in self.ip_blocks.iteritems():
            LOG.info("Working on block_id {} block: {}".format(block_id, stringer(block)))
            netplugin = 'NVP'

            if _br(block.network_id) not in networks:
                LOG.info("_br(block.network_id) not in networks: {}".format(_br(block.network_id)))
                networks[_br(block.network_id)] = {
                        "tenant_id": block.tenant_id,
                        "name": block.network_name,
                        "created_at": block.created_at,
                        "network_plugin": netplugin}
                LOG.info("Added networks[{}] = {}".format(_br(block.network_id),
                    stringer(networks[_br(block.network_id)])))
            elif _br(block.network_id) in networks:
                LOG.info("_br(block.network_id) YES in networks: {}".format(_br(block.network_id)))
                if networks[_br(block.network_id)]["created_at"] > block.created_at:
                    LOG.info("Changing created at to {}".format(block.created_at))
                    networks[_br(block.network_id)]["created_at"] = block.created_at
            LOG.info("Done with first pass on block {}".format(_br(block.network_id)))
        LOG.info("#"*80)
        LOG.info("Done with first pass on all blocks.")
        LOG.info("#"*80)
        for net_id, net in networks.iteritems():
            if cell_regex.match(networks[net_id]["tenant_id"]) \
                    or preprod_cell_regex.match(networks[net_id]["tenant_id"]):
                LOG.critical("Cell regex matched {}".format(networks[net_id]["tenant_id"]))
                if net["name"] == 'public':

                    self.pubpriv[net_id] = pub_rax.id
                    q_network = pub_rax
                
                    LOG.info("net['name'] == 'public', setting "
                            "self.pubpriv[{}] = {}".format(net_id, pub_rax.id))
                    LOG.info("q_network set to {}".format(stringer(pub_rax)))
                else:
                    LOG.info("net['name'] != 'public', setting "
                            "self.pubpriv[{}] = {}".format(net_id, prv_rax.id))
                    LOG.info("q_network set to {}".format(stringer(prv_rax)))
                    self.pubpriv[net_id] = prv_rax.id
                    q_network = prv_rax
                LOG.info("Setting self.quark_networks[{}] = {}".format(net_id, stringer(q_network)))
                self.quark_networks[net_id] = q_network
            else: 
                LOG.critical("Cell regex NOT matched {}".format(networks[net_id]["tenant_id"]))
                cache_net = networks[net_id]
                LOG.info("Setting cache_net = networks[{}]".format(net_id))
                LOG.info("cache_net now: {}".format(stringer(cache_net)))
                q_network = quark.QuarkNetwork(id=net_id,
                    tenant_id=cache_net["tenant_id"],
                    name=cache_net["name"],
                    created_at=networks[_br(net_id)]["created_at"],
                    network_plugin=cache_net["network_plugin"],
                    ipam_strategy="ANY")
                LOG.info("Setting self.quark_networks[{}] = {}".format(q_network.id,
                        stringer(q_network)))
                self.quark_networks[q_network.id] = q_network
            m += 1
            LOG.info("Done with network {}".format(net_id))
        LOG.info("#"*80)
        LOG.info("Done with networks")
        LOG.info("#"*80)

        for block_id, block in self.ip_blocks.iteritems():
            LOG.info("Working on block_id {} block {}".format(block_id, stringer(block)))
            LOG.info("isdone = False")
            isdone = False
            if not block.allocatable_ip_counter:
                LOG.info("not block.allocatable_ip_counter")
                block.allocatable_ip_counter = netaddr.IPNetwork(block.cidr).first
                LOG.info("block.allocatable_ip_counter = {}".format(block.allocatable_ip_counter))
            if block.tenant_id not in self.quark_quotas:
                LOG.info("block.tenant_id not in self.quark_quotas")
                self.quark_quotas.update({block.tenant_id: quark.QuarkQuota(
                        id=str(uuid4()),
                        limit=block.max_allocation,
                        tenant_id=block.tenant_id)})
                LOG.info("updating self.quark_quotas:")
                LOG.info("self.quark_quotas[{}] = {}".format(block.tenant_id, stringer(self.quark_quotas[block.tenant_id])))
            else:
                LOG.info("block.tenant_id YES in self.quark_quotas.")
                if block.max_allocation > self.quark_quotas[block.tenant_id].limit:
                    LOG.info("block.max_allocation > self.quark_quotas[block.tenant_id].limit")
                    self.quark_quotas.update({block.tenant_id: quark.QuarkQuota(
                            id=str(uuid4()),
                            limit=block.max_allocation,
                            tenant_id=block.tenant_id)})
                    LOG.info("self.quark_quotas[{}] = {}".format(block.tenant_id,
                        stringer(self.quark_quotas[block.tenant_id])))
            if cell_regex.match(block.tenant_id) \
                    or preprod_cell_regex.match(block.tenant_id):
                LOG.info("block.tenant_id {} matches the cell regex".format(block.tenant_id))
                if block.network_name and 'private' in block.network_name:
                    LOG.info("block.network_name and 'private' in block.network_name")
                    self.quark_subnets.update({block.id: quark.QuarkSubnet(
                            id=block.id,
                            name=block.network_name,
                            tenant_id=block.tenant_id,
                            created_at=block.created_at,
                            network_id='11111111-1111-1111-1111-111111111111',
                            _cidr=block.cidr,
                            first_ip=netaddr.IPNetwork(block.cidr).first,
                            last_ip=netaddr.IPNetwork(block.cidr).last,
                            ip_version=netaddr.IPNetwork(block.cidr).version,
                            ip_policy_id=block.policy_id,
                            next_auto_assign_ip=block.allocatable_ip_counter,
                            tag_association_uuid=None,
                            do_not_use=block.omg_do_not_use,
                            segment_id=block.tenant_id)})
                    LOG.info("self.quark_subnets[{}] = {}".format(block.id,
                            stringer(self.quark_subnets[block.id])))
                    isdone = True
                    LOG.info("isdone = True")
                elif block.network_name and 'public' in block.network_name:
                    LOG.info("block.network_name and 'public' in block.network_name")
                    self.quark_subnets.update({block.id: quark.QuarkSubnet(
                            id=block.id,
                            name=block.network_name,
                            tenant_id=block.tenant_id,
                            created_at=block.created_at,
                            network_id='00000000-0000-0000-0000-000000000000',
                            _cidr=block.cidr,
                            first_ip=netaddr.IPNetwork(block.cidr).first,
                            last_ip=netaddr.IPNetwork(block.cidr).last,
                            ip_version=netaddr.IPNetwork(block.cidr).version,
                            ip_policy_id=block.policy_id,
                            next_auto_assign_ip=block.allocatable_ip_counter,
                            tag_association_uuid=None,
                            do_not_use=block.omg_do_not_use,
                            segment_id=block.tenant_id)})
                    LOG.info("self.quark_subnets[{}] = {}".format(block.id,
                                stringer(self.quark_subnets[block.id])))
                    isdone = True
                    LOG.info("isdone = True")
                if not isdone:
                    LOG.critical("rackspace tenant name {} not in ['public','private'] for ip_block {}".
                            format(block.network_name, block.tenant_id))
            if not isdone:
                LOG.info("not isdone")
                self.quark_subnets.update({block.id: quark.QuarkSubnet(
                        id=block.id,
                        name=block.network_name,
                        tenant_id=block.tenant_id,
                        created_at=block.created_at,
                        network_id=_br(block.network_id),
                        _cidr=block.cidr,
                        first_ip=netaddr.IPNetwork(block.cidr).first,
                        last_ip=netaddr.IPNetwork(block.cidr).last,
                        ip_version=netaddr.IPNetwork(block.cidr).version,
                        ip_policy_id=block.policy_id,
                        next_auto_assign_ip=block.allocatable_ip_counter,
                        tag_association_uuid=None,
                        do_not_use=block.omg_do_not_use)})
                LOG.info("self.quark_subnets[{}] = {}".format(block.id,
                            stringer(self.quark_subnets[block.id])))
            if block.dns1:
                self.quark_dns_nameservers.update({block.id: quark.QuarkDnsNameserver(
                    id=str(uuid4()),
                    ip=int(netaddr.IPAddress(block.dns1)),
                    created_at=block.created_at,
                    tenant_id=block.tenant_id,
                    subnet_id=block.id)})
                LOG.info("self.quark_dns_nameservers[{}] = {}".format(block.id,
                    stringer(self.quark_dns_nameservers[block.id])))
            if block.dns2:
                # TODO XXX : overwriting the block.id nameserver here arent we

                self.quark_dns_nameservers.update({block.id: quark.QuarkDnsNameserver(
                    id=str(uuid4()),
                    ip=int(netaddr.IPAddress(block.dns2)),
                    created_at=block.created_at,
                    tenant_id=block.tenant_id,
                    subnet_id=block.id)})
                LOG.info("self.quark_dns_nameservers[{}] = {}".format(block.id,
                    stringer(self.quark_dns_nameservers[block.id])))
            LOG.info("Calling self.migrate_routes({})".format(block))
            self.migrate_routes(block)
            LOG.info("Done with migrate_routes({})".format(block))
            if block.policy_id:
                LOG.info("YES block.policy_id")
                if block.policy_id not in self.policy_ids.keys():
                    LOG.info("block.policy_id not in self.policy_ids.keys()")
                    self.policy_ids[block.policy_id] = {}
                    LOG.info("Added empty dict, self.policy_ids[{}] = (empty)".format(block.policy_id))
                #if block.network_id in self.pubpriv.keys():
                    #self.policy_ids[block.policy_id][self.pubpriv[block.network_id]] = _br(self.pubpriv[block.network_id])
                self.policy_ids[block.policy_id][block.id] = _br(block.network_id)
                LOG.info("self.policy_ids[{}][{}] = {}".format(block.policy_id, block.id, _br(block.network_id)))
            else:
                LOG.critical("Block lacks policy (this is bad): {}".format(block.id))
        # add routes:
        LOG.info("#"*80)
        LOG.info("Done iterating over self.ip_blocks")
        LOG.info("#"*80)
        LOG.info("migrating new routes")
        for block in self.ip_blocks.values():
            LOG.info("Working on {}".format(block))
            if block.gateway:
                LOG.info("Block has gateway...")
                LOG.info("Calling self.migrate_new_routes({})".format(block))
                self.migrate_new_routes(block)
        LOG.info("Done migrating new routes.")
        LOG.info("-="*40)
        LOG.info("Done with migrate_networks()")
        LOG.info("-="*40)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_routes(self, block):
        LOG.info("In migrate_routes(), iterating over self.ip_routes...")
        for route_id, route in self.ip_routes.iteritems():
            if route.source_block_id == block.id:
                LOG.info("route.source_block_id == block.id")
                self.quark_routes.update({route_id: quark.QuarkRoute(
                    id=route_id,
                    cidr=translate_netmask(route.netmask, route.destination),
                    tenant_id=block.tenant_id,
                    gateway=route.gateway,
                    created_at=block.created_at,
                    subnet_id=block.id,
                    tag_association_uuid=None)})
                LOG.info("self.quark_routes[{}] = {}".format(route_id,
                        stringer(self.quark_routes[route_id])))
        

    def migrate_new_routes(self, block):
        LOG.info("In migrate_new_routes()")
        gateway = netaddr.IPAddress(block.gateway)
        LOG.info("Got a gateway of {}".format(gateway))
        destination = None
        if gateway.version == 4:
            destination = '0.0.0.0/0'
        else:
            destination = '::/0'
        LOG.info("Got gateway = {}".format(destination))
        self.quark_routes.update({block.id: quark.QuarkRoute(
            id=str(uuid4()),
            tag_association_uuid=None,
            cidr=destination,
            tenant_id=block.tenant_id,
            gateway=block.gateway,
            subnet_id=block.id,
            created_at=datetime.utcnow())})
        LOG.info("self.quark_routes[{}] = {}".format(block.id,
                    stringer(self.quark_routes[block.id])))


    def migrate_ips(self):
        print("Migrating ips...")
        LOG.info("Now in migrate_ips()")
        m = 0
        ip_addr_cache = {}
        LOG.info("ip_addr_cache = {}")
        LOG.info("Iterating over self.ip_addresses to build ip_addr_cache")
        for address in self.ip_addresses.values():
            if address.ip_block_id not in ip_addr_cache.keys():
                ip_addr_cache.update({address.ip_block_id: [address]})
            else:
                ip_addr_cache[address.ip_block_id].append(address)
            LOG.info("ip_addr_cache[{}] = {}".format(address.ip_block_id,
                stringer(ip_addr_cache[address.ip_block_id])))
        LOG.info("Done iterating.")
        LOG.info("#"*80)
        LOG.info("Iterating over ip_addr_cache we just built")
        for block_id, addresses in ip_addr_cache.iteritems():
            LOG.info("Working on block_id {}, addresses {}".format(block_id, addresses))
            block = self.ip_blocks[block_id]
            LOG.info("Got block from self.ip_blocks[{}] -> {}".format(block_id, stringer(block)))
            LOG.info("Looping over addresses")
            for address in addresses:
                LOG.info("Now on addresses {}, populating interface_network cache".format(address))
                m += 1
                """Populate interface_network cache"""
                interface_id = address.interface_id
                LOG.info("Got interface_id = {}".format(interface_id))
                if interface_id is not None and\
                        interface_id not in self.interface_network:
                    LOG.info("interface_id is not None and interface_id not in self.interface_network")
                    self.interface_network[interface_id] = _br(block.network_id)
                    LOG.info("Set self.interface_network[{}] = {}".format(interface_id, _br(block.network_id)))
                if interface_id in self.interface_network and\
                        self.interface_network[interface_id] != _br(block.network_id):
                    # TODO XXX --- DOBBY@?!?@ handle this better?
                    LOG.critical("Found interface with different network id: {0} != {1}"
                                 .format(self.interface_network[interface_id],
                                         _br(block.network_id)))
                deallocated = not address.allocated or address.marked_for_deallocation
                LOG.info("Set deallocated to {}".format(deallocated))
                ip_address = netaddr.IPAddress(address.address)
                LOG.info("Set ip_address to {}".format(ip_address))
                if block.network_id in self.pubpriv.keys():
                    LOG.info("block.network_id in self.pubpriv.keys()")
                    block.network_id = self.pubpriv[block.network_id]
                    LOG.info("block.network_id set to {}".format(block.network_id))
                q_ip = quark.QuarkIpAddress(
                       id=address.id,
                       created_at=address.created_at,
                       used_by_tenant_id=address.used_by_tenant_id,
                       network_id=_br(block.network_id),
                       subnet_id=block.id,
                       version=ip_address.version,
                       address_readable=address.address,
                       deallocated_at=address.deallocated_at,
                       _deallocated=deallocated,
                       address=netaddr.strategy.ipv6.str_to_int(
                           ip_address.ipv6().format(dialect=netaddr.ipv6_verbose)),
                       allocated_at=block.updated_at)
                LOG.info("Created q_ip: {}".format(stringer(q_ip)))
                self.quark_ip_addresses.update({address.id: q_ip})
                LOG.info("Updated self.quark_ip_addresses[{}] = ^(this q_ip)".format(address.id))
                if interface_id not in self.interface_ip:
                    LOG.info("interface_id not in self.interface_ip[]... using empty set()")
                    self.interface_ip[interface_id] = set()
                self.interface_ip[interface_id].add(q_ip)
                LOG.info("q_ip added to self.interface_ip[{}]".format(interface_id))
            LOG.info("- "*40)
        LOG.info("-="*40)
        LOG.info("Done migrating ips")
        LOG.info("-="*40)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_interfaces(self):
        print("Migrating interfaces...")
        LOG.info("Migrating interfaces")
        m = 0
        n = 0
        cell_regex = re.compile("\w{3}-\w{1}\d{4}")
        preprod_cell_regex = re.compile("\w{7}-\w{3}-\w{1}\d{4}")
        LOG.info("iterating over self.interfaces")
        for interface_id, interface in self.interfaces.iteritems():
            LOG.info("On interface_id {} interface: {}".format(interface_id, stringer(interface)))
            if interface_id not in self.interface_network:
                LOG.critical("{} not in self.interface_network, no interface to migrate".format(interface_id))
                n += 1
                LOG.info("Continuing.")
                continue
            m += 1
            network_id = self.interface_network[interface_id]
            LOG.info("Got network_id = {}".format(network_id))
            #if network_id in self.pubpriv.keys():
            #    the_block = self.quark_networks[self.pubpriv[network_id]]
            #else:
            the_block = self.quark_networks[network_id]
            LOG.info("Got the block: {}".format(stringer(the_block)))
            debug = False
            bridge_name = None
            LOG.info("bridge_name = None")
            if "rackspace" in the_block.tenant_id: #cell_regex.match(the_block.tenant_id) or preprod_cell_regex.match(the_block.tenant_id):
                # this is a rackspace interface
                LOG.info("'rackspace' in {}".format(the_block.tenant_id))
                if the_block.name == "public":
                    bridge_name = "publicnet"
                    network_id = '00000000-0000-0000-0000-000000000000'
                    LOG.info("publicnet, network_id = {}".format(network_id))
                elif the_block.name == "private":
                    bridge_name = "servicenet"
                    network_id = '11111111-1111-1111-1111-111111111111'
                    LOG.info("servicenet, network_id = {}".format(network_id))
                else:
                    raise Exception("NOOOooooo! Block name not public or private:"
                            " block name = {}".format(the_block.name))
            self.interface_tenant[interface_id] = interface.tenant_id
            LOG.info("self.interface_tenant[{}] = {}".format(interface_id, interface.tenant_id))
            port_id = interface.vif_id_on_device
            LOG.info("port_id = {}".format(port_id))
            if not port_id:
                LOG.info("not port_id so port_id = 'TODO'")
                #LOG.critical("interface.vif_id_on_device is NULL, "
                #             "tenant_id: {0} interface_id: {1}".format(
                #                 interface.tenant_id,
                #                 interface_id))
                port_id = "TODO"
            q_port = quark.QuarkPort(
                    id=interface_id,
                    name=None, # shouldn't matter (Dobby)
                    device_id=interface.device_id,
                    tenant_id=interface.tenant_id,
                    created_at=interface.created_at,
                    backend_key=port_id,
                    network_id=network_id,
                    mac_address=interface.mac_address,
                    bridge=bridge_name, # ['publicnet','servicenet'] depends on env
                    device_owner=None)  # Prolly OKay (Comrade Dovvy)
            lswitch_id = str(uuid4())
            q_nvp_switch = quark.QuarkNvpDriverLswitch(
                    id=lswitch_id,
                    nvp_id=network_id,
                    network_id=network_id,
                    display_name=network_id,
                    port_count=None,
                    transport_zone=None,
                    transport_connector=None,
                    segment_id=None,
                    segment_connector=None)
            q_nvp_port = quark.QuarkNvpDriverLswitchPort(
                    port_id=port_id,
                    switch_id=lswitch_id,
                    created_at=interface.created_at)
            LOG.info("q_port: {}".format(stringer(q_port)))
            LOG.info("q_nvp_switch: {}".format(stringer(q_nvp_switch)))
            LOG.info("q_nvp_port: {}".format(stringer(q_nvp_port)))
            if q_nvp_switch in self.quark_nvp_stuff:
                self.quark_nvp_stuff[q_nvp_switch].append(q_nvp_port)
                LOG.info("q_nvp_port appended to self.quark_nvp_stuff[{}]".format(q_nvp_switch))
            else:
                self.quark_nvp_stuff.update({q_nvp_switch: [q_nvp_port]})
                LOG.info("[q_nvp_port] updated into self.quark_nvp_stuff[{}]".format(q_nvp_switch))
            self.port_cache[interface_id] = q_port
            LOG.info("self.port_cache[{}] = {}".format(interface_id, q_port))
        LOG.info("F"*80)
        LOG.info("Done migrating interfaces.")
        LOG.info("F"*80)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
        print("\t\t{} not migrated (no network).".format(n))


    def associate_ips_with_ports(self):
        print("Migrating port ips...")
        LOG.info("Now in associate_ips_with_ports()...")
        m = 0
        LOG.info("iterating over self.port_cache")
        for port_id, port in self.port_cache.iteritems():
            LOG.info("port_id = {}, port = {}".format(port_id, port))
            self.port_cache[port_id].ip_addresses = self.interface_ip[port_id]
            LOG.info("self.port_cache[{}].ip_addresses = self.interface_ip[{}]".format(port_id, port_id))
            LOG.info("Those would be: ")
            for p in self.interface_ip[port_id]:
                LOG.info("=> {}".format(p))
            m += len(self.interface_ip[port_id])
            LOG.info("done with {}".format(port_id))
        LOG.info("!"*80)
        LOG.info("Done associating ips with ports")
        LOG.info("!"*80)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_macs(self):
        print("Migrating macs...")
        m = 0
        LOG.info("Now in migrate_macs, iterating over self.mac_address_ranges")
        for mac_range_id, mac_range in self.mac_address_ranges.iteritems():
            LOG.info("On mac_range_id {} mac_range{}".format(mac_range_id, mac_range))  
            # there should only be one
            LOG.info("Calling to_mac_range({})".format(mac_range.cidr))
            cidr, first_address, last_address = to_mac_range(mac_range.cidr)
            LOG.info("Back, got {}, {}, {}".format(cidr, first_address, last_address))
            q_range = quark.QuarkMacAddressRange(
                    id=mac_range_id,
                    cidr=cidr,
                    created_at=mac_range.created_at,
                    first_address=first_address,
                    next_auto_assign_mac=mac_range.next_address,
                    last_address=last_address)
            LOG.info("Created q_range = {}".format(q_range))
            self.mac_address_ranges.update({mac_range_id: q_range})
            LOG.info("self.mac_address_ranges[{}] = {}".format(mac_range_id, q_range))
            LOG.info("iterating over self.mac_addresses")
            for mac_id, mac in self.mac_addresses.iteritems():
                dealloc = False
                LOG.info("On mac_id {}, mac {}".format(mac_id, mac))
                if mac.interface_id not in self.interface_network:
                    LOG.critical("mac.interface_id {} not in interface_network.".
                                 format(mac.interface_id))
                    continue
                    # dealloc = True
                m += 1
                tenant_id = self.interface_tenant[mac.interface_id]
                LOG.info("Got tenant_id {} from self.interface_tenant[{}]".format(tenant_id, mac.interface_id))
                q_mac = quark.QuarkMacAddress(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        created_at=mac.created_at,
                        mac_address_range_id=mac_range.id,
                        address=mac.address,
                        deallocated=dealloc,
                        deallocated_at=mac.updated_at)
                LOG.info("Created q_mac = {}".format(q_mac))
                if mac_range_id not in self.quark_mac_addresses:
                    LOG.info("mac_range_id not in self.quark_mac_addresses so creating list")
                    self.quark_mac_addresses.update({mac_range_id: [q_mac]})
                else:
                    LOG.info("Appending q_mac to self.quark_mac_address[{}]".format(mac_range_id))
                    self.quark_mac_addresses[mac_range_id].append(q_mac)
                q_port = self.port_cache[mac.interface_id]
                LOG.info("self.port_cache[{}] =  q_port {}".format(mac.interface_id, q_port))
                q_port.mac_address = q_mac.address
                LOG.info("q_port.mac_address = {}".format(q_mac.address))
            LOG.info("~o "*20)
        LOG.info("E"*80)
        LOG.info("Done migrating macs")
        LOG.info("E"*80)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_policies(self):
        print("Migrating policies...")
        LOG.info("Now migrating_policies")
        m = 0
        octets = self.ip_octets.values()
        offsets = self.ip_ranges.values()
        LOG.info("octets: {}".format(octets))
        LOG.info("offsets: {}".format(offsets))
        LOG.info("Iterating over self.policy_ids")
        for policy, policy_block_ids in self.policy_ids.items():
            LOG.debug("Migrating policy {}".format(policy))
            m += 1
            policy_octets = [o.octet for o in octets if o.policy_id == policy]
            LOG.info("got policy_octets = [{}]".format(policy_octets))
            policy_rules = [(off.offset, off.length) for off in offsets
                            if off.policy_id == policy]
            LOG.info("got policy_rules = [{}]".format(policy_rules))
            policy_rules = make_offset_lengths(policy_octets, policy_rules)
            LOG.info("Made new policy_rules by calling make_offset_lengths(policy_octets, policy_rules)")
            LOG.info("policy_rules now = {}".format(policy_rules))
            a = [o.created_at for o in octets if o.policy_id == policy]
            b = [off.created_at for off in offsets if off.policy_id == policy]
            try:
                oct_created_at = min(a)
            except Exception:
                oct_created_at = datetime.utcnow()
            try:
                ran_created_at = min(b)
            except Exception:
                ran_created_at = datetime.utcnow()
            min_created_at = min([oct_created_at, ran_created_at])
            LOG.info("oct_created_at = {}".format(oct_created_at))
            LOG.info("ran_created_at = {}".format(ran_created_at))
            try:
                policy_description = policy.description
            except Exception:
                policy_description = None
            LOG.info("policy_description = {}".format(policy_description))
            LOG.info("iterating over policy_block_ids.keys()")
            for block_id in policy_block_ids.keys():
                LOG.debug("Migration block_id policy {}".format(block_id))
                policy_uuid = policy
                LOG.info("policy_uuid = {}".format(policy))
                if block_id in self.pubpriv.keys():
                    LOG.info("block.id in self.pubpriv.keys()")
                    q_network = self.quark_networks[self.pubpriv[policy_block_ids[block_id]]]
                    LOG.info("q_network = {}".format(q_network))
                else:
                    LOG.info("block.id NOT in self.pubpriv.keys()")
                    q_network = self.quark_networks[policy_block_ids[block_id]]
                    LOG.info("q_network = {}".format(q_network))
                the_name = self.policies[policy].name
                LOG.info("the_name = {}".format(the_name))
                if not policy_description:
                    LOG.info("not policy_description")
                    the_desc = the_name
                    LOG.info("the_desc = {}".format(the_desc))
                q_ip_policy = quark.QuarkIpPolicy(
                        id=policy_uuid,
                        tenant_id=q_network.tenant_id,
                        description=policy_description or the_desc,
                        created_at=min_created_at,
                        name=the_name)
                LOG.info("created q_ip_policy = {}".format(q_ip_policy))
                self.quark_ip_policies.update({policy_uuid: q_ip_policy})
                LOG.info("self.quark_ip_policies[{}] = {}".format(policy_uuid, q_ip_policy))
                LOG.info("iterating over policy_rules")
                for rule in policy_rules:
                    LOG.debug("Migrating policy rule {}".format(rule))
                    #if block_id in self.pubpriv.keys():
                    #    outer_cidr = self.ip_blocks[block_id].cidr
                    #else:
                    outer_cidr = self.ip_blocks[block_id].cidr
                    LOG.info("Got outer_cidr {}".format(outer_cidr))
                    _cidr = make_cidr(outer_cidr, rule[0], rule[1])
                    LOG.debug("Make cidr (MMM!) {}".format(_cidr))
                    if _cidr:
                        q_ip_policy_cidr = quark.QuarkIpPolicyRule(
                                      id=str(uuid4()),
                                      cidr=_cidr,
                                      ip_policy_id=policy_uuid,
                                      created_at=min_created_at)
                        LOG.info("q_ip_policy_cidr = {}".format(q_ip_policy_cidr))
                        if q_ip_policy.id in self.quark_ip_policy_cidrs.keys():
                            self.quark_ip_policy_cidrs[q_ip_policy.id].append(q_ip_policy_cidr)
                            LOG.info("q_ip_policy_cidr appended to self.quark_ip_policy_cidrs[{}]".format(q_ip_policy.id))
                        else:
                            self.quark_ip_policy_cidrs.update({q_ip_policy.id: [q_ip_policy_cidr]})
                            LOG.info("New q_ip_policy_cidrs list at self.quark_ip_policy_cidrs[{}]".format(q_ip_policy.id))
                    else:
                        LOG.critical("*(#@&%$# No policy cidr created for rule {} block {}".format(
                            rule, block_id))
                LOG.info("Done with these rules.")
            LOG.info("Done with this block_id")
        LOG.info("><> "*10)
        LOG.info("Done migrating policies")
        LOG.info("><> "*10)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def insert_networks(self, cursor, connection):
        print("Inserting networks...")
        m = 0
        query = """INSERT 
        INTO quark_networks ( `id`, `tenant_id`, `created_at`, 
            `name`, `ipam_strategy`, `network_plugin`) 
        VALUES """
        ids = set([record.id for record in self.quark_networks.values()])
        for record in self.quark_networks.values():
            if record.id not in ids:
                continue
            ids.remove(record.id)
            m += 1
            #record = mysqlize(record)
            record.tenant_id = escape(record.tenant_id)
            record.name = escape(record.name)
            query += "('{0}','{1}','{2}','{3}','{4}','{5}'),\n".format(record.id,
                                                   record.tenant_id,
                                                   record.created_at,
                                                   record.name,
                                                   record.ipam_strategy,
                                                   record.network_plugin)
        query = query.rstrip(',\n')
        with open('query/insert_networks.sql', 'w') as f:
            f.write(query)
        #LOG.info(query)
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m))


    def insert_ports(self, cursor, connection):
        print("Inserting ports...")
        m = 0
        query = """INSERT 
        INTO quark_ports ( `id`, `tenant_id`, `created_at`, `name`,
            `admin_state_up`, `network_id`, `backend_key`, `mac_address`,
            `device_id`, `device_owner`, `bridge`)
        VALUES """
        all_records = []
        for record in self.port_cache.values():
            #record = mysqlize(record)
            record.name = escape(record.name)
            record.created_at = dater(record.created_at)
            record.device_id = escape(record.device_id)
            record.tenant_id = escape(record.tenant_id)
            record.device_owner = nuller(record.device_id)
            record.bridge = escape(record.bridge)

            if record.device_id == 'NULL':
                LOG.critical("NULL device_id in {}".format(stringer(record)))
                record.device_id = "'NULL'"
            m += 1
            all_records.append("('{0}',{1},{2},{3},{4},'{5}','{6}',{7},{8},{9},{10}),\n".format(
                    record.id, # varchar NOT null
                    record.tenant_id, #varchar nullable
                    record.created_at, # datetime nullable
                    record.name, # varchar nullable
                    record.admin_state_up, # tinyint nullable
                    record.network_id, # varchar NOT null
                    record.backend_key, # varchar NOT null
                    record.mac_address, # bigint nullable
                    record.device_id, # varchar NOT null
                    record.device_owner, # varchar nullable
                    record.bridge)) # varchar nullable
        chunks = paginate_query(all_records)
        with open('query/insert_ports.sql', 'w') as f:
            for i, chunk in enumerate(chunks):
                chunk_query = query + chunk
                chunk_query = chunk_query.rstrip(',\n')
                f.write(chunk_query)
                #LOG.info(chunk_query)
                cursor.execute(chunk_query)
                connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m)) 
   

    def insert_subnets(self, cursor, connection):
        print("Inserting subnets...")
        m = 0
        query = """INSERT
        INTO quark_subnets (
            `id`, `tenant_id`, `created_at`, `network_id`, `_cidr`, `first_ip`,
            `last_ip`, `ip_version`, `next_auto_assign_ip`, `tag_association_uuid`,
            `do_not_use`, `name`, `ip_policy_id`, `enable_dhcp`, `segment_id`)
        VALUES """
        for record in self.quark_subnets.values():
            m += 1
            record = mysqlize(record)
            query += "({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.created_at,
                    record.network_id,
                    record._cidr,
                    record.first_ip,
                    record.last_ip,
                    record.ip_version,
                    record.next_auto_assign_ip,
                    record.tag_association_uuid,
                    record.do_not_use,
                    record.name,
                    record.ip_policy_id,
                    record.enable_dhcp,
                    record.segment_id)
        
        with open('query/insert_subnets.sql', 'w') as f:
            f.write(query)
        #LOG.info(query)
        cursor.execute(query.rstrip(',\n'))
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def insert_ip_addresses(self, cursor, connection):
        print("Inserting ip addresses...")
        m = 0
        query = """INSERT
        INTO quark_ip_addresses (
            `id`, `address_readable`, `address`, `used_by_tenant_id`,
            `created_at`, `subnet_id`, `network_id`, `version`,
            `_deallocated`, `deallocated_at`, `allocated_at`)
        VALUES """
        all_records = []
        for record in self.quark_ip_addresses.values():
            record = mysqlize(record)
            m += 1
            all_records.append("({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}),\n".format(
                    record.id,
                    record.address_readable,
                    record.address,
                    record.used_by_tenant_id,
                    record.created_at,
                    record.subnet_id,
                    record.network_id,
                    record.version,
                    record._deallocated,
                    record.deallocated_at,
                    record.allocated_at))
        chunks = paginate_query(all_records)
    
        with open('query/insert_ip_addresses.sql', 'w') as f:
            for i, chunk in enumerate(chunks):
                chunk_query = query + chunk
                chunk_query = chunk_query.rstrip(',\n')
                f.write(chunk_query)
                #LOG.info(chunk_query)
                cursor.execute(chunk_query)
                connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m))


    def insert_port_ip_assn(self, cursor, connection):
        print("Inserting port_ip_address_associations...")
        m = 0
        query_head = """INSERT
        INTO quark_port_ip_address_associations ( `port_id`, `ip_address_id`)
        VALUES """
        all_records = []
        for port_id, port in self.port_cache.iteritems():
            for ip in list(port.ip_addresses):
                m += 1
                all_records.append("('{0}',{1}),\n".format(port_id, ip.id))
        chunks = paginate_query(all_records)
        with open('query/insert_port_ip_assn.sql', 'w') as f:
            for i, chunk in enumerate(chunks):
                chunk_query = query_head + chunk
                chunk_query = chunk_query.rstrip(',\n')
                f.write(chunk_query)
                #LOG.info(chunk_query)
                cursor.execute(chunk_query)
                connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
    

    def insert_policies(self, cursor, connection):
        print("Inserting policies...")
        m = 0
        query = """ INSERT
        INTO quark_ip_policy ( `id`, `name`, `tenant_id`, `description`,
            `created_at`)
        VALUES """
        for record in self.quark_ip_policies.values():
            m += 1
            record = mysqlize(record)
            query += "({0},{1},{2},{3},{4}),\n".format(
                    record.id,
                    record.name,
                    record.tenant_id,
                    record.description,
                    record.created_at)
        #LOG.info(query)
    
        with open('query/insert_ip_policies.sql', 'w') as f:
            f.write(query.rstrip(',\n'))
        cursor.execute(query.rstrip(',\n'))
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
   

    def insert_lswitches(self, cursor, connection):
        print("Inserting nvp driver lswitches...")
        m = 0
        query = """ INSERT 
        INTO quark_nvp_driver_lswitch ( `id`, `nvp_id`, `network_id`,
            `display_name`, `port_count`, `transport_zone`, `transport_connector`,
            `segment_id`)
        VALUES """
        port_query = """ INSERT
        INTO quark_nvp_driver_lswitchport ( `id`, `port_id`, `switch_id`,
            `created_at`)
        VALUES """
        switchids = []
        for switch, ports in self.quark_nvp_stuff.iteritems():
            switch = mysqlize(switch)
            query += "({0},{1},{2},{3},{4},{5},{6},{7}),\n".format(
                    switch.id,
                    switch.nvp_id,
                    switch.network_id,
                    switch.display_name,
                    switch.port_count,
                    switch.transport_zone,
                    switch.transport_connector,
                    switch.segment_connector,
                    switch.segment_id)
            for port in ports:
                if port.port_id != 'TODO':
                    m += 1
                    port = mysqlize(port)
                    port_query += "('{0}',{1},{2},{3}),\n".format(str(uuid4()),
                            port.port_id, switch.id, port.created_at)
        query = query.rstrip(',\n')
        port_query = port_query.rstrip(',\n')
        with open('query/insert_nvp_driver_lswitch.sql', 'w') as f:
            f.write(query)
        with open('query/insert_nvp_driver_lswitchport.sql', 'w') as f:
            f.write(port_query)
        cursor.execute(query)
        connection.commit()
        cursor.execute(port_query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
   

    def insert_mac_addresses(self, cursor, connection):
        print("Inserting mac addressess...")
        m = 0
        all_records = []
        query = """ INSERT
        INTO quark_mac_addresses ( `tenant_id`, `created_at`, `address`,
            `mac_address_range_id`, `deallocated`, `deallocated_at`)
        VALUES """
        for mac_range_id, macs in self.quark_mac_addresses.iteritems():
            try:
                mac_range = self.mac_address_ranges[mac_range_id]
                # There is only one mac range so this is fine:
                _query = """ INSERT
                         INTO quark_mac_address_ranges ( `id`, `created_at`, `cidr`,
                              `first_address`, `last_address`, `next_auto_assign_mac`)
                          VALUES ('{0}','{1}','{2}',{3},{4},{5})""".format(
                               mac_range.id,
                               mac_range.created_at,
                               mac_range.cidr,
                               mac_range.first_address,
                               mac_range.last_address,
                               mac_range.next_auto_assign_mac)
                with open('query/insert_mac_address_ranges.sql', 'w') as f:
                    f.write(_query)
                cursor.execute(_query)
                connection.commit()
            except MySQLdb.Error, e:
                try:
                    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                except IndexError:
                    print "MySQL Error: %s" % str(e)
            for mac in macs:
                m += 1
                # mac = mysqlize(mac)
                all_records.append("('{0}','{1}',{2},'{3}',0,'{5}'),\n".format(
                        mac.tenant_id,
                        mac.created_at,
                        mac.address,
                        mac.mac_address_range_id,
                        mac.deallocated,
                        mac.deallocated_at))
        chunks = paginate_query(all_records)
        with open('query/insert_mac_addresses.sql', 'w') as f:
            for i, chunk in enumerate(chunks):
                chunk_query = query + chunk
                chunk_query = chunk_query.rstrip(',\n')
                f.write(chunk_query)
                #LOG.info(chunk_query)
                cursor.execute(chunk_query)
                connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def insert_routes(self, cursor, connection):
        print("Inserting routes...")
        query = """ INSERT
        INTO quark_routes ( `id`, `tenant_id`, `created_at`, `cidr`,
            `gateway`, `subnet_id`, `tag_association_uuid`)
        VALUES """
        for route_id, route in self.quark_routes.iteritems():
            record = mysqlize(route)
            query += "({0},{1},{2},{3},{4},{5},{6}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.created_at,
                    record.cidr,
                    record.gateway,
                    record.subnet_id,
                    record.tag_association_uuid)
        query = query.rstrip(',\n')
        #LOG.info(query)

        with open('query/insert_routes.sql', 'w') as f:
            f.write(query)
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_routes)))


    def insert_quark_dns_nameservers(self, cursor, connection):
        print("Inserting dns nameservers...")
        query = """ INSERT
        INTO quark_dns_nameservers ( `id`, `tenant_id`, `created_at`,
            `ip`, `subnet_id`, `tag_association_uuid`)
        VALUES """
        for ns_id, ns in self.quark_dns_nameservers.iteritems():
            record = mysqlize(ns)
            query += "({0},{1},{2},{3},{4},{5}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.created_at,
                    record.ip,
                    record.subnet_id,
                    record.tag_association_uuid)
        query = query.rstrip(',\n')
        #LOG.info(query)
        with open('query/insert_dns_nameservers.sql', 'w') as f:
            f.write(query)
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_dns_nameservers)))


    def insert_ip_policy_rules(self, cursor, connection):
        print("Inserting ip policy cidrs...")
        query = """ INSERT
        INTO quark_ip_policy_cidrs ( `id`, `ip_policy_id`, `created_at`, `cidr`)
        VALUES """
        for rule_id, rules in self.quark_ip_policy_cidrs.iteritems():
            for rule in rules:
                record = mysqlize(rule)
                query += "({0},{1},{2},{3}),\n".format(
                        record.id,
                        record.ip_policy_id,
                        record.created_at,
                        record.cidr)
        query = query.rstrip(',\n')
        #LOG.info(query)
        with open('query/insert_ip_policy_cidrs.sql', 'w') as f:
            f.write(query)
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_ip_policy_cidrs)))


    def insert_quotas(self, cursor, connection):
        print("Inserting quotas...")
        query = """ INSERT
        INTO quotas ( `id`, `tenant_id`, `limit`, `resource`) 
        VALUES """
        for tenant_id, quota in self.quark_quotas.iteritems():
            record = mysqlize(quota)
            query += "({0},{1},{2},{3}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.limit,
                    record.resource)
        query = query.rstrip(',\n')
        #LOG.info(query)
        with open('query/insert_quotas.sql', 'w') as f:
            f.write(query)
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_quotas)))


    def migrates(self):
        self.migrate_networks()
        self.migrate_ips()
        self.migrate_interfaces()
        self.associate_ips_with_ports()
        self.migrate_macs()
        self.migrate_policies()


    def inserts(self):
        conn = MySQLdb.connect(host = self.db_destination['host'],
                           user = self.db_destination['user'],
                           passwd = self.db_destination['pass'],
                           db = self.db_destination['db'])
        cursor = conn.cursor()
        # these have to be in this order or the key constriants fail
        self.insert_networks(cursor, conn)
        self.insert_ports(cursor, conn)
        self.insert_policies(cursor, conn)
        self.insert_subnets(cursor, conn)
        self.insert_ip_addresses(cursor, conn)
        self.insert_port_ip_assn(cursor, conn)
        self.insert_lswitches(cursor, conn)
        self.insert_mac_addresses(cursor, conn)
        self.insert_routes(cursor, conn)
        self.insert_quark_dns_nameservers(cursor, conn)
        self.insert_ip_policy_rules(cursor, conn)
        self.insert_quotas(cursor, conn)
        cursor.close()
        conn.close()


if __name__ == "__main__":
    o = Oblige()
    print("-" * 40)
    o.migrates()
    print("-" * 40)
    o.inserts()
    print("-" * 40)
    print("TOTAL TIME: {}".format(timedelta(seconds=time.time()-o.start_time)))
    logging.shutdown()
