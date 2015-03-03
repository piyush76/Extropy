# Steamlines installation of a PHP-PEAR module
#
# Example:
# pear::install {
#   "XML_Parser":
#       version => "1.0.1"
# }
#
# You can omit the "version" parameter if you just want the latest.
define pear::install($version=false) {
    $pearcmd = "/usr/bin/php -f /usr/share/pear/pearcmd.php"
    $pkgname = $version ? {
        false => $name,
        default => "$name-$version",
    }

    $already_installed = $version ? {
        false => "$pearcmd list | /bin/grep ^$name\\ ",
        default => "$pearcmd list | /bin/grep ^$name\\ | /bin/grep $version\\ ",
    }

    exec {
        # The following 2 steps are hacks to ensure that we've got a current
        # version of PEAR installed on the box. 

        # First, we need to upgrade to PEAR-1.3.3 (we're so out of date that
        # we can't upgrade directly to PEAR-1.4.x without going to 1.3.3 first)
        "pear-upgrade-step1-$name":
            command => "$pearcmd upgrade --force http://pear.php.net/get/PEAR-1.3.3.tar http://pear.php.net/get/Console_Getopt-1.2.tar http://pear.php.net/get/Archive_Tar-1.3.1.tar",
            unless => "$pearcmd info pear | /bin/grep -e '^ABOUT PEAR-1.3.3' -e '^ABOUT PEAR-1.4.'",
            require => [Package["php"], Package["php-pear"]];

        # Then, we upgrade to PEAR-1.4.11 (a version known to do what we want)
        "pear-upgrade-step2-$name":
            command => "$pearcmd upgrade --force http://pear.php.net/get/PEAR-1.4.11",
            unless => "$pearcmd info pear | /bin/grep '^ABOUT PEAR-1.4.'",
            require => [Package["php"], Package["php-pear"], Exec["pear-upgrade-step1-$name"]];

        # Now we can finally install the actual package. Sheesh...
        "pear-install-$name":
            command => "$pearcmd upgrade $pkgname",
            unless => "$already_installed",
            require => [Package["php"], Package["php-pear"], Exec["pear-upgrade-step2-$name"]];
    }
}
