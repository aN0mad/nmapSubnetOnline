# nmapSubnetOnline
Verify an nmap file against a target range file to determine if the network subnet is online or offline.

## Installation
### Python
1. Clone the repo
2. Install dependencies - Virtual environments are recommended (ie. poetry)
```bash
pip install -r requirements.txt
```
3. Run the main script file
```bash
python main.py
```

### pipx (Recommended)
1. Clone the repo
2. Install the script using `pipx`
```bash
pipx install .
```
3. Run the program
```
nmapsubnetonline -h
```

### Docker
1. Clone the repo
2. Build the container
```bash
docker build -t nso .
```
3. Run the container and map directories inside
```bash
docker run --rm -v ${PWD}:/data nso
```


### Development
Development of this project is done with `poetry` as it makes managing the depencies and virtual envs much easier.
1. Clone the repo
2. Install the dependencies
```bash
poetry install
```
3. Enter the poetry shell
```bash
poetry shell
```
4. Modify source or run the main script file from this shell

## Usage
```bash
usage: nmapSubnetOnline [-h] -r RANGES [-n NMAP] [-d DIR] [-o OUTPUT] [--debug] [--quiet]

Verify an nmap file against a target range file to determine if the network is online or offline

options:
  -h, --help            show this help message and exit
  -r RANGES, --ranges RANGES
                        Range file to check for online hosts
  -n NMAP, --nmap NMAP  Path to nmap output file (Supports multiple flags)
  -d DIR, --dir DIR     Directory of nmap output files
  -o OUTPUT, --output OUTPUT
                        Directory for output files
  --debug               Enable debug
  --quiet               Enable quiet mode

Example: nmapSubnetOnline -r ranges.txt -n nmap.xml -d /path/to/nmap/files/
```

## Examples 
### Python/Pipx Installation
```bash
(nmapsubnetonline-py3.11) root@cfeaca12f15c:/workspaces/nmapSubnetOnline# nmapSubnetOnline -r example/ranges.txt -d example/
2024-05-29T16:05:44.429698+0000 | SUCCESS | nmapsubnetonline.nmapsubnetonline has started
2024-05-29T16:05:44.434502+0000 | INFO | Reading range file 'example/ranges.txt'
2024-05-29T16:05:44.437332+0000 | INFO | Reading nmap file 'example/ping.xml'
2024-05-29T16:05:44.440492+0000 | INFO | Reading nmap file 'example/possible_dc.xml'
2024-05-29T16:05:44.449440+0000 | INFO | Outputting results to csv file
```

### Docker installation
There are a couple gotchas when running tooling within a docker container.
1. The files need to be mapped into the container for processing by using a volume.
2. The output files need to be placed within the same directory that is mounted as a volume in order to be transfered back to the host.
3. Unless the `--rm` flag is passed the container will exist long after it is exited.

> Note: The following command uses the docker container while mapping all files within the current working directory into the docker container at `/data`. We also specify the output directory as `/data` and we tell docker to remove the container and it's data on exit.

#### Windows
```powershell
PS C:\nmapSubnetOnline> docker run --rm -v ${PWD}:/data nso -r /data/ranges.txt -n /data/possible_dc.xml -o /data
2024-05-29T17:32:34.540801+0000 | SUCCESS | nmapsubnetonline.nmapsubnetonline has started
2024-05-29T17:32:34.551113+0000 | INFO | Reading range file '/data/ranges.txt'
2024-05-29T17:32:34.582641+0000 | INFO | Reading nmap file '/data/possible_dc.xml'
2024-05-29T17:32:34.625612+0000 | INFO | Outputting results to csv file
```

#### Linux
> Note: The `-v` volume argument is changed here from the original PowerShell version.
```bash
user@cfeaca12f15c:~/$ docker run --rm -v $(pwd):/data nso -r /data/ranges.txt -n /data/possible_dc.xml -o /data
2024-05-29T17:32:34.540801+0000 | SUCCESS | nmapsubnetonline.nmapsubnetonline has started
2024-05-29T17:32:34.551113+0000 | INFO | Reading range file '/data/ranges.txt'
2024-05-29T17:32:34.582641+0000 | INFO | Reading nmap file '/data/possible_dc.xml'
2024-05-29T17:32:34.625612+0000 | INFO | Outputting results to csv file
```

## Input Files Example
### Nmap xml file
This file can either be a ping sweep or a port scan. The ping sweep will be faster but network devices may be blocking ICMP packets and a forced port scan may need to be done.

#### Nmap ping sweep command
```bash
nmap -sn -oX ranges 192.168.1.1/24
```

```bash
nmap -sn -iL ranges.txt -oX ranges
```


#### Nmap port scan command
```bash
nmap -Pn -n -oX ranges 192.168.1.1/24
```

```bash
nmap -Pn -n -iL ranges.txt -oX ranges
```

### Range file
Ranges provided to nmap for scanning. These subnets/CIDRs will be output as online or offline determined by a boolean variable within the CSV.
```
192.168.1.1/24
192.168.1.2/24
```