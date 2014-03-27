import netaddr
import datetime # need the type
import ConfigParser as cfgp
import os
import math
import sys
import logging
import MySQLdb
LOG = logging.getLogger(__name__)

def stringer(obj):
    maxwidth = 27
    retstr = "\n"
    members = [attr for attr in dir(obj)
            if not callable(attr) and not attr.startswith("__")]
    if members:
        for member in members:
            retstr += "{0}: {1}\n".format(member.rjust(maxwidth),
                                          getattr(obj, member))
    return retstr

def handle_null(value):
    if not value or value == 0 or value == "0":
        return False
    return True

def create_schema(dest):
    #from quark.db import models as quarkmodels
    #from sqlalchemy.ext.declarative import declarative_base
    #from sqlalchemy import create_engine
    #from sqlalchemy.orm import sessionmaker
    #username = db_destination['user']
    #password = db_destination['pass']
    #location = db_destination['host']
    #dbname = db_destination['db']
    #engine = create_engine("mysql://{0}:{1}@{2}/{3}".
    #        format(username, password, location, dbname),
    #        echo=True)
    conn = MySQLdb.connect(host = dest['host'],
                           user = dest['user'],
                           passwd = dest['pass'],
                           db = dest['db'])

    cursor = conn.cursor() 
    MYSQL_OPTION_MULTI_STATEMENTS_ON = 0
    MYSQL_OPTION_MULTI_STATEMENTS_OFF = 1

    conn.set_server_option(MYSQL_OPTION_MULTI_STATEMENTS_ON)
    
    schema = open("neutron_schema.sql").read()
    cursor.execute(schema)
    more = True
    while more:
        print cursor.fetchall()
        more = cursor.nextset()
    conn.commit()
    conn.set_server_option(MYSQL_OPTION_MULTI_STATEMENTS_OFF)
    cursor.close()
    conn.close()
    #Base = declarative_base(engine)
    #Session = sessionmaker(bind=engine)
    #session = Session()
    #quarkmodels.BASEV2.metadata.drop_all(engine)
    #quarkmodels.BASEV2.metadata.create_all(engine)

def paginate_query(all_records):
    """return a list of strings less than max_byte_size each for mysql consumption"""
    avg = sum([len(all_records[i]) for i in range(100)])/100
    total_byte_size = avg * len(all_records) #sys.getsizeof(all_records)
    max_byte_size = 20000000
    records = len(all_records)
    avg_record_bytes = total_byte_size / records
    records_per_chunk = int(math.ceil(max_byte_size / avg_record_bytes))
    chunks = []
    start_mark = 0
    end_mark = int(records_per_chunk)
    if end_mark >= records:
        chunks.append("".join(all_records))
    else:
        while start_mark < records:
            if start_mark + records_per_chunk > all_records:
                chunks.append("".join(all_records[start_mark:]))
                start_mark = end_mark
                end_mark += records_per_chunk
            else:
                chunks.append("".join(all_records[start_mark:end_mark]))
                start_mark = end_mark
                end_mark += records_per_chunk
    return chunks

def get_config():
    possible_configs = [os.path.expanduser('~/.oblige_config'),
                        '.oblige_config']
    config = cfgp.RawConfigParser()
    config.read(possible_configs)
    if len(config.sections()) < 1:
        return None
    return config

def escape(astr):
    return astr.replace("'", "\\'")

def mysqlize(some_object):
    members = [attr for attr in dir(some_object)
            if not callable(attr) and not attr.startswith("__")]
    for m in members:
        x = getattr(some_object, m)
        if type(x) is str:
            x = x.replace("'", "\\'")
        elif type(x) is int:
            # doesn't need quotes
            continue
        elif type(x) is datetime.datetime:
            x = x.strftime('%Y-%m-%d %H:%M:%S')
        elif type(x) is bool:
            x = 1 if x else 0
        elif type(x) is set:
            continue
        setattr(some_object, m, "'{}'".format(x) if x else 'NULL')
    return some_object

def _br(target):
    if target[:3] == 'br-':
        return target[3:]
    return target

def translate_netmask(netmask, destination):
    """
    In [64]: a = netaddr.IPAddress("255.240.0.0") # <- netmask
    In [65]: netaddr.IPNetwork("192.168.0.0/%s" %
        (32 - int(math.log(2**32 - a.value, 2))))
    Out[65]: IPNetwork('192.168.0.0/12')
    So if the destination address is 192.168.0.0
    Thats your cidr
    """
    # returns a cidr based on the string arguments
    if not netmask:
        print("No netmask given.")
    if not destination:
        print("No destination given.")
    try:
        a = netaddr.IPAddress(netmask)
        return str(netaddr.IPNetwork("{0}/{1}".format(destination,
            32 - int(math.log(2 ** 32 - a.value, 2)))))  # noqa
    except Exception as e:
        print("Could not generate cidr, netmask {0} destination {1}".
                format(netmask, destination))
        print e

def to_mac_range(val):
    cidr_parts = val.split("/")
    prefix = cidr_parts[0]
    prefix = prefix.replace(':', '')
    prefix = prefix.replace('-', '')
    prefix_length = len(prefix)
    if prefix_length < 6 or prefix_length > 12:
        r = "6>len({0}) || len({0})>12 len == {1}]".format(val, prefix_length)
        raise ValueError(r)
    diff = 12 - len(prefix)
    if len(cidr_parts) > 1:
        mask = int(cidr_parts[1])
    else:
        mask = 48 - diff * 4
    mask_size = 1 << (48 - mask)
    prefix = "%s%s" % (prefix, "0" * diff)
    try:
        cidr = "%s/%s" % (str(netaddr.EUI(prefix)).replace("-", ":"), mask)
    except Exception as e:
        r = "{0} raised netaddr.AddrFormatError: ".format(prefix)
        r += "{0}... ignoring.".format(e.message)
        print(r)
    prefix_int = int(prefix, base=16)
    return cidr, prefix_int, prefix_int + mask_size

def make_offset_lengths(octets, offsets):
    tmp_ranges = list()
    tmp_or = list()
    if offsets:
        for o in offsets:
            tmp_ranges.append(offset_to_range(o))
    if octets:
        tmp_or = list_to_ranges(octets)
        for r in tmp_or:
            tmp_ranges.append(r)
    tmp_all = consolidate_ranges(tmp_ranges)
    return ranges_to_offset_lengths(tmp_all)

def make_cidr(outer_cidr, offset, length):
    #if offset < 0 and length + offset == 4:
        #print("Noob")
    network = netaddr.IPNetwork(outer_cidr)
    first_ip = netaddr.IPAddress(int(network.first) + offset)
    last_ip = netaddr.IPAddress(int(first_ip) + (length - 1))
    cidr = netaddr.iprange_to_cidrs(first_ip, last_ip)
    #if len(cidr) > 1:
        #print("Network: {}".format(network))
        #print("Offset:  {}".format(offset))
        #print("Length:  {}".format(length))
        #print cidr
    # TODO: confirm that offset/lengths like -8192/8196 desire default policies
    #    return None
        #raise Exception
    return str(cidr[0])

def offset_to_range(offset):
    return (offset[0], offset[0] + offset[1])

def list_to_ranges(the_list=None):
    retvals = list()
    all_items = list()
    stack = list()
    for o in the_list:
        all_items.append(o)
    all_items.sort()
    if len(all_items) == 1:
        return [(all_items[0], all_items[0] + 1)]
    stack.append(all_items[0])
    for c, i in enumerate(all_items[1:], start=1):
        if i - 1 == stack[-1]:
            stack.append(i)
        else:
            retvals.append((stack[0], stack[-1] + 1))
            stack = list()
            stack.append(i)
    retvals.append((stack[0], stack[-1] + 1))
    return retvals

def consolidate_ranges(the_ranges):
    if not the_ranges:
        return []
    if the_ranges[0] == 255:
        the_ranges[0] = -1
    if len(the_ranges) < 2:
        return the_ranges
    the_ranges = sorted(the_ranges, key=lambda ran: ran[0])
    retvals = list()
    for r in the_ranges:
        if r[1] - r[0] == 1:
            retvals.append(r[0])
        else:
            for n in range(r[0], r[1]):
                retvals.append(n)
    retvals = set(retvals)
    retvals = list_to_ranges(retvals)
    return retvals

def ranges_to_offset_lengths(ranges):
    retvals = list()
    for r in ranges:
        retvals.append((r[0], r[1] - r[0]))
    return retvals
