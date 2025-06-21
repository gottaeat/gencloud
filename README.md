# gencloud
gencloud creates `CIDATA` `cloud-init` ISOs that hold `user-data` and
`meta-data` YAMLs.

## installation
### 1. stable
```sh
pip install gencloud
```

### 2. dev
```sh
git clone --depth=1 https://github.com/gottaeat/gencloud
cd gencloud/
pip install .
```

## configuration
### specification
#### domains
| key            | necessity | description                                                                              |
| -------------- | --------- | ---------------------------------------------------------------------------------------- |
| dom_name       | required  | `str` name of the domain                                                                 |
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
you can also do `gencloud mkuser` to interactively generate a `userspec.yml`
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
    dom_name: test
    sshpwauth: false
```

### usage
```sh
gencloud --help
```
