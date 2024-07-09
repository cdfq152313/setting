export extern "ssh" [
    destination?: string@"nu-complete ssh-host"
] 

def "nu-complete ssh-host" [] {
    let files = [
        '/etc/ssh/ssh_config',
        '~/.ssh/config'
    ] | filter { |file| $file | path exists } 

    $files | each { |file|
        let lines = $file | open | lines | str trim
        let hosts = $lines
        | parse --regex '^Host\s+(?<host>.+)'
        | get host

        let hostnames = $lines
        | parse --regex '^HostName\s+(?<hostname>.+)'
        | get hostname
        $hosts | zip $hostnames | each { || 
            {'value': $in.0, 'description': $in.1}
        }
    } | flatten
}