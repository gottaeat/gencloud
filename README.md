# genutm
`genutm` creates `aarch64` linux VMs that run via Apple Virtualization Framework
utilizing UTM bundles, alongside the `CIDATA` `cloud-init` ISOs that hold the
`user-data` and `meta-data` YAMLs.

## installation and usage
docker is necessary to call `qemu-imq` without having to install the full `qemu`
suite via `brew`. `picocom` is for providing serial console access when the user
doesn't enable ssh key access for a user they create.
```sh
# pull deps
brew install docker utm --cask
brew install picocom

# install release
pip install genutm

# pull latest debian 12 qcow2
curl -L \
    https://cdimage.debian.org/images/cloud/bookworm/latest/debian-12-generic-arm64.qcow2 \
    -o $HOME/debian-12-generic-arm64.qcow2

# create userspec
genutm mkuser

# create vmspec
cat << EOF > vm.yml
---
vmspec:
  dom_name: debian12arm1
  dom_mem: 2048
  dom_vcpu: 2
  vol_size: 10
  base_image: $HOME/debian-12-generic-arm64.qcow2
  sshpwauth: yes
EOF

# create arbitrary user-data additions (optional)
cat << EOF > userdata.yml
package_update: true
package_upgrade: true

packages:
  - apt-transport-https
  - ca-certificates
  - curl
  - gnupg

write_files:
  - path: /tmp/hello.txt
    content: |
      hello world!

runcmd:
  - systemctl mask iptables
  - systemctl enable --now nftables
EOF

# create cidata.iso and utm bundle
gencloud create vm.yml --users userspec-*.yml --userdata userdata.yml

# register and start vm
open debian12arm1.utm

# hook up to serial
picocom /dev/ttys006
```

## configuration
### specification
#### domains
| key            | necessity | description                                                                              |
| -------------- | --------- | ---------------------------------------------------------------------------------------- |
| dom_name       | required  | `str` name of the domain                                                                 |
| dom_mem        | required  | `int` amount of memory in megabytes                                                      |
| dom_vcpu       | required  | `int` core count                                                                         |
| vol_size       | required  | `int` disk size in gigabytes                                                             |
| base_image     | required  | `str` full path to the `cloud-init` capable cloud image[1]                               |
| sshpwauth      | optional  | `bool` whether to allow ssh authentication via passwords (VM-wide, applies to all users) |

#### users
| key           | necessity | description                                                                                            |
| ------------- | --------- | ------------------------------------------------------------------------------------------------------ |
| name          | required  | `str` name of the user                                                                                 |
| password_hash | optional  | `str` password hash in `shadow` compliant `crypt()` format (like `mkuser` output)                      |
| ssh_keys      | optional  | `list of str` list of ssh keys to append to the `authorized_keys` of the user                          |
| sudo_god_mode | required  | `bool` toggle for adding the user to the `sudo` group and allowing it to run `sudo` without a password |

__WARNING__: if you do not specify any authentication method in the file
supplied via `--users` and if you:
1. do not specify an arbitrary `user-data` file via `--userdata`,
2. or, specify a `user-data` but the resulting final `cloud-init` `user-data`
yaml to be written to the iso ends up having no valid authentication method

program will halt.

### examples
#### `--users <userspec.yml>`
you can also do `genutm mkuser` to interactively generate a `userspec.yml`
through prompts.
```yml
---
userspec:
    - name: john
      password_hash: '$y$j9T$/gPg8H0fdtuZh8Ja8decf.$f7IzP89gNaToHUsY2bdgaxv2HJsKSRYLyG6mxNZ6AW3'
      sudo_god_mode: true

    - name: doe
      ssh_keys:
        - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI0000000000000000000000000000000000000000000

```

#### `<vmspec.yml>`
```yml
---
vmspec:
    dom_name: testvm
    dom_mem: 2048
    dom_vcpu: 2
    net: cloudvirt
    vol_size: 10
    base_image: /Users/user/debian-12-generic-arm64.qcow2
    sshpwauth: true
```
