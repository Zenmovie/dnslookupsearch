# dnslookupsearch

## Description:
Small DNS Recon utility, allows you to obtain some useful info about NS-servers placed behind relays, firewalls, etc. Also it can find subdomains by your wordlist.

Requires 'dig' utility!

## Examples:


$ ./dnslookup.py --server ns9.nic.ru
```json
{
    "ns9.nic.ru": {
        "ip": "31.177.85.186", 
        "servers": [
            {
                "ip": "31.177.85.194", 
                "name": "ns9-1.nic.ru"
            }
        ], 
        "versions": []
    }
}
```

$ ./dnslookup.py --domain yandex.ru

```json
    {
        "ns1.yandex.ru.": {
            "ip": "213.180.193.1",
            "servers": [],
            "versions": [
                "Yandex"
            ]
        },
        "ns2.yandex.ru.": {
            "ip": "93.158.134.1",
            "servers": [],
            "versions": [
                "Yandex"
            ]
        },
        "ns9.z5h64q92x9.net.": {
            "ip": "154.47.36.189",
            "servers": [],
            "versions": [
                "Yandex"
            ]
        }
    }
```

$ ./dnslookup.py -d google.com --subdomain subd.txt

```json
[
    {
        "ns1.google.com.": {
            "ip": "216.239.32.10",
            "servers": [],
            "versions": []
        },
        "ns2.google.com.": {
            "ip": "216.239.34.10",
            "servers": [],
            "versions": []
        },
        "ns3.google.com.": {
            "ip": "216.239.36.10",
            "servers": [],
            "versions": []
        },
        "ns4.google.com.": {
            "ip": "216.239.38.10",
            "servers": [],
            "versions": []
        }
    },
    {
        "0": {
            "Domain:": "google.com",
            "Subdomain:": ""
        },
        "1": {
            "Domain:": "google.com",
            "Subdomain:": "https://mail.google.com/"
        },
        "2": {
            "Domain:": "google.com",
            "Subdomain:": "https://www.google.com/"
        },
        "3": {
            "Domain:": "google.com",
            "Subdomain:": "https://admin.google.com/"
        }
    }
]
```