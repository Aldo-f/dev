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
  'instanceid' => 'oc4t3ftfs2n4',
  'passwordsalt' => '2cKu3y0gouIBJm1jubkpiwslK7i2X2',
  'secret' => 'RtDxfNPNIkH/Oo5oDvJsaqsJj5l2ctBHUL08i1FeZJxvfmFg',
  'trusted_domains' => 
  array (
    0 => '192.168.0.5:8888',
    1 => 'cloud.aldof.duckdns.org',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'mysql',
  'version' => '34.0.2.1',
  'overwrite.cli.url' => 'https://cloud.aldof.duckdns.org',
  'dbname' => 'nextcloud',
  'dbhost' => 'db',
  'dbtableprefix' => 'oc_',
  'mysql.utf8mb4' => true,
  'dbuser' => 'nextcloud',
  'dbpassword' => 'nextcloudpassword',
  'installed' => true,
  'maintenance' => true,
  'memcache.distributed' => '\\OC\\Memcache\\Redis',
  'memcache.locking' => '\\OC\\Memcache\\Redis',
  'redis' => 
  array (
    'host' => 'redis',
    'port' => 6379,
    'timeout' => '0',
    'password' => 'nextcloudpassword',
  ),
  'overwritehost' => 'cloud.aldof.duckdns.org',
  'overwriteprotocol' => 'https',
  'overwritecondaddr' => '\\\\.aldof\\\\.duckdns\\\\.org$',
  'trusted_proxies' => 
  array (
    0 => '172.18.0.0/16',
  ),
  'loglevel' => 2,
);
