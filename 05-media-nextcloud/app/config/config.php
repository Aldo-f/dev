<?php

/*
 * WARNING
 *
 * This file gets modified by automatic processes and all lines that are not
 * active code (ie. comments) are lost during that process.
 *
 * If you want to document things with comments or use constants add your settings
 * in a '<NAME>.config.php' file which will be included and rendered into this file.
 *
 * Example:
 *   <?php
 *   $CONFIG = [];
 *
 * See also: https://docs.nextcloud.com/server/latest/admin_manual/configuration_server/config_sample_php_parameters.html#multiple-merged-configuration-files
 */
$CONFIG = array (
  'htaccess.RewriteBase' => '/',
  'memcache.local' => '\\OC\\Memcache\\APCu',
  'apps_paths' => 
  array (
    0 => 
    array (
      'path' => '/var/www/html/apps',
      'url' => '/apps',
      'writable' => false,
    ),
    1 => 
    array (
      'path' => '/var/www/html/custom_apps',
      'url' => '/custom_apps',
      'writable' => true,
    ),
  ),
  'upgrade.disable-web' => true,
  'instanceid' => 'oc0tom8od1f5',
  'memcache.distributed' => '\\OC\\Memcache\\Redis',
  'memcache.locking' => '\\OC\\Memcache\\Redis',
  'redis' => 
  array (
    'host' => 'redis',
    'password' => 'nextcloudpassword',
    'port' => 6379,
    'timeout' => 0,
  ),
  'passwordsalt' => 'yoL/gri4iE2cgFZHYifE3vLS6gn46x',
  'secret' => 'PszlNFYrjaZABMn0tvlVaxxr4TF/Vt05t6+eXAl+SIMYA8ds',
  'trusted_domains' => 
  array (
    0 => 'cloud.aldof.duckdns.org',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'mysql',
  'version' => '34.0.3.2',
  'overwrite.cli.url' => 'http://localhost',
  'dbname' => 'nextcloud',
  'dbhost' => 'db',
  'dbtableprefix' => 'oc_',
  'mysql.utf8mb4' => true,
  'dbuser' => 'nextcloud',
  'dbpassword' => 'nextcloudpassword',
  'installed' => true,
  'overwritehost' => 'cloud.aldof.duckdns.org',
  'overwriteprotocol' => 'https',
  'default_phone_region' => 'BE',
  'maintenance' => false,
);
