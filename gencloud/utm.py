import logging
import os
import plistlib
import random
import uuid

from .util import runcmd


class UTM:
    def __init__(self, vmspec):
        self.vmspec = vmspec
        self.logger = logging.getLogger(self.__class__.__name__)
        self.utm_dir = f"{self.vmspec.dom_name}.utm"
        self.data_dir = os.path.join(self.utm_dir, "Data")

    def _genmac(self):
        self.logger.info("generating mac address")

        i, vmmac = 0, "52:54:"
        while i < 4:
            col = hex(random.randint(0, 255)).lstrip("0x")
            if len(col) < 2:
                col = f"{col}0"
            vmmac += f"{col}:"

            i += 1

        return str(vmmac.rstrip(":"))

    def _mkplist(self):
        with open(os.path.join(self.utm_dir, "config.plist"), "wb") as f:
            plistlib.dump(
                {
                    "Backend": "QEMU",
                    "ConfigurationVersion": 4,
                    "Display": [],
                    "Drive": [
                        {
                            "Identifier": str(uuid.uuid4()).upper(),
                            "ImageName": "overlay.qcow2",
                            "ImageType": "Disk",
                            "Interface": "VirtIO",
                            "InterfaceVersion": 1,
                            "ReadOnly": False,
                        },
                        {
                            "Identifier": str(uuid.uuid4()).upper(),
                            "ImageName": "cidata.iso",
                            "ImageType": "CD",
                            "Interface": "VirtIO",
                            "InterfaceVersion": 1,
                            "ReadOnly": True,
                        },
                    ],
                    "Information": {
                        "IconCustom": False,
                        "Name": self.vmspec.dom_name,
                        "UUID": str(uuid.uuid4()).upper(),
                    },
                    "Input": {
                        "MaximumUsbShare": 3,
                        "UsbBusSupport": "3.0",
                        "UsbSharing": False,
                    },
                    "Network": [
                        {
                            "Hardware": "virtio-net-pci",
                            "IsolateFromHost": False,
                            "MacAddress": self._genmac(),
                            "Mode": "Shared",
                            "PortForward": [],
                            "VlanDhcpEndAddress": "=",
                            "VlanDhcpStartAddress": "=",
                        }
                    ],
                    "QEMU": {
                        "AdditionalArguments": [],
                        "BalloonDevice": False,
                        "DebugLog": False,
                        "Hypervisor": True,
                        "PS2Controller": False,
                        "RNGDevice": True,
                        "RTCLocalTime": False,
                        "TPMDevice": False,
                        "TSO": False,
                        "UEFIBoot": True,
                    },
                    "Serial": [
                        {"Hardware": "virtserialport", "Mode": "Ptty", "Target": "Auto"}
                    ],
                    "Sharing": {
                        "ClipboardSharing": False,
                        "DirectoryShareMode": "None",
                        "DirectoryShareReadOnly": False,
                    },
                    "Sound": [],
                    "System": {
                        "Architecture": "aarch64",
                        "CPU": "host",
                        "CPUCount": self.vmspec.dom_vcpu,
                        "CPUFlagsAdd": [],
                        "CPUFlagsRemove": [],
                        "ForceMulticore": False,
                        "JITCacheSize": 0,
                        "MemorySize": self.vmspec.dom_mem,
                        "Target": "virt",
                    },
                },
                f,
                fmt=plistlib.FMT_XML,  # pylint: disable=no-member
            )

    def _mkdirs(self):
        os.makedirs(self.utm_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def _mkqcow(self):
        overlay_path = os.path.join(self.data_dir, "overlay.qcow2")

        runcmd(
            f"qemu-img convert -f qcow2 -O qcow2 {self.vmspec.base_image} {overlay_path}"
        )
        runcmd(f"qemu-img resize {overlay_path} {self.vmspec.vol_size}G")

    def mkvm(self):
        self._mkdirs()
        self._mkplist()
        self._mkqcow()
