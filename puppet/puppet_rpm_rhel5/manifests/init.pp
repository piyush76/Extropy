class puppet_rpm_rhel5::repo {
    yum::repo {
        "PM-RHEL5":
            source => "/var/lib/hannibal/sync/modules/puppet_rpm_rhel5/files"
    }
}


class puppet_rpm_rhel5::client {
    case $yum_server {
        $servername: {
            yumrepo {
                "PM-RHEL5":
                    gpgcheck => 0,
                    enabled => 1,
                    descr => "PM-RHEL5",
                    baseurl => "file:///var/www/thttpd/html/yum-PM-RHEL5";
            }
        }
        default: {
            yum::client {
                "PM-RHEL5":
                    server => $yum_server;
            }
        }
    }
}
