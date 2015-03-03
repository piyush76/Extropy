require 'puppet'
require 'time'

Puppet::Network::Handler.report.newreport(:groundwork) do
    desc "Send all received logs to groundwork via its mythical, crappy SOAP API"

    def threshold
        unless defined? @threshold 
	    @threshold = self.levels.index(:notice)
        end
        @threshold
    end

    def levels
        unless defined? @levels 
	    @levels = Puppet::Util::Log.levels
        end
        @levels
    end

    def match?(log)
        self.levels.index(log.level) >= self.threshold
    end

    def process
        t = Time.now
        self.logs.find_all {|log| self.match? log}.each do |log|
            file = File.join("/var/log/puppet/clients", self.host)
            File.open(file, 'a') { |f|
                f.puts "%s\t%f\t%s\t%s\t%s" % [t, t, log.level, log.source, log.to_s]
            }
        end
    end
end

# $Id: log.rb 2367 2007-03-29 18:22:24Z luke $

