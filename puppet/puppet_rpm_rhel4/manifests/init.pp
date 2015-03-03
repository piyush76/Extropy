class puppet_rpm_rhel4::repo {
    yum::repo {
        "PM-RHEL4":
            source => "/var/lib/hannibal/sync/modules/puppet_rpm_rhel4/files";
    }
}

class puppet_rpm_rhel4::client {
    yum::client{
        "PM-RHEL4":
            server => $yum_server;
    }
}
