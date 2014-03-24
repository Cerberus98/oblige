from utils import stringer


class IpBlock(object):
    def __init__(self, id, network_id, cidr, created_at, _type, tenant_id,
            gateway, dns1, dns2, allocatable_ip_counter, is_full, policy_id,
            parent_id, network_name, omg_do_not_use, max_allocation, updated_at):
        self.id = id
        self.network_id = network_id
        self.cidr = cidr
        self.created_at = created_at
        self._type = _type
        self.tenant_id = tenant_id
        self.gateway = gateway
        self.dns1 = dns1
        self.dns2 = dns2
        self.allocatable_ip_counter = allocatable_ip_counter
        self.is_full = is_full
        self.policy_id = policy_id
        self.parent_id = parent_id
        self.network_name = network_name
        self.omg_do_not_use = omg_do_not_use
        self.max_allocation = max_allocation
        self.updated_at = updated_at

    def __str__(self):
        return stringer(self)

class Interface(object):
    def __init__(self, id, vif_id_on_device, device_id, tenant_id, created_at):
        self.id = id
        self.vif_id_on_device = vif_id_on_device
        self.device_id = device_id
        self.tenant_id = tenant_id
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class IpOctet(object):
    def __init__(self, id, octet, policy_id, created_at):
        self.id = id
        self.octet = octet
        self.policy_id = policy_id
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class IpRange(object):
    def __init__(self, id, offset, length, policy_id, created_at):
        self.id = id
        self.offset = offset
        self.length = length
        self.policy_id = policy_id
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class Policy(object):
    def __init__(self, id, name, tenant_id, description, created_at):
        self.id = id
        self.name = name
        self.tenant_id = tenant_id
        self.description = description
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class IpRoute(object):
    def __init__(self, id, destination, netmask, gateway, source_block_id,
            created_at):
        self.id = id
        self.destination = destination
        self.netmask = netmask
        self.gateway = gateway
        self.source_block_id = source_block_id
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class AllocatableMac(object):
    def __init__(self, id, mac_address_range_id, address, created_at):
        self.id = id
        self.mac_address_range_id = mac_address_range_id
        self.address = address
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class MacAddressRange(object):
    def __init__(self, id, cidr, next_address, created_at):
        self.id = id
        self.cidr = cidr
        self.next_address = next_address
        self.created_at = created_at

    def __str__(self):
        return stringer(self)

class MacAddress(object):
    def __init__(self, id, address, mac_address_range_id, interface_id,
            created_at, updated_at):
        self.id = id
        self.address = address
        self.mac_address_range_id = mac_address_range_id
        self.interface_id = interface_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return stringer(self)

class IpAddress(object):
    def __init__(self, id, address, interface_id, ip_block_id,
            used_by_tenant_id, created_at, marked_for_deallocation,
            deallocated_at, allocated):
        self.id = id
        self.address = address
        self.interface_id = interface_id
        self.ip_block_id = ip_block_id
        self.used_by_tenant_id = used_by_tenant_id
        self.created_at = created_at
        self.marked_for_deallocation = marked_for_deallocation
        self.deallocated_at = deallocated_at
        self.allocated = allocated

    def __str__(self):
        return stringer(self)

