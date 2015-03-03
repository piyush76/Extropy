# Abstraction for ensuring that a directory is listed in /etc/exports on an NFS
# server.
# 
# Ex:
# nfsserver::export {
#     "/export/this":
#         ensure => "present";
#     
#     "/export/this2":
#         ensure => "absent";
#
#     "/export/this3":
#         options => "(rw,all_squash,anonuid=10219,anongid=10219,async)";
define nfsutils::export($options=false, $ensure=present) {
    include nfsutils::bootstrap

    $nfsopts = $options ? {
        true => $options,
        false => "rw,all_squash,anonuid=10219,anongid=10219,async",
    }
    $line = "$name $private_network/$private_netmask($nfsopts)"

    exec {
        "update-exports-$name":
            command => $ensure ? {
                present => "(grep -v '^$name ' /etc/exports; echo '$line') > /tmp/puppet.exports; mv /tmp/puppet.exports /etc/exports",
                absent => "grep -v '^$name ' /etc/exports > /tmp/puppet.exports; mv /tmp/puppet.exports /etc/exports",
            },
            unless => "grep '$line' /etc/exports",
            path => ["/bin", "/usr/bin"],
            notify => Service[nfs];
    }
}
