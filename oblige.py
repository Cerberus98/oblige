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

LOG = logging.getLogger(__name__)
logging.basicConfig(format='%(funcName)s: %(lineno)s - %(message)s',
        filename='oblige_debug.log', level=logging.DEBUG)

# TODO: paginate query all the inserts
# TODO: remove the mysqlize calls
# TODO: run times on all the DBs


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
                id=interface[0],
                vif_id_on_device=interface[1],
                device_id=interface[2],
                tenant_id=interface[3],
                created_at=interface[4])})
        print("Got {} interfaces...".format(len(self.interfaces)))

        cursor.execute("select * from ip_addresses")
        self.ip_addresses = {}
        ipaddrs = cursor.fetchall()
        for ip in ipaddrs:
            self.ip_addresses.update({ip[0]: melange.IpAddress(
                id = ip[0],
                address = ip[1],
                interface_id = ip[2],
                ip_block_id = ip[3],
                used_by_tenant_id = ip[4],
                created_at = ip[5],  # 6 = updated_at
                marked_for_deallocation = handle_null(ip[7]),
                deallocated_at = ip[8],
                allocated = handle_null(ip[9]))})
        print("Got {} ip_addresses...".format(len(self.ip_addresses)))

        cursor.execute("select * from mac_addresses")
        self.mac_addresses = {} 
        macaddrs = cursor.fetchall()
        for mac in macaddrs:
            self.mac_addresses.update({mac[0]: melange.MacAddress(
                id = mac[0],
                address = mac[1],
                mac_address_range_id = mac[2],
                interface_id = mac[3],
                created_at = mac[4],
                updated_at = mac[5])})
            self.interfaces[mac[3]].mac_address = mac[1]
        print("Got {} mac_addresses...".format(len(self.mac_addresses)))

        cursor.execute("select * from mac_address_ranges")
        self.mac_address_ranges = {}
        mars = cursor.fetchall()
        for mar in mars:
            self.mac_address_ranges.update({mar[0]: melange.MacAddressRange(
                id = mar[0],
                cidr = mar[1],
                next_address = mar[2],
                created_at = mar[3])})
        print("Got {} mac_address_ranges...".format(len(self.mac_address_ranges)))

        cursor.execute("select * from allocatable_macs")
        self.allocatable_macs = {}
        allmacs = cursor.fetchall()
        for amac in allmacs:
            self.allocatable_macs.update({amac[0]: melange.AllocatableMac(
                id = amac[0],
                mac_address_range_id = amac[1],
                address = amac[2],
                created_at = amac[3])})
        print("Got {} allocatable_macs...".format(len(self.allocatable_macs)))

        cursor.execute("select * from ip_blocks")
        ipb = cursor.fetchall()
        self.ip_blocks = {}
        for ip_block in ipb:
            self.ip_blocks.update({ip_block[0]: melange.IpBlock(
                id=ip_block[0],
                network_id=ip_block[1],
                cidr=ip_block[2],
                created_at=ip_block[3],
                updated_at = ip_block[4],
                _type=ip_block[5],
                tenant_id=ip_block[6],
                gateway=ip_block[7],
                dns1=ip_block[8],
                dns2=ip_block[9],
                allocatable_ip_counter=ip_block[10],
                is_full=handle_null(ip_block[11]),
                policy_id=ip_block[12],
                parent_id=ip_block[13],
                network_name=ip_block[14],
                omg_do_not_use=handle_null(ip_block[15]),
                max_allocation=ip_block[16])})
        print("Got {} ip_blocks...".format(len(self.ip_blocks)))

        cursor.execute("select * from ip_routes")
        self.ip_routes = {}
        iprs = cursor.fetchall()
        for ipr in iprs:
            self.ip_routes.update({ipr[0]: melange.IpRoute(
                id = ipr[0],
                destination = ipr[1],
                netmask = ipr[2],
                gateway = ipr[3],
                source_block_id = ipr[4],
                created_at = ipr[5])})
        print("Got {} ip_routes...".format(len(self.ip_routes)))

        cursor.execute("select * from policies")
        self.policies = {}
        pols = cursor.fetchall()
        for pol in pols:
            self.policies.update({pol[0]: melange.Policy(
                id = pol[0],
                name = pol[1],
                tenant_id = pol[2],
                description = pol[3],
                created_at = pol[4])})
        print("Got {} policies...".format(len(self.policies)))

        cursor.execute("select * from ip_octets")
        self.ip_octets = {}
        ipoc = cursor.fetchall()
        for ipo in ipoc:
            self.ip_octets.update({ipo[0]: melange.IpOctet(
                id = ipo[0],
                octet = ipo[1],
                policy_id = ipo[2],
                created_at = ipo[3])})
        print("Got {} ip_octets...".format(len(self.ip_octets)))

        cursor.execute("select * from ip_ranges")
        self.ip_ranges = {}
        iprns = cursor.fetchall()
        for iprn in iprns:
            self.ip_ranges.update({iprn[0]: melange.IpRange(
                id = iprn[0],
                offset = iprn[1],
                length = iprn[2],
                policy_id = iprn[3],
                created_at = iprn[4])})
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

        print("\tInitialization complete in {:.2f} seconds.".format(
            time.time() - self.start_time))
        
        
    def migrate_networks(self):
        print("Migrating networks...")
        networks = {}
        cell_regex = re.compile("\w{3}-\w{1}\d{4}")
        m = 0
        prv_rax = quark.QuarkNetwork(id='11111111-1111-1111-1111-111111111111',
                                     tenant_id='rackspace',
                                     created_at=datetime.utcnow(),
                                     name='private',
                                     network_plugin='UNMANAGED',
                                     ipam_strategy='BOTH')
        
        pub_rax = quark.QuarkNetwork(id='00000000-0000-0000-0000-000000000000',
                                     tenant_id='rackspace',
                                     created_at=datetime.utcnow(),
                                     name='public',
                                     network_plugin='UNMANAGED',
                                     ipam_strategy='BOTH_REQUIRED')

        self.quark_networks.update({prv_rax.id: prv_rax})
        self.quark_networks.update({pub_rax.id: pub_rax})
        
        for block_id, block in self.ip_blocks.iteritems():
            netplugin = 'NVP'
            if _br(block.network_id) not in networks:
                networks[_br(block.network_id)] = {
                        "tenant_id": block.tenant_id,
                        "name": block.network_name,
                        "created_at": block.created_at,
                        "network_plugin": netplugin}
            elif _br(block.network_id) in networks:
                if networks[_br(block.network_id)]["created_at"] > block.created_at:
                    networks[_br(block.network_id)]["created_at"] = block.created_at
        for net_id, net in networks.iteritems():
            cache_net = networks[net_id]
            q_network = quark.QuarkNetwork(id=net_id,
                    tenant_id=cache_net["tenant_id"],
                    name=cache_net["name"],
                    created_at=networks[_br(net_id)]["created_at"],
                    network_plugin=cache_net["network_plugin"],
                    ipam_strategy="ANY")
            self.quark_networks[q_network.id] = q_network
            m += 1
        
        for block_id, block in self.ip_blocks.iteritems():
            isdone = False
            if not block.allocatable_ip_counter:
                block.allocatable_ip_counter = netaddr.IPNetwork(block.cidr).first
            
            if block.tenant_id not in self.quark_quotas:
                self.quark_quotas.update({block.tenant_id: quark.QuarkQuota(
                        id=str(uuid4()),
                        limit=block.max_allocation,
                        tenant_id=block.tenant_id)})
            else:
                if block.max_allocation > self.quark_quotas[block.tenant_id].limit:
                    self.quark_quotas.update({block.tenant_id: quark.QuarkQuota(
                            id=str(uuid4()),
                            limit=block.max_allocation,
                            tenant_id=block.tenant_id)})
            
            if cell_regex.match(block.tenant_id):
                if block.network_name and 'private' in block.network_name:
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
                            do_not_use=0)})
                    isdone = True
                elif block.network_name and 'public' in block.network_name:
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
                            do_not_use=0)})
                    isdone = True
                if not isdone:
                    LOG.critical("rackspace tenant name {} not in ['public','private'] for ip_block {}".
                            format(block.network_name, block.tenant_id))
            if not isdone:
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
            if block.dns1: 
                self.quark_dns_nameservers.update({block.id: quark.QuarkDnsNameserver(
                    id=str(uuid4()),
                    ip=int(netaddr.IPAddress(block.dns1)),
                    created_at=block.created_at,
                    tenant_id=block.tenant_id,
                    subnet_id=block.id)})
            if block.dns2:
                self.quark_dns_nameservers.update({block.id: quark.QuarkDnsNameserver(
                    id=str(uuid4()),
                    ip=int(netaddr.IPAddress(block.dns2)),
                    created_at=block.created_at,
                    tenant_id=block.tenant_id,
                    subnet_id=block.id)})
            self.migrate_routes(block)
            if block.policy_id:
                if block.policy_id not in self.policy_ids.keys():
                    self.policy_ids[block.policy_id] = {}
                self.policy_ids[block.policy_id][block.id] = _br(block.network_id)
            else:
                LOG.critical("Block lacks policy (this is bad): {}".format(block.id))
        # add routes:
        for block in self.ip_blocks.values():
            if block.gateway:
                self.migrate_new_routes(block)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_routes(self, block):
        for route_id, route in self.ip_routes.iteritems():
            if route.source_block_id == block.id:
                self.quark_routes.update({route_id: quark.QuarkRoute(
                    id=route_id,
                    cidr=translate_netmask(route.netmask, route.destination),
                    tenant_id=block.tenant_id,
                    gateway=route.gateway,
                    created_at=block.created_at,
                    subnet_id=block.id,
                    tag_association_uuid=None)})
    

    def migrate_new_routes(self, block):
        gateway = netaddr.IPAddress(block.gateway)
        destination = None
        if gateway.version == 4:
            destination = '0.0.0.0/0'
        else:
            destination = '::/0'
        self.quark_routes.update({block.id: quark.QuarkRoute(
            id=str(uuid4()),
            tag_association_uuid=None,
            cidr=destination,
            tenant_id=block.tenant_id,
            gateway=block.gateway,
            subnet_id=block.id,
            created_at=datetime.utcnow())})


    def migrate_ips(self):
        print("Migrating ips...")
        m = 0
        ip_addr_cache = {}
        for address in self.ip_addresses.values():
            if address.ip_block_id not in ip_addr_cache.keys():
                ip_addr_cache.update({address.ip_block_id: [address]})
            else:
                ip_addr_cache[address.ip_block_id].append(address)
        for block_id, addresses in ip_addr_cache.iteritems():
            block = self.ip_blocks[block_id]
            for address in addresses:
                m += 1
                """Populate interface_network cache"""
                interface_id = address.interface_id
                if interface_id is not None and\
                        interface_id not in self.interface_network:
                    self.interface_network[interface_id] = _br(block.network_id)
                if interface_id in self.interface_network and\
                        self.interface_network[interface_id] != _br(block.network_id):
                    LOG.critical("Found interface with different network id: {0} != {1}"
                                 .format(self.interface_network[interface_id],
                                         _br(block.network_id)))

                deallocated = not address.allocated or address.marked_for_deallocation
                ip_address = netaddr.IPAddress(address.address)
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
                self.quark_ip_addresses.update({address.id: q_ip})
                if interface_id not in self.interface_ip:
                    self.interface_ip[interface_id] = set()
                self.interface_ip[interface_id].add(q_ip)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_interfaces(self):
        print("Migrating interfaces...")
        m = 0
        n = 0
        cell_regex = re.compile("\w{3}-\w{1}\d{4}")
        for interface_id, interface in self.interfaces.iteritems():
            if interface_id not in self.interface_network:
                LOG.critical("No network for {}".format(interface_id))
                n += 1
                continue
            m += 1
            network_id = self.interface_network[interface_id]
            the_block = self.quark_networks[network_id]
            debug = False
            bridge_name = None
            if cell_regex.match(the_block.tenant_id):
                # this is a rackspace interface
                if the_block.name == "public":
                    bridge_name = "publicnet"
                    network_id = '00000000-0000-0000-0000-000000000000'
                elif the_block.name == "private":
                    bridge_name = "servicenet"
                    network_id = '11111111-1111-1111-1111-111111111111'
                else:
                    raise Exception("NOOOooooo! Block name not public or private:"
                            " block name = {}".format(the_block.name))
            self.interface_tenant[interface_id] = interface.tenant_id
            port_id = interface.vif_id_on_device
            if not port_id:
                LOG.critical("interface.vif_id_on_device is NULL, "
                             "tenant_id: {0} interface_id: {1}".format(
                                 interface.tenant_id,
                                 interface_id))
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
            if q_nvp_switch in self.quark_nvp_stuff:
                self.quark_nvp_stuff[q_nvp_switch].append(q_nvp_port)
            else:
                self.quark_nvp_stuff.update({q_nvp_switch: [q_nvp_port]})
            self.port_cache[interface_id] = q_port
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
        print("\t\t{} not migrated (no network).".format(n))


    def associate_ips_with_ports(self):
        print("Migrating port ips...")
        m = 0
        for port_id, port in self.port_cache.iteritems():
            self.port_cache[port_id].ip_addresses = self.interface_ip[port_id]
            m += len(self.interface_ip[port_id])
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_macs(self):
        print("Migrating macs...")
        m = 0
        for mac_range_id, mac_range in self.mac_address_ranges.iteritems():
            # there should only be one
            cidr, first_address, last_address = to_mac_range(mac_range.cidr)
            q_range = quark.QuarkMacAddressRange(
                    id=mac_range_id,
                    cidr=cidr,
                    created_at=mac_range.created_at,
                    first_address=first_address,
                    next_auto_assign_mac=mac_range.next_address,
                    last_address=last_address)
            self.mac_address_ranges.update({mac_range_id: q_range})
            for mac_id, mac in self.mac_addresses.iteritems():
                dealloc = False
                if mac.interface_id not in self.interface_network:
                    LOG.critical("mac.interface_id {} not in interface_network.".
                                 format(mac.interface_id))
                    continue
                    # dealloc = True
                m += 1
                tenant_id = self.interface_tenant[mac.interface_id]
                q_mac = quark.QuarkMacAddress(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        created_at=mac.created_at,
                        mac_address_range_id=mac_range.id,
                        address=mac.address,
                        deallocated=dealloc,
                        deallocated_at=mac.updated_at)
                if mac_range_id not in self.quark_mac_addresses:
                    self.quark_mac_addresses.update({mac_range_id: [q_mac]})
                else:
                    self.quark_mac_addresses[mac_range_id].append(q_mac)
                q_port = self.port_cache[mac.interface_id]
                q_port.mac_address = q_mac.address
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_policies(self):
        print("Migrating policies...")
        m = 0
        octets = self.ip_octets.values()
        offsets = self.ip_ranges.values()
        for policy, policy_block_ids in self.policy_ids.items():
            m += 1
            policy_octets = [o.octet for o in octets if o.policy_id == policy]
            policy_rules = [(off.offset, off.length) for off in offsets
                            if off.policy_id == policy]
            policy_rules = make_offset_lengths(policy_octets, policy_rules)
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
            try:
                policy_description = policy.description
            except Exception:
                policy_description = None
            for block_id in policy_block_ids.keys():
                policy_uuid = policy
                q_network = self.quark_networks[policy_block_ids[block_id]]
                the_name = self.policies[policy].name
                if not policy_description:
                    the_desc = the_name
                q_ip_policy = quark.QuarkIpPolicy(
                        id=policy_uuid,
                        tenant_id=q_network.tenant_id,
                        description=policy_description or the_desc,
                        created_at=min_created_at,
                        name=the_name)
                self.quark_ip_policies.update({policy_uuid: q_ip_policy})
                for rule in policy_rules:
                    outer_cidr = self.ip_blocks[block_id].cidr
                    _cidr = make_cidr(outer_cidr, rule[0], rule[1])
                    if _cidr:
                        q_ip_policy_cidr = quark.QuarkIpPolicyRule(
                                      id=str(uuid4()),
                                      cidr=_cidr,
                                      ip_policy_id=policy_uuid,
                                      created_at=min_created_at)
                        if q_ip_policy.id in self.quark_ip_policy_cidrs.keys():
                            self.quark_ip_policy_cidrs[q_ip_policy.id].append(q_ip_policy_cidr)
                        else:
                            self.quark_ip_policy_cidrs.update({q_ip_policy.id: [q_ip_policy_cidr]})
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def insert_networks(self, cursor, connection):
        print("Inserting networks...")
        m = 0
        query = """
        INSERT 
        INTO quark_networks (
            `id`, 
            `tenant_id`, 
            `created_at`, 
            `name`,
            `ipam_strategy`,
            `network_plugin`) 
        VALUES """
        for record in self.quark_networks.values():
            m += 1
            record = mysqlize(record)
            query += "({0},{1},{2},{3},{4},{5}),\n".format(record.id,
                                                   record.tenant_id,
                                                   record.created_at,
                                                   record.name,
                                                   record.ipam_strategy,
                                                   record.network_plugin)
        query = query.rstrip(',\n')
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m))


    def insert_ports(self, cursor, connection):
        print("Inserting ports...")
        m = 0
        query = """
        INSERT 
        INTO quark_ports (
            `id`,
            `tenant_id`,
            `created_at`,
            `name`,
            `admin_state_up`,
            `network_id`,
            `backend_key`,
            `mac_address`,
            `device_id`,
            `device_owner`,
            `bridge`)
        VALUES """
        all_records = []
        for record in self.port_cache.values():
            record = mysqlize(record)
            m += 1
            all_records.append("({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.created_at,
                    record.name,
                    record.admin_state_up,
                    record.network_id,
                    record.backend_key,
                    record.mac_address,
                    record.device_id,
                    record.device_owner,
                    record.bridge))
        chunks = paginate_query(all_records)
        for i, chunk in enumerate(chunks):
            chunk_query = query + chunk
            chunk_query = chunk_query.rstrip(',\n')
            cursor.execute(chunk_query)
            connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m)) 
   

    def insert_subnets(self, cursor, connection):
        print("Inserting subnets...")
        m = 0
        query = """
        INSERT
        INTO quark_subnets (
            `id`,
            `tenant_id`,
            `created_at`,
            `network_id`,
            `_cidr`,
            `first_ip`,
            `last_ip`,
            `ip_version`,
            `next_auto_assign_ip`,
            `tag_association_uuid`,
            `do_not_use`,
            `name`,
            `ip_policy_id`,
            `enable_dhcp`,
            `segment_id`)
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
        cursor.execute(query.rstrip(',\n'))
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m))


    def insert_ip_addresses(self, cursor, connection):
        print("Inserting ip addresses...")
        m = 0
        query = """
        INSERT
        INTO quark_ip_addresses (
            `id`,
            `address_readable`,
            `address`,
            `used_by_tenant_id`,
            `created_at`,
            `subnet_id`,
            `network_id`,
            `version`,
            `_deallocated`,
            `deallocated_at`,
            `allocated_at`)
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
        for i, chunk in enumerate(chunks):
            chunk_query = query + chunk
            chunk_query = chunk_query.rstrip(',\n')
            cursor.execute(chunk_query)
            connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(
            time.time() - self.start_time, m))


    def insert_port_ip_assn(self, cursor, connection):
        print("Inserting port_ip_address_associations...")
        m = 0
        query_head = """
        INSERT
        INTO quark_port_ip_address_associations (
            `port_id`,
            `ip_address_id`)
        VALUES """
        all_records = []
        for port_id, port in self.port_cache.iteritems():
            for ip in list(port.ip_addresses):
                m += 1
                all_records.append("('{0}',{1}),\n".format(port_id, ip.id))
        query_size = current_stop = 200000
        records_handled = 0
        while records_handled < len(all_records):
            if len(all_records) < current_stop:
                current_stop = len(all_records)
            current_block = "".join(all_records[records_handled:current_stop])
            current_stop += query_size
            cursor.execute(query_head + current_block.rstrip(',\n'))
            connection.commit()
            records_handled += query_size
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
    

    def insert_policies(self, cursor, connection):
        print("Inserting policies...")
        m = 0
        query = """
        INSERT
        INTO quark_ip_policy (
            `id`,
            `name`,
            `tenant_id`,
            `description`,
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
        cursor.execute(query.rstrip(',\n'))
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
   

    def insert_lswitches(self, cursor, connection):
        print("Inserting nvp driver lswitches...")
        m = 0
        query = """
        INSERT 
        INTO quark_nvp_driver_lswitch (
            `id`,
            `nvp_id`,
            `network_id`,
            `display_name`,
            `port_count`,
            `transport_zone`,
            `transport_connector`,
            `segment_id`)
        VALUES """
        port_query = """
        INSERT
        INTO quark_nvp_driver_lswitchport (
            `id`,
            `port_id`,
            `switch_id`,
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
        try:
            cursor.execute(query)
            connection.commit()
            cursor.execute(port_query)
            connection.commit()
        except Exception as e:
            print("\tError inserting nvp ports: {}".format(e))
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))
   

    def insert_mac_addresses(self, cursor, connection):
        print("Inserting mac addressess...")
        m = 0
        all_records = []
        query = """
        INSERT
        INTO quark_mac_addresses (
            `tenant_id`,
            `created_at`,
            `address`,
            `mac_address_range_id`,
            `deallocated`,
            `deallocated_at`)
        VALUES """
        for mac_range_id, macs in self.quark_mac_addresses.iteritems():
            try:
                mac_range = self.mac_address_ranges[mac_range_id]
                # There is only one mac range so this is fine:
                cursor.execute("""
                INSERT
                INTO quark_mac_address_ranges (
                    `id`,
                    `created_at`,
                    `cidr`,
                    `first_address`,
                    `last_address`,
                    `next_auto_assign_mac`)
                VALUES ('{0}','{1}','{2}',{3},{4},{5})""".format(
                    mac_range.id,
                    mac_range.created_at,
                    mac_range.cidr,
                    mac_range.first_address,
                    mac_range.last_address,
                    mac_range.next_auto_assign_mac))
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
        for i, chunk in enumerate(chunks):
            chunk_query = query + chunk
            chunk_query = chunk_query.rstrip(',\n')
            cursor.execute(chunk_query)
            connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def insert_routes(self, cursor, connection):
        print("Inserting routes...")
        query = """
        INSERT
        INTO quark_routes (
            `id`,
            `tenant_id`,
            `created_at`,
            `cidr`,
            `gateway`,
            `subnet_id`,
            `tag_association_uuid`)
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
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_routes)))


    def insert_quark_dns_nameservers(self, cursor, connection):
        print("Inserting dns nameservers...")
        query = """
        INSERT
        INTO quark_dns_nameservers (
            `id`,
            `tenant_id`,
            `created_at`,
            `ip`,
            `subnet_id`,
            `tag_association_uuid`)
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
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_dns_nameservers)))


    def insert_ip_policy_rules(self, cursor, connection):
        print("Inserting ip policy rules...")
        query = """
        INSERT
        INTO quark_ip_policy_cidrs (
            `id`,
            `ip_policy_id`,
            `created_at`,
            `cidr`)
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
        cursor.execute(query)
        connection.commit()
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time,
            len(self.quark_ip_policy_cidrs)))


    def insert_quotas(self, cursor, connection):
        print("Inserting quotas...")
        query = """
        INSERT
        INTO quotas (
            `id`,
            `tenant_id`,
            `limit`,
            `resource`) 
        VALUES """
        for tenant_id, quota in self.quark_quotas.iteritems():
            record = mysqlize(quota)
            query += "({0},{1},{2},{3}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.limit,
                    record.resource)
        query = query.rstrip(',\n')
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
