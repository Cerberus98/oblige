-- MySQL dump 10.13  Distrib 5.5.31, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: melange
-- ------------------------------------------------------
-- Server version	5.5.31-0+wheezy1

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

--
-- Table structure for table `allocatable_ips`
--

DROP TABLE IF EXISTS `allocatable_ips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allocatable_ips` (
  `id` varchar(36) NOT NULL,
  `ip_block_id` varchar(36) DEFAULT NULL,
  `address` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_block_id` (`ip_block_id`),
  CONSTRAINT `allocatable_ips_ibfk_1` FOREIGN KEY (`ip_block_id`) REFERENCES `ip_blocks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `allocatable_macs`
--

DROP TABLE IF EXISTS `allocatable_macs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allocatable_macs` (
  `id` varchar(36) NOT NULL,
  `mac_address_range_id` varchar(36) DEFAULT NULL,
  `address` bigint(20) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mac_address_range_id` (`mac_address_range_id`),
  CONSTRAINT `allocatable_macs_ibfk_1` FOREIGN KEY (`mac_address_range_id`) REFERENCES `mac_address_ranges` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `allowed_ips`
--

DROP TABLE IF EXISTS `allowed_ips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allowed_ips` (
  `id` varchar(36) NOT NULL,
  `ip_address_id` varchar(36) NOT NULL,
  `interface_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip_address_id` (`ip_address_id`,`interface_id`),
  KEY `interface_id` (`interface_id`),
  CONSTRAINT `allowed_ips_ibfk_1` FOREIGN KEY (`ip_address_id`) REFERENCES `ip_addresses` (`id`),
  CONSTRAINT `allowed_ips_ibfk_2` FOREIGN KEY (`interface_id`) REFERENCES `interfaces` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dnsnameservers`
--

DROP TABLE IF EXISTS `dnsnameservers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dnsnameservers` (
  `address` varchar(128) NOT NULL,
  `subnet_id` varchar(36) NOT NULL,
  PRIMARY KEY (`address`,`subnet_id`),
  KEY `subnet_id` (`subnet_id`),
  CONSTRAINT `dnsnameservers_ibfk_1` FOREIGN KEY (`subnet_id`) REFERENCES `subnets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `interfaces`
--

DROP TABLE IF EXISTS `interfaces`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interfaces` (
  `id` varchar(36) NOT NULL,
  `vif_id_on_device` varchar(36) DEFAULT NULL,
  `device_id` varchar(36) DEFAULT NULL,
  `tenant_id` varchar(36) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip_addresses`
--

DROP TABLE IF EXISTS `ip_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip_addresses` (
  `id` varchar(36) NOT NULL,
  `address` varchar(255) NOT NULL,
  `interface_id` varchar(255) DEFAULT NULL,
  `ip_block_id` varchar(36) DEFAULT NULL,
  `used_by_tenant_id` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `marked_for_deallocation` tinyint(1) DEFAULT NULL,
  `deallocated_at` datetime DEFAULT NULL,
  `allocated` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`,`ip_block_id`),
  KEY `interface_id` (`interface_id`),
  KEY `ip_block_id` (`ip_block_id`),
  CONSTRAINT `ip_addresses_ibfk_1` FOREIGN KEY (`interface_id`) REFERENCES `interfaces` (`id`),
  CONSTRAINT `ip_addresses_ibfk_2` FOREIGN KEY (`ip_block_id`) REFERENCES `ip_blocks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip_blocks`
--

DROP TABLE IF EXISTS `ip_blocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip_blocks` (
  `id` varchar(36) NOT NULL,
  `network_id` varchar(255) DEFAULT NULL,
  `cidr` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `type` varchar(7) DEFAULT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  `gateway` varchar(255) DEFAULT NULL,
  `dns1` varchar(255) DEFAULT NULL,
  `dns2` varchar(255) DEFAULT NULL,
  `allocatable_ip_counter` bigint(20) DEFAULT NULL,
  `is_full` tinyint(1) DEFAULT NULL,
  `policy_id` varchar(36) DEFAULT NULL,
  `parent_id` varchar(36) DEFAULT NULL,
  `network_name` varchar(255) DEFAULT NULL,
  `omg_do_not_use` tinyint(1) DEFAULT NULL,
  `max_allocation` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `ip_blocks_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `ip_blocks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ip_blocks_ibfk_2` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip_nats`
--

DROP TABLE IF EXISTS `ip_nats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip_nats` (
  `id` varchar(36) NOT NULL,
  `inside_local_address_id` varchar(36) NOT NULL,
  `inside_global_address_id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inside_local_address_id` (`inside_local_address_id`),
  KEY `inside_global_address_id` (`inside_global_address_id`),
  CONSTRAINT `ip_nats_ibfk_1` FOREIGN KEY (`inside_local_address_id`) REFERENCES `ip_addresses` (`id`),
  CONSTRAINT `ip_nats_ibfk_2` FOREIGN KEY (`inside_global_address_id`) REFERENCES `ip_addresses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip_octets`
--

DROP TABLE IF EXISTS `ip_octets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip_octets` (
  `id` varchar(36) NOT NULL,
  `octet` int(11) NOT NULL,
  `policy_id` varchar(36) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `ip_octets_ibfk_1` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip_ranges`
--

DROP TABLE IF EXISTS `ip_ranges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip_ranges` (
  `id` varchar(36) NOT NULL,
  `offset` int(11) NOT NULL,
  `length` int(11) NOT NULL,
  `policy_id` varchar(36) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `ip_ranges_ibfk_1` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ip_routes`
--

DROP TABLE IF EXISTS `ip_routes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ip_routes` (
  `id` varchar(36) NOT NULL,
  `destination` varchar(255) NOT NULL,
  `netmask` varchar(255) DEFAULT NULL,
  `gateway` varchar(255) NOT NULL,
  `source_block_id` varchar(36) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `source_block_id` (`source_block_id`),
  CONSTRAINT `ip_routes_ibfk_1` FOREIGN KEY (`source_block_id`) REFERENCES `ip_blocks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ipallocationpools`
--

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
-- Table structure for table `mac_address_ranges`
--

DROP TABLE IF EXISTS `mac_address_ranges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mac_address_ranges` (
  `id` varchar(36) NOT NULL,
  `cidr` varchar(255) NOT NULL,
  `next_address` bigint(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mac_addresses`
--

DROP TABLE IF EXISTS `mac_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mac_addresses` (
  `id` varchar(36) NOT NULL,
  `address` bigint(20) NOT NULL,
  `mac_address_range_id` varchar(36) DEFAULT NULL,
  `interface_id` varchar(36) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`),
  UNIQUE KEY `interface_id` (`interface_id`),
  KEY `mac_address_range_id` (`mac_address_range_id`),
  CONSTRAINT `mac_addresses_ibfk_1` FOREIGN KEY (`mac_address_range_id`) REFERENCES `mac_address_ranges` (`id`),
  CONSTRAINT `mac_addresses_ibfk_2` FOREIGN KEY (`interface_id`) REFERENCES `interfaces` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `migrate_version`
--

DROP TABLE IF EXISTS `migrate_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `migrate_version` (
  `repository_id` varchar(250) NOT NULL,
  `repository_path` text,
  `version` int(11) DEFAULT NULL,
  PRIMARY KEY (`repository_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
-- Table structure for table `policies`
--

DROP TABLE IF EXISTS `policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `policies` (
  `id` varchar(36) NOT NULL,
  `name` varchar(255) NOT NULL,
  `tenant_id` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
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
  `ip` blob,
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
  `address` blob NOT NULL,
  `subnet_id` varchar(36) DEFAULT NULL,
  `network_id` varchar(36) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `allocated_at` datetime DEFAULT NULL,
  `_deallocated` tinyint(1) DEFAULT NULL,
  `used_by_tenant_id` varchar(255) DEFAULT NULL,
  `deallocated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet_id` (`subnet_id`),
  KEY `network_id` (`network_id`),
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
-- Table structure for table `quark_ip_policy_rules`
--

DROP TABLE IF EXISTS `quark_ip_policy_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quark_ip_policy_rules` (
  `id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `ip_policy_id` varchar(36) DEFAULT NULL,
  `offset` int(11) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_policy_id` (`ip_policy_id`),
  CONSTRAINT `quark_ip_policy_rules_ibfk_1` FOREIGN KEY (`ip_policy_id`) REFERENCES `quark_ip_policy` (`id`) ON DELETE CASCADE
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
  CONSTRAINT `quark_mac_addresses_ibfk_1` FOREIGN KEY (`mac_address_range_id`) REFERENCES `quark_mac_address_ranges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=187723558158504 DEFAULT CHARSET=latin1;
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
  `max_allocation` int(11) DEFAULT NULL,
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
  PRIMARY KEY (`id`)
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
  PRIMARY KEY (`id`)
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
  KEY `ip_address_id` (`ip_address_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
  KEY `group_id` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
  KEY `ix_quark_ports_device_id` (`device_id`),
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
  `first_ip` blob,
  `last_ip` blob,
  `ip_version` int(11) DEFAULT NULL,
  `next_auto_assign_ip` blob,
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

-- Dump completed on 2013-12-20 16:21:56
