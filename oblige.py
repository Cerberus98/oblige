import re
import sys
import MySQLdb
import time
import melange
import netaddr
import quark

from datetime import datetime, timedelta
from uuid import uuid4

from utils import _br  # removes leading 'br-'s
from utils import translate_netmask
from utils import to_mac_range
from utils import make_offset_lengths
from utils import mysqlize

class Oblige(object):
    def __init__(self):
        self.start_time = time.time()
        self.debug = False
                
        conn = MySQLdb.connect(host = "localhost",
                               user = "root",
                               passwd = "password",
                               db = "melange")
        cursor = conn.cursor()
        if self.debug:
            cursor.execute("describe interfaces")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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

        if self.debug:
            cursor.execute("describe ip_addresses")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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
                marked_for_deallocation = ip[7],
                deallocated_at = ip[8],
                allocated = ip[9])})
        print("Got {} ip_addresses...".format(len(self.ip_addresses)))

        if self.debug:
            cursor.execute("describe mac_addresses")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
        cursor.execute("select * from mac_addresses")
        self.mac_addresses = {} 
        macaddrs = cursor.fetchall()
        for mac in macaddrs:
            self.mac_addresses.update({mac[0]: melange.MacAddress(
                id = mac[0],
                address = mac[1],
                mac_address_range_id = mac[2],
                interface_id = mac[3],
                created_at = mac[4])})
            self.interfaces[mac[3]].mac_address = mac[1]
        print("Got {} mac_addresses...".format(len(self.mac_addresses)))

        if self.debug:
            cursor.execute("describe mac_address_ranges")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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

        if self.debug:
            cursor.execute("describe allocatable_macs")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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

        if self.debug:
            cursor.execute("describe ip_blocks")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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
                is_full=ip_block[11],
                policy_id=ip_block[12],
                parent_id=ip_block[13],
                network_name=ip_block[14],
                omg_do_not_use=ip_block[15],
                max_allocation=ip_block[16])})
        print("Got {} ip_blocks...".format(len(self.ip_blocks)))

        if self.debug:
            cursor.execute("describe ip_routes")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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

        if self.debug:
            cursor.execute("describe policies")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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

        if self.debug:
            cursor.execute("describe ip_octets")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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

        if self.debug:
            cursor.execute("describe ip_ranges")
            desc = cursor.fetchall()
            for i, v in enumerate(desc):
                print("{}: {}".format(i, v[0]))
                print
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
        self.quark_ip_policy_rules = {}
        self.quark_nvp_stuff = {}  # lswitch: port
        
        # self.quark_nvp_driver_lswitches = {}
        # self.quark_nvp_driver_lswitchports = {}

        self.policy_ids = {}
        self.interface_network = {}
        self.interface_ip = {}
        self.port_cache = {}
        self.interface_tenant = {}

        print("\tInitialization complete in {:.2f} seconds.".format(
            time.time() - self.start_time))
        
        quark_conn = MySQLdb.connect(host = "localhost",
                                     user = "root",
                                     passwd = "password")
        print("Initializing quark cursor")
        quark_cursor = quark_conn.cursor()
        print("Dropping quark")
        quark_cursor.execute("drop database if exists quark")
        print("Creating quark")
        quark_cursor.execute("create database quark")
        print("Using quark")
        quark_cursor.execute("use quark")
        print("Creating quark schema")
        quark_schema = open("__schema__.sql").read()
        quark_cursor.execute(quark_schema)
        quark_cursor.close()
        quark_conn.close()
        

    def migrate_networks(self):
        print("Migrating networks...")
        networks = {}
        m = 0
        for block_id, block in self.ip_blocks.iteritems():
            if _br(block.network_id) not in networks:
                networks[_br(block.network_id)] = {
                        "tenant_id": block.tenant_id,
                        "name": block.network_name,
                        "max_allocation": block.max_allocation,
                        "created_at": block.created_at}
            elif _br(block.network_id) in networks:
                if networks[_br(block.network_id)]["created_at"] > block.created_at:
                    networks[_br(block.network_id)]["created_at"] = block.created_at
            #else:  # how was this ever firing?
            #    print("Bad: {} != {}".format(networks[_br(block.network_id)]["tenant_id"],
            #        block.tenant_id))
        for net_id, net in networks.iteritems():
            cache_net = networks[net_id]
            q_network = quark.QuarkNetwork(id=net_id,
                    tenant_id=cache_net["tenant_id"],
                    name=cache_net["name"],
                    max_allocation=cache_net["max_allocation"],
                    created_at=networks[_br(net_id)]["created_at"])
            self.quark_networks[q_network.id] = q_network
            m += 1
        for block_id, block in self.ip_blocks.iteritems():
            self.quark_subnets.update({block.id: quark.QuarkSubnet(
                    id=block.id,
                    name=block.network_name,
                    tenant_id=block.tenant_id,
                    created_at=block.created_at,
                    network_id=_br(block.network_id),
                    _cidr=block.cidr,
                    first_ip=None,  # get with netaddr (bigint) TODO
                    last_ip=None,
                    ip_version=None,  # netaddr int TODO
                    ip_policy_id=block.policy_id,
                    next_auto_assign_ip=None,  # TODO need to get this
                    tag_association_uuid=None,  # These aren't used
                    do_not_use=block.omg_do_not_use)})
            if block.dns1: 
                self.quark_dns_nameservers.update({block.id: quark.QuarkDnsNameserver(
                    ip=int(netaddr.IPAddress(block.dns1)),
                    created_at=block.created_at,
                    tenant_id=block.tenant_id,
                    subnet_id=block.id)})
            if block.dns2:
                self.quark_dns_nameservers.update({block.id: quark.QuarkDnsNameserver(
                    ip=int(netaddr.IPAddress(block.dns2)),
                    created_at=block.created_at,
                    tenant_id=block.tenant_id,
                    subnet_id=block.id)})
            # self.migrate_ips(block)
            self.migrate_routes(block)
            if block.policy_id:
                if block.policy_id not in self.policy_ids.keys():
                    self.policy_ids[block.policy_id] = {}
                self.policy_ids[block.policy_id][block.id] = _br(block.network_id)
            else:
                # print("Block lacks policy: {}".format(block.id))
                pass
        # add routes:
        for block in self.ip_blocks.values():
            if block.gateway:
                self.migrate_new_routes(block)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_routes(self, block):
        for route_id, route in self.ip_routes.iteritems():
            if route_id == block.id:
                self.quark_routes.update({route_id: quark.QuarkRoute(
                    id = route_id,
                    cidr=translate_netmask(route.netmask, route.destination),
                    tenant_id=block.tenant_id,
                    gateway=route.gateway,
                    created_at=block.created_at,
                    subnet_id=block_id)})
    

    def migrate_new_routes(self, block):
        gateway = netaddr.IPAddress(block.gateway)
        destination = None
        if gateway.version == 4:
            destination = '0.0.0.0/0'
        else:  # TODO not all of these will look like this RE: dobby
            destination = '0:0:0:0:0:0:0:0/0'
        self.quark_routes.update({block.id: quark.QuarkRoute(
            id=None,  # TODO: how do we insert this without stepping on others?
            tag_association_uuid=None,  # TODO: check this
            cidr=destination,
            tenant_id=block.tenant_id,
            gateway=block.gateway,
            subnet_id=block.id,
            created_at=datetime.utcnow())})


    def migrate_ips(self):  # , block):
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
        #for block_id, block in self.ip_blocks.iteritems():
            #for address in [x for x in self.ip_addresses.values()
                    #if x.ip_block_id == block_id]:
                m += 1
                """Populate interface_network cache"""
                interface = address.interface_id
                if interface is not None and\
                        interface not in self.interface_network:
                    self.interface_network[interface] = _br(block.network_id)
                if interface in self.interface_network and\
                        self.interface_network[interface] != _br(block.network_id):
                    pass  # TODO this?
                    #print("Found interface with different "
                    #               "network id: {0} != {1}"
                    #               .format(self.interface_network[interface],
                    #                       _br(block.network_id)))
                deallocated = False
                deallocated_at = None
                # If marked for deallocation
                #       put it into the quark ip table as deallocated
                if address.marked_for_deallocation == 1:
                    deallocated = True
                    deallocated_at = address.deallocated_at
                ip_address = netaddr.IPAddress(address.address)
                q_ip =  quark.QuarkIpAddress(
                        id=address.id,
                        created_at=address.created_at,
                        used_by_tenant_id=address.used_by_tenant_id,
                        network_id=_br(block.network_id),
                        subnet_id=block.id,
                        version=ip_address.version,
                        address_readable=address.address,
                        deallocated_at=deallocated_at,
                        _deallocated=deallocated,
                        address=int(ip_address.ipv6()),
                        allocated_at=block.updated_at)
                self.quark_ip_addresses.update({address.id: q_ip})
                # Populate interface_ip cache
                if interface not in self.interface_ip:
                    self.interface_ip[interface] = set()
                self.interface_ip[interface].add(q_ip)
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def migrate_interfaces(self):
        print("Migrating interfaces...")
        m = 0
        n = 0
        for interface_id, interface in self.interfaces.iteritems():
            if interface_id not in self.interface_network:
                # print("No network for {}".format(interface_id))
                n += 1
                continue
            m += 1
            network_id = self.interface_network[interface_id]
            self.interface_tenant[interface_id] = interface.tenant_id
            port_id = interface.vif_id_on_device
            if not port_id:
                port_id = "TODO"  # TODO don't know how to get on my level son
            q_port = quark.QuarkPort(
                    id=interface_id,
                    name=None,
                    device_id=interface.device_id,
                    tenant_id=interface.tenant_id,
                    created_at=interface.created_at,
                    backend_key=port_id,
                    network_id=network_id,
                    mac_address=interface.mac_address,
                    bridge=None, # TODO needed for pub/snet and depend on env
                    device_owner=None)  # TODO
            lswitch_id = str(uuid4())
            q_nvp_switch = quark.QuarkNvpDriverLswitch(
                    id=lswitch_id,
                    nvp_id=network_id,
                    network_id=network_id, # TODO: axe justin probby okay
                    display_name=network_id,
                    port_count=None,
                    transport_zone=None,
                    transport_connector=None,
                    segment_id=None,
                    segment_connector=None)
            q_nvp_port = quark.QuarkNvpDriverLswitchPort(
                    port_id=port_id,
                    switch_id=lswitch_id)
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
                    #print("mac.interface_id {} not in interface_network.".
                    #        format(mac.interface_id))
                    continue # TODO come back to this
                    # dealloc = True
                m += 1
                tenant_id = self.interface_tenant[mac.interface_id]
                q_mac = quark.QuarkMacAddress(
                        id=None,
                        tenant_id=tenant_id,
                        created_at=mac.created_at,
                        mac_address_range_id=mac_range.id,
                        address=mac.address,
                        deallocated=dealloc,  # TODO
                        deallocated_at=None)  # TODO
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
                policy_description = policy.description # TODO fix name/desc
            except Exception:
                policy_description = None
            for block_id in policy_block_ids.keys():
                policy_uuid = policy
                q_network = self.quark_networks[policy_block_ids[block_id]]
                q_ip_policy = quark.QuarkIpPolicy(
                        id=policy_uuid,
                        tenant_id=q_network.tenant_id,
                        description=policy_description,
                        created_at=min_created_at,
                        name=self.policies[policy].name)  # TODO
                self.quark_ip_policies.update({policy_uuid: q_ip_policy})
                # q_ip_policy.subnets.append(self.quark_subnets[block_id])
                for rule in policy_rules:
                    q_ip_policy_rule = quark.QuarkIpPolicyRule(
                                      id=str(uuid4()),
                                      offset=rule[0],
                                      length=rule[1],
                                      ip_policy_id=policy_uuid,
                                      created_at=min_created_at)
                    self.quark_ip_policy_rules.update({q_ip_policy.id: q_ip_policy_rule})
        print("\tDone, {:.2f} sec, {} migrated.".format(time.time() - self.start_time, m))


    def insert_networks(self, cursor):
        print("Inserting networks...")
        query = """
        INSERT 
        INTO quark_networks (
            `id`, 
            `tenant_id`, 
            `created_at`, 
            `name`,
            `ipam_strategy`,
            `max_allocation`) 
        VALUES """
        #  TODO TODO
        # if network is public or snet -> network_plugin == UNMANAGED
        # else network_plugin == NVP
        for record in self.quark_networks.values():
            record = mysqlize(record)
            query += "({0},{1},{2},{3},'{4}',{5}),\n".format(record.id,
                                                   record.tenant_id,
                                                   record.created_at,
                                                   record.name,
                                                   'ANY',
                                                   record.max_allocation)
        query = query.rstrip(',\n')
        with open('quark_networks.sql', 'w') as f:
            f.write(query)
        
        cursor.execute(query)
        print("\tDone, {:.2f} sec, sizeof {}, len {}".format(
            time.time() - self.start_time, sys.getsizeof(query), len(query)))


    def insert_ports(self, cursor):
        print("Inserting ports...")
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
        for record in self.port_cache.values():
            record = mysqlize(record)
            query += "({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}),\n".format(
                    record.id,
                    record.tenant_id,
                    record.created_at,
                    record.name,
                    record.admin_state_up,
                    record.network_id,
                    record.backend_key, # TODO shouldnt be TODO
                    record.mac_address,
                    record.device_id,
                    record.device_owner,
                    record.bridge) # TODO come back to this
        query = query.rstrip(',\n')
        with open('quark_ports.sql', 'w') as f:
            f.write(query)
        cursor.execute(query)
        print("\tDone, {:.2f} sec, sizeof {}, len {}".format(
            time.time() - self.start_time, sys.getsizeof(query), len(query))) 
   

    def insert_subnets(self, cursor):
        print("Inserting subnets...")
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
        with open("quark_subnets.sql", 'w') as f:
            f.write(query)
        cursor.execute(query.rstrip(',\n'))
        print("\tDone, {:.2f} sec".format(
            time.time() - self.start_time))


    def insert_ip_addresses(self, cursor):
        print("Inserting ip addresses...")
        # this giant query needs to be broken down into bite-sized chunks
        # make a list of the strings for insertion then send them off

        #cursor.execute("SET foreign_key_checks = 0")
        query_head = """
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
        query_size = current_stop = 50000
        records_handled = 0
        n = 0
        while records_handled < len(all_records):
            if len(all_records) < current_stop:
                current_stop = len(all_records)
            current_block = "".join(all_records[records_handled:current_stop])
            current_stop += query_size
            n += 1
            with open('quark_ip_addresses_{}.sql'.format(n), 'w') as f:
                f.write(query_head + current_block.rstrip(',\n'))
            cursor.execute(query_head + current_block.rstrip(',\n'))
            records_handled += query_size
        #cursor.execute("SET foreign_key_checks = 1")
        print("\tDone, {:.2f} sec".format(time.time() - self.start_time))


    def insert_port_ip_assn(self, cursor):
        print("Inserting port_ip_address_associations...")
        query_head = """
        INSERT
        INTO quark_port_ip_address_associations (
            `port_id`,
            `ip_address_id`)
        VALUES """
        all_records = []
        # for port_id in self.port_cache:
        #    self.port_cache[port_id].ip_addresses = self.interface_ip[port_id]
        
        for port_id, port in self.port_cache.iteritems():
            #if type(port.ip_addresses) is not list:
                # print port.ip_addresses
            for ip in list(port.ip_addresses):
                all_records.append("('{0}',{1}),\n".format(port_id, ip.id))
        query_size = current_stop = 200000
        records_handled = 0
        while records_handled < len(all_records):
            if len(all_records) < current_stop:
                current_stop = len(all_records)
            current_block = "".join(all_records[records_handled:current_stop])
            # print records_handled
            with open('quark_port_ip_assn.sql', 'w') as f:
                f.write(query_head + current_block.rstrip(',\n'))
            current_stop += query_size
            cursor.execute(query_head + current_block.rstrip(',\n'))
            records_handled += query_size
        print("\tDone, {:.2f} sec, {} records".format(time.time() - self.start_time,
            records_handled))
    

    def insert_policies(self, cursor):
        print("Inserting policies...")
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
            record = mysqlize(record)
            query += "({0},{1},{2},{3},{4}),\n".format(
                    record.id,
                    record.name,
                    record.tenant_id,
                    record.description,
                    record.created_at)
        with open('quark_ip_policies.sql', 'w') as f:
            f.write(query.rstrip(',\n'))
        cursor.execute(query.rstrip(',\n'))
        print("\tDone, {:.2f} sec".format(time.time() - self.start_time))
   

    def insert_lswitches(self, cursor):
        print("Inserting nvp driver lswitches...")
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
            `port_id`,
            `switch_id`)
        VALUES """

        for switch, ports in self.quark_nvp_stuff.iteritems():
            switch = mysqlize(switch)
            query += "({0},{1},{2},{3},{4},{5},{6},{7}),\n".format(
                    switch.id,  # duplicate key error
                    switch.nvp_id,
                    switch.network_id,
                    switch.display_name,
                    switch.port_count,
                    switch.transport_zone,  # TODO: isolated nets not NULL
                    switch.transport_connector,
                    switch.segment_connector,
                    switch.segment_id) # TODO: created_at add
            for port in ports:
                port = mysqlize(port)
                port_query += "({0},{1}),\n".format(port.port_id, switch.id)
        query = query.rstrip(',\n')
        port_query = port_query.rstrip(',\n')
        with open("quark_nvp_lswitch.sql", "w") as f:
            f.write(query)
        with open("quark_nvp_ports.sql", "w") as f:
            f.write(port_query)
        cursor.execute(query)
        try:
            cursor.execute(port_query)
        except Exception as e:
            print("\tError inserting nvp ports: {}".format(e))
        print("\tDone, {:.2f} sec".format(time.time() - self.start_time))
   

    def insert_mac_addresses(self, cursor):
        print("Inserting mac addressess...")
        query = """
        INSERT
        INTO quark_mac_addresses (
            `tenant_id`,
            `created_at`,
            `address`,
            `mac_address_range_id`,
            `deallocated`,
            `deallocated_at`)
        VALUES """  # TODO: make sure that NULL is okay for deallocated
        # self.quark_macs.update({mac_range_id: [q_mac]})
        for mac_range_id, macs in self.quark_mac_addresses.iteritems():
            # insert the mac_address_range TODO
            cursor.execute("""
            INSERT
            INTO
            quark_mac_address_ranges (
                `id`,
                `created_at`,
                `cidr`,
                `first_address`,
                `last_address`,
                `next_auto_assign_mac`)
            VALUES ('{0}',{1},'{2}','{3}','{4}','{5}')""".format(
                mac_range_id,
                'NULL',
                1,
                1,  # TODO: fill these in
                1,
                1))
            for mac in macs:
                mac = mysqlize(mac)
                query += "({0},{1},{2},{3},{4},{5}),\n".format(
                        mac.tenant_id,
                        mac.created_at,
                        mac.address,
                        mac.mac_address_range_id,
                        mac.deallocated,
                        mac.deallocated_at)
        query = query.rstrip(',\n')
        cursor.execute(query)

        print("\tDone, {:.2f} sec".format(time.time() - self.start_time))


    def insert_mac_address_ranges(self, cursor):
        print("Inserting mac address ranges... \tTODO")
        query = """
        INSERT
        INTO quark_mac_addresses_ranges (
            `id`,
            `created_at`,
            `cidr`,
            `first_address`,
            `last_address`,
            `next_auto_assign_max`)
        VALUES """
        # for record in ... TODO
        #
        print("\tDone, {:.2f} sec".format(time.time() - self.start_time))

    def migrates(self):
        self.migrate_networks()
        self.migrate_ips()
        self.migrate_interfaces()
        self.associate_ips_with_ports()
        self.migrate_macs()
        self.migrate_policies()


    def inserts(self):
        conn = MySQLdb.connect(host = "localhost",
                           user = "root",
                           passwd = "Br_-00jWp2McAf--@",
                           db = "quark")
        conn.autocommit(True)
        cursor = conn.cursor()
        # these have to be in this order or the key constriants fail
        self.insert_networks(cursor)
        self.insert_ports(cursor)
        self.insert_policies(cursor)
        self.insert_subnets(cursor)
        self.insert_ip_addresses(cursor)
        self.insert_port_ip_assn(cursor)
        self.insert_lswitches(cursor)
        # self.insert_lswitch_ports(cursor)
        self.insert_mac_addresses(cursor)
        # self.insert_mac_address_ranges(cursor)
        cursor.close()
        conn.close()

# TODO: null data validator

if __name__ == "__main__":
    o = Oblige()
    o.migrates()
    o.inserts()
    print("TOTAL TIME: {}".format(timedelta(seconds=time.time()-o.start_time)))
