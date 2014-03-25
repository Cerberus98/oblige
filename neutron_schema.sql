/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `dnsnameservers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dnsnameservers` ( `address` varchar(128) NOT NULL,`subnet_id` varchar(36) NOT NULL, PRIMARY KEY (`address`,`subnet_id`), KEY `subnet_id` (`subnet_id`), CONSTRAINT `dnsnameservers_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `ipallocationpools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ipallocationpools` (
  `id` varchar(36) NOT NULL,
  `subnet_id` varchar(36) DEFAULT NULL,
  `first_ip` varchar(64) NOT NULL,
  `last_ip` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet_id` (`subnet_id`),
  CONSTRAINT `ipallocationpools_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ipallocations`
--

DROP TABLE IF EXISTS `ipallocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ipallocations` (
  `port_id` varchar(36) DEFAULT NULL,
  `ip_address` varchar(64) NOT NULL,
  `subnet_id` varchar(36) NOT NULL,
  `network_id` varchar(36) NOT NULL,
  PRIMARY KEY (`ip_address`,`subnet_id`,`network_id`),
  KEY `port_id` (`port_id`),
  KEY `subnet_id` (`subnet_id`),
  KEY `network_id` (`network_id`),
  CONSTRAINT `ipallocations_ibfk_1` FOREIGN KEY (`port_id`) REFERENCES `ports` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ipallocations_ibfk_2` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ipallocations_ibfk_3` FOREIGN KEY (`network_id`) REFERENCES `networks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ipavailabilityranges`
--

DROP TABLE IF EXISTS `ipavailabilityranges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ipavailabilityranges` (
  `allocation_pool_id` varchar(36) NOT NULL,
  `first_ip` varchar(64) NOT NULL,
  `last_ip` varchar(64) NOT NULL,
  PRIMARY KEY (`allocation_pool_id`,`first_ip`,`last_ip`),
  CONSTRAINT `ipavailabilityranges_ibfk_1` FOREIGN KEY (`allocation_pool_id`) REFERENCES `ipallocationpools` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `networks`
--

DROP TABLE IF EXISTS `networks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `networks` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `status` varchar(16) DEFAULT NULL,
  `admin_state_up` tinyint(1) DEFAULT NULL,
  `shared` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ports`
--

DROP TABLE IF EXISTS `ports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ports` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `network_id` varchar(36) NOT NULL,
  `mac_address` varchar(32) NOT NULL,
  `admin_state_up` tinyint(1) NOT NULL,
  `status` varchar(16) NOT NULL,
  `device_id` varchar(255) NOT NULL,
  `device_owner` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `network_id` (`network_id`),
  CONSTRAINT `ports_ibfk_1` FOREIGN KEY (`network_id`) REFERENCES `networks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_dns_nameservers`
--

DROP TABLE IF EXISTS `quark_dns_nameservers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_dns_nameservers` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `ip` char(39) DEFAULT NULL,
  `subnet_id` varchar(36) DEFAULT NULL,
  `tag_association_uuid` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet_id` (`subnet_id`),
  KEY `tag_association_uuid` (`tag_association_uuid`),
  CONSTRAINT `quark_dns_nameservers_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `quark_subnets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `quark_dns_nameservers_ibfk_2` FOREIGN KEY (`tag_association_uuid`) REFERENCES `quark_tag_associations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_ip_addresses`
--

DROP TABLE IF EXISTS `quark_ip_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_ip_addresses` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `address_readable` varchar(128) NOT NULL,
  `address` char(39) NOT NULL,
  `subnet_id` varchar(36) DEFAULT NULL,
  `network_id` varchar(36) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `allocated_at` datetime DEFAULT NULL,
  `_deallocated` tinyint(1) DEFAULT NULL,
  `used_by_tenant_id` varchar(255) DEFAULT NULL,
  `deallocated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subnet_id` (`subnet_id`,`address`),
  KEY `network_id` (`network_id`),
  KEY `ix_quark_ip_addresses_address` (`address`),
  KEY `ix_quark_ip_addresses_version` (`version`),
  KEY `ix_quark_ip_addresses_deallocated_at` (`deallocated_at`),
  CONSTRAINT `quark_ip_addresses_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `quark_subnets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `quark_ip_addresses_ibfk_2` FOREIGN KEY (`network_id`) REFERENCES `quark_networks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_ip_policy`
--

DROP TABLE IF EXISTS `quark_ip_policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_ip_policy` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_ip_policy_cidrs`
--

DROP TABLE IF EXISTS `quark_ip_policy_cidrs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_ip_policy_cidrs` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `ip_policy_id` varchar(36) DEFAULT NULL,
  `cidr` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_policy_id` (`ip_policy_id`),
  CONSTRAINT `quark_ip_policy_cidrs_ibfk_1` FOREIGN KEY (`ip_policy_id`) REFERENCES `quark_ip_policy` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_mac_address_ranges`
--

DROP TABLE IF EXISTS `quark_mac_address_ranges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_mac_address_ranges` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `cidr` varchar(255) NOT NULL,
  `first_address` bigint(20) NOT NULL,
  `last_address` bigint(20) NOT NULL,
  `next_auto_assign_mac` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_mac_addresses`
--

DROP TABLE IF EXISTS `quark_mac_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_mac_addresses` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `address` bigint(20) NOT NULL AUTO_INCREMENT,
  `mac_address_range_id` varchar(36) NOT NULL,
  `deallocated` tinyint(1) DEFAULT NULL,
  `deallocated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`address`),
  KEY `mac_address_range_id` (`mac_address_range_id`),
  KEY `ix_quark_mac_addresses_deallocated_at` (`deallocated_at`),
  CONSTRAINT `quark_mac_addresses_ibfk_1` FOREIGN KEY (`mac_address_range_id`) REFERENCES `quark_mac_address_ranges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=187723572703011 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_networks`
--

DROP TABLE IF EXISTS `quark_networks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_networks` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `ip_policy_id` varchar(36) DEFAULT NULL,
  `network_plugin` varchar(36) DEFAULT NULL,
  `ipam_strategy` varchar(255) DEFAULT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_policy_id` (`ip_policy_id`),
  KEY `ix_quark_networks_tenant_id` (`tenant_id`),
  CONSTRAINT `quark_networks_ibfk_1` FOREIGN KEY (`ip_policy_id`) REFERENCES `quark_ip_policy` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_nvp_driver_lswitch`
--

DROP TABLE IF EXISTS `quark_nvp_driver_lswitch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_nvp_driver_lswitch` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `nvp_id` varchar(36) NOT NULL,
  `network_id` varchar(36) NOT NULL,
  `display_name` varchar(255) DEFAULT NULL,
  `port_count` int(11) DEFAULT NULL,
  `transport_zone` varchar(36) DEFAULT NULL,
  `transport_connector` varchar(20) DEFAULT NULL,
  `segment_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_quark_nvp_driver_lswitch_nvp_id` (`nvp_id`),
  KEY `ix_quark_nvp_driver_lswitch_network_id` (`network_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_nvp_driver_lswitchport`
--

DROP TABLE IF EXISTS `quark_nvp_driver_lswitchport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_nvp_driver_lswitchport` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `port_id` varchar(36) NOT NULL,
  `switch_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `switch_id` (`switch_id`),
  KEY `ix_quark_nvp_driver_lswitchport_port_id` (`port_id`),
  CONSTRAINT `quark_nvp_driver_lswitchport_ibfk_1` FOREIGN KEY (`switch_id`) REFERENCES `quark_nvp_driver_lswitch` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_nvp_driver_qos`
--

DROP TABLE IF EXISTS `quark_nvp_driver_qos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_nvp_driver_qos` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `display_name` varchar(255) NOT NULL,
  `max_bandwidth_rate` int(11) NOT NULL,
  `min_bandwidth_rate` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_nvp_driver_security_profile`
--

DROP TABLE IF EXISTS `quark_nvp_driver_security_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_nvp_driver_security_profile` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `nvp_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_quark_nvp_driver_security_profile_nvp_id` (`nvp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_port_ip_address_associations`
--

DROP TABLE IF EXISTS `quark_port_ip_address_associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_port_ip_address_associations` (
  `port_id` varchar(36) DEFAULT NULL,
  `ip_address_id` varchar(36) DEFAULT NULL,
  KEY `port_id` (`port_id`),
  KEY `ip_address_id` (`ip_address_id`),
  CONSTRAINT `quark_port_ip_address_associations_ibfk_1` FOREIGN KEY (`port_id`) REFERENCES `quark_ports` (`id`),
  CONSTRAINT `quark_port_ip_address_associations_ibfk_2` FOREIGN KEY (`ip_address_id`) REFERENCES `quark_ip_addresses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_port_security_group_associations`
--

DROP TABLE IF EXISTS `quark_port_security_group_associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_port_security_group_associations` (
  `port_id` varchar(36) DEFAULT NULL,
  `group_id` varchar(36) DEFAULT NULL,
  KEY `port_id` (`port_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `quark_port_security_group_associations_ibfk_1` FOREIGN KEY (`port_id`) REFERENCES `quark_ports` (`id`),
  CONSTRAINT `quark_port_security_group_associations_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `quark_security_groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_ports`
--

DROP TABLE IF EXISTS `quark_ports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_ports` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `admin_state_up` tinyint(1) DEFAULT NULL,
  `network_id` varchar(36) NOT NULL,
  `backend_key` varchar(36) NOT NULL,
  `mac_address` bigint(20) DEFAULT NULL,
  `device_id` varchar(255) NOT NULL,
  `device_owner` varchar(255) DEFAULT NULL,
  `bridge` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `network_id` (`network_id`),
  KEY `ix_quark_ports_name` (`name`),
  KEY `ix_quark_ports_device_id` (`device_id`),
  KEY `idx_ports_3` (`tenant_id`),
  KEY `idx_ports_1` (`device_id`,`tenant_id`),
  KEY `idx_ports_2` (`device_owner`,`network_id`),
  CONSTRAINT `quark_ports_ibfk_1` FOREIGN KEY (`network_id`) REFERENCES `quark_networks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_routes`
--

DROP TABLE IF EXISTS `quark_routes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_routes` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `cidr` varchar(64) DEFAULT NULL,
  `gateway` varchar(64) DEFAULT NULL,
  `subnet_id` varchar(36) DEFAULT NULL,
  `tag_association_uuid` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet_id` (`subnet_id`),
  KEY `tag_association_uuid` (`tag_association_uuid`),
  CONSTRAINT `quark_routes_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `quark_subnets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `quark_routes_ibfk_2` FOREIGN KEY (`tag_association_uuid`) REFERENCES `quark_tag_associations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_security_group_rule`
--

DROP TABLE IF EXISTS `quark_security_group_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_security_group_rule` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `group_id` varchar(36) NOT NULL,
  `direction` varchar(10) NOT NULL,
  `ethertype` varchar(4) NOT NULL,
  `port_range_max` int(11) DEFAULT NULL,
  `port_range_min` int(11) DEFAULT NULL,
  `protocol` int(11) DEFAULT NULL,
  `remote_ip_prefix` varchar(22) DEFAULT NULL,
  `remote_group_id` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `quark_security_group_rule_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `quark_security_groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_security_groups`
--

DROP TABLE IF EXISTS `quark_security_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_security_groups` (
  `created_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_quark_security_groups_tenant_id` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_subnets`
--

DROP TABLE IF EXISTS `quark_subnets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_subnets` (
  `created_at` datetime DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `network_id` varchar(36) DEFAULT NULL,
  `_cidr` varchar(64) NOT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  `segment_id` varchar(255) DEFAULT NULL,
  `first_ip` char(39) DEFAULT NULL,
  `last_ip` char(39) DEFAULT NULL,
  `ip_version` int(11) DEFAULT NULL,
  `next_auto_assign_ip` char(39) DEFAULT NULL,
  `enable_dhcp` tinyint(1) DEFAULT NULL,
  `ip_policy_id` varchar(36) DEFAULT NULL,
  `do_not_use` tinyint(1) DEFAULT NULL,
  `tag_association_uuid` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `network_id` (`network_id`),
  KEY `ip_policy_id` (`ip_policy_id`),
  KEY `tag_association_uuid` (`tag_association_uuid`),
  KEY `ix_quark_subnets_tenant_id` (`tenant_id`),
  KEY `ix_quark_subnets_segment_id` (`segment_id`),
  CONSTRAINT `quark_subnets_ibfk_1` FOREIGN KEY (`network_id`) REFERENCES `quark_networks` (`id`),
  CONSTRAINT `quark_subnets_ibfk_2` FOREIGN KEY (`ip_policy_id`) REFERENCES `quark_ip_policy` (`id`),
  CONSTRAINT `quark_subnets_ibfk_3` FOREIGN KEY (`tag_association_uuid`) REFERENCES `quark_tag_associations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_tag_associations`
--

DROP TABLE IF EXISTS `quark_tag_associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_tag_associations` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `discriminator` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quark_tags`
--

DROP TABLE IF EXISTS `quark_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_tags` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `association_uuid` varchar(36) NOT NULL,
  `tag` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `association_uuid` (`association_uuid`),
  CONSTRAINT `quark_tags_ibfk_1` FOREIGN KEY (`association_uuid`) REFERENCES `quark_tag_associations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quotas`
--

DROP TABLE IF EXISTS `quotas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quotas` (
  `id` varchar(36) NOT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  `resource` varchar(255) DEFAULT NULL,
  `limit` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_quotas_tenant_id` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subnetroutes`
--

DROP TABLE IF EXISTS `subnetroutes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subnetroutes` (
  `destination` varchar(64) NOT NULL,
  `nexthop` varchar(64) NOT NULL,
  `subnet_id` varchar(36) NOT NULL,
  PRIMARY KEY (`destination`,`nexthop`,`subnet_id`),
  KEY `subnet_id` (`subnet_id`),
  CONSTRAINT `subnetroutes_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subnets`
--

DROP TABLE IF EXISTS `subnets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subnets` (
  `tenant_id` varchar(255) DEFAULT NULL,
  `id` varchar(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `network_id` varchar(36) DEFAULT NULL,
  `ip_version` int(11) NOT NULL,
  `cidr` varchar(64) NOT NULL,
  `gateway_ip` varchar(64) DEFAULT NULL,
  `enable_dhcp` tinyint(1) DEFAULT NULL,
  `shared` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `network_id` (`network_id`),
  CONSTRAINT `subnets_ibfk_1` FOREIGN KEY (`network_id`) REFERENCES `networks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-03-24 23:06:03
