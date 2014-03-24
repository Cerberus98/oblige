from utils import stringer

class QuarkIpAddress(object):
    def __init__(self, id, used_by_tenant_id, created_at, address_readable,
            address, subnet_id, network_id, version, _deallocated,
            deallocated_at, allocated_at):
        self.id = id
        self.used_by_tenant_id = used_by_tenant_id
        self.created_at = created_at
        self.address_readable = address_readable
        self.address = address
        self.subnet_id = subnet_id
        self.network_id = network_id
        self.version = version
        self._deallocated = _deallocated
        self.deallocated_at = deallocated_at
        self.allocated_at = allocated_at  # TODO
    
    def __str__(self):
        return stringer(self)


class QuarkPortIpAddressAssociation(object):
    def __init__(self, port_id, ip_address_id):
        self.port_id = port_id
        self.ip_address_id = ip_address_id

    def __str__(self):
        return stringer(self)

class QuarkPort(object):
    def __init__(self, id, name, tenant_id, created_at, network_id, mac_address,
            device_id, backend_key, device_owner, bridge):
        self.id = id
        self.name = name
        self.admin_state_up = False
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.network_id = network_id
        self.mac_address = mac_address
        self.backend_key = backend_key
        self.device_id = device_id
        self.device_owner = device_owner
        self.ip_addresses = []
        self.bridge = bridge

    def __str__(self):
        return stringer(self)

class QuarkMacAddress(object):
    def __init__(self, id, tenant_id, created_at, address, mac_address_range_id,
            deallocated, deallocated_at):
        self.id = id
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.address = address
        self.mac_address_range_id = mac_address_range_id  # TODO: just range in the ERD
        self.deallocated = deallocated
        self.deallocated_at = deallocated_at

    def __str__(self):
        return stringer(self)

class QuarkMacAddressRange(object):
    def __init__(self, id, created_at, cidr, first_address, last_address,
            next_auto_assign_mac):
        self.id = id
        self.created_at = created_at
        self.cidr = cidr
        self.first_address = first_address
        self.last_address = last_address
        self.next_auto_assign_mac = next_auto_assign_mac

    def __str__(self):
        return stringer(self)

class QuarkTag(object):
    def __init__(self, id, tenant_id, created_at, association_uuid, tag):
        self.id = id
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.association_uuid = association_uuid
        self.tag = tag

    def __str__(self):
        return stringer(self)

class QuarkNetwork(object):
    def __init__(self, id, tenant_id, created_at, name,
            network_plugin, ipam_strategy):
        self.id = id
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.name = name
        self.network_plugin = network_plugin
        self.ipam_strategy = ipam_strategy

    def __str__(self):
        return stringer(self)

class QuarkTagAssociation(object):
    def __init__(self, id, created_at, discriminator):
        self.id = id
        self.created_at = created_at
        self.discriminator = discriminator

    def __str__(self):
        return stringer(self)

class QuarkSubnet(object):
    def __init__(self, id, tenant_id, created_at, network_id, _cidr, first_ip,
            last_ip, ip_version, next_auto_assign_ip, tag_association_uuid,
            do_not_use, name, ip_policy_id):
        self.id = id
        self.name = name
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.network_id = network_id
        self._cidr = _cidr
        self.ip_policy_id = ip_policy_id
        self.first_ip = first_ip
        self.last_ip = last_ip
        self.ip_version = ip_version  # we need this?
        self.next_auto_assign_ip = next_auto_assign_ip
        self.tag_association_uuid = tag_association_uuid
        self.do_not_use = do_not_use
        self.enable_dhcp = False  # TODO
        self.segment_id = tenant_id

    def __str__(self):
        return stringer(self)


class QuarkQuota(object):
    def __init__(self, id, tenant_id, limit=65, resource='ports_per_network'):
        self.id = id
        self.tenant_id = tenant_id
        self.limit = limit
        self.resource = resource

    def __str__(self):
        return stringer(self)


class QuarkDnsNameserver(object):
    def __init__(self, id, ip, subnet_id, created_at, tenant_id):
        self.id = id
        self.ip = ip
        self.subnet_id = subnet_id
        self.created_at = created_at  # TODO: Not in ERD
        self.tenant_id = tenant_id  # TODO: Not in ERD
        self.tag_association_uuid = None

    def __str__(self):
        return stringer(self)

class QuarkNvpDriverLswitch(object):
    def __init__(self, id, nvp_id, network_id, display_name, port_count,
            transport_zone, transport_connector, segment_id, segment_connector):
        self.id = id
        self.nvp_id = nvp_id
        self.network_id = network_id
        self.display_name = display_name
        self.port_count = port_count
        self.transport_zone = transport_zone
        self.transport_connector = transport_connector
        self.segment_id = segment_id
        self.segment_connector = segment_connector

    def __str__(self):
        return stringer(self)

class QuarkNvpDriverLswitchPort(object):
    def __init__(self, port_id, switch_id, created_at):
        self.port_id = port_id
        self.switch_id = switch_id
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class QuarkRoute(object):
    def __init__(self, id, tenant_id, created_at, cidr, gateway, subnet_id,
            tag_association_uuid):
        self.id = id
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.cidr = cidr
        self.gateway = gateway
        self.subnet_id = subnet_id
        self.tag_association_uuid = tag_association_uuid

    def __str__(self):
        return stringer(self)

class QuarkIpPolicy(object):
    def __init__(self, id, tenant_id, created_at, name, description):
        self.id = id
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.name = name
        self.description = description

    def __str__(self):
        return stringer(self)

class QuarkIpPolicyRule(object):
    def __init__(self, id, ip_policy_id, created_at, cidr):
        self.id = id
        self.ip_policy_id = ip_policy_id
        self.created_at = created_at
        self.cidr = cidr

    def __str__(self):
        return stringer(self)

