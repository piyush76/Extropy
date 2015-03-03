define text::append_if_no_such_line($file, $line, $refreshonly = 'false') {
   exec { "/bin/echo '$line' >> '$file'":
      unless => "/bin/grep -Fxqe '$line' '$file'",
      path => "/bin",
      refreshonly => $refreshonly,
   }
}

define text::prepend_if_no_such_line($file, $line, $refreshonly = 'false') {
   exec { "/usr/bin/perl -p0i -e 's/^/$line\n/;' '$file'":
      unless      => "/bin/grep -Fxqe '$line' '$file'",
      path        => "/bin",
      refreshonly => $refreshonly,
   }
}

define text::ensure_key_value($file, $key, $value, $delimeter = " ") {
    # append line if "$key" not in "$file"
    exec { "echo '$key$delimeter$value' >> $file":
       unless => "grep -qe '^$key[[:space:]]*$delimeter' -- $file",
       path => "/bin:/usr/bin"
    }

    # update it if it already exists...
    exec { "sed -i 's/^$key$delimeter.*$/$key$delimeter$value/g' $file":
        unless => "grep -e '^$key[[:space:]]*$delimeter[[:space:]]*' -- $file | fgrep -q '$value'",
        path => "/bin:/usr/bin"
    }
}
