# nillion-ipfs-store
encrypt, store to IPFS, then save encryption keys to Nillion nilvm network 

reference implementation for large files in Nillion.


# prerequisites

1. install and run an [ipfs node](https://docs.ipfs.io/install/) or [desktop app](https://github.com/ipfs/ipfs-desktop)
2. install python deps
```shell
pip3 install -r requirements.txt
```
3. copy `.env.sample` to `.env` and customize to suit

# usage

## add file to network

`python3 add.py <PATH-TO-FILE> [<PATH-TO-FILE> <PATH-TO-FILE> ...]`

```shell
$ python3 add.py ~/Downloads/pop-os_22.04_amd64_intel_43.iso 
    sending /tmp/tmp45lrng_6 to ipfs (agent id:12D3KooWD7TeKCA19eF7VV7Ls4mejqqqcuTnUXbMQgiD5oJfEPVf)
    stored to ipfs cid QmRtUzk3ivAy1TTUrXMAp6iQK6ZpDzN7QsMtWr2ctbdF6D
    Getting quote for operation...
    Quote cost is 4322 unil
    Submitting payment receipt 4322 unil, tx hash 747AD8E3159541C35BE49094D7C20E2F2FDA781ECC4178523B3FD47FE584A7FB
    The secret is stored at store_id: 5b531834-98c2-4b13-a29f-ea658d21ba6e
```

## get file from network

`python3 get.py <NILLION-STORE-ID>`

```shell
$ python3 get.py 5b531834-98c2-4b13-a29f-ea658d21ba6e                                                     
    Getting quote for operation...
    Quote cost is 2 unil
    Submitting payment receipt 2 unil, tx hash 7FFDF5E23F88650D6FBBC8D73335080DFFB47040DA092E8109168C17DC8873E3
    The nillion secret value is '{"cid": "QmRtUzk3ivAy1TTUrXMAp6iQK6ZpDzN7QsMtWr2ctbdF6D", "filename": "pop-os_22.04_amd64_intel_43.iso", "size": 2657157120, "key": "A0jSZP8rFbp2Ngi4Bh0OP2iEiZlRWD1CwWLOIvAhzPc=", "sig": "rn8oeZmNHEcESn2N", "iv": "PGCP9oPkSx5s3a3S", "tag": "box00IaMXT+B87t77Sj9ZA=="}'
    file decrypted to: [/tmp/tmp9dx5hk6r/pop-os_22.04_amd64_intel_43.iso]
```

