import xml.etree.ElementTree as ET


def extract_hosts(nmap_file: str) -> list:
    hosts = []
    for event, elem in ET.iterparse(nmap_file, events=("end",)):
        if elem.tag == "host":
            saveHost = True
            for child in elem:
                if child.tag == "status":
                    if child.attrib["state"].lower() == "up":
                        saveHost = True
                if child.tag == "address" and saveHost:
                    hosts.append(child.attrib["addr"])
    return hosts
