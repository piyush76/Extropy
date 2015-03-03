Puppet::Type.type(:service).provide :runit, :parent => :base do
    desc "Support for runit."

    commands :sv => "/sbin/sv", :mklink => "/bin/ln", :rmlink => "/bin/rm"

    def source
        "/var/service/" + @resource[:name]
    end

    def target
        "/etc/sv/" + @resource[:name]
    end

    def enable
        begin
            output = mklink "-f", "-s", self.target, self.source
        rescue Puppet::ExecutionFailure
            raise Puppet::Error, "Could not enable %s: %s" % [self.name, output]
        end
    end

    def enabled?
        if File.symlink?(self.source) and File.new(self.source).stat.ino == File.new(self.target).stat.ino:
	    return :true
        else
            return :false
        end
    end

    def disable
        begin
            output = rmlink self.source
        rescue Puppet::ExecutionFailure
            raise Puppet::Error, "Could not disable %s: %s" % [self.name, output]
        end
    end

    def statuscmd
        [command(:sv), "-v", "status", @resource[:name]]
    end

    def restartcmd
        [command(:sv), "-v", "force-restart", @resource[:name]]
    end

    def startcmd
        [command(:sv), "-v", "start", @resource[:name]]
    end

    def stopcmd
        [command(:sv), "-v", "force-stop", @resource[:name]]
    end
end
