from netmiko import ConnectHandler
import argparse
import json
import sys
import re
from prettytable import PrettyTable

DEVICES =[]
JSON_DATA =''


class Connector():
    def __init__(self, dev_details):
        self.dev_details = dev_details
        try:
            self.net_Connect = ConnectHandler(**self.dev_details)
            print("Connection Successful")
        except:
            print("Unable to reach the device, Please check the connection and try again")
            sys.exit(1)
    def getConnHandler(self):
        return self.net_Connect


class L3_extractor():
    def __init__(self, ConnHandler):
        self.ConnHandler = ConnHandler
        self.IP_Intr_list = {}
        self.ConnHandler.enable()
        self.get_details(1,"Show ip int br")
        print(self.get_details(2,"Show ip ospf int br"))
        #bgp =  self.get_details(3,"show ip bgp summary")
        self.get_devices()

    def get_details(self,num,cmd):
        print("Extracting details for \"{}\" now".format(cmd))
        output = self.ConnHandler.send_command(cmd)
        if not output:
            print("There are no Details found")
            return
        if num == 1:
            output = output.split("\n")[1:]
            tab = PrettyTable()
            tab.field_names = ["Interface", "IPs"]
            for each in output:
                key = each.split()[0]
                if "FastEthernet" in key:
                    key = key.replace("FastEthernet", "Fa")
                elif "GigaEthernet" in key:
                    key = key.replace("GigaEthernet", "Gi")
                self.IP_Intr_list[key] = each.split()[1]
                tab.add_row([key, each.split()[1]])
            print(tab)
        else:
            return output

    def get_devices(self):
        interestedLinks = {}
        cdp = self.get_details(4, "show cdp neighbor")
        cdpLines = cdp.split("\n")
        for each in cdpLines:
            if "0/0" not in each and re.search(r'./.',each):
                each = each.replace("Fas ","Fa") #replacing to have a consistent interface name
                devName = each.split()[0].split(".")[0]
                devLink = each.split()[1]
                interestedLinks[devLink] = devName

        print(interestedLinks)
        




if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',action='store',type=str)
    args = parser.parse_args()
    print("FileName = {}".format(args.filename))

    with open(args.filename,'r') as fh:
        JSON_DATA = json.load(fh)
        for each in JSON_DATA:
            DEVICES.append(each)
        for each in JSON_DATA.keys():
            print(each)

    print(DEVICES)
    for each in DEVICES:
        print("Establishing connection for {}".format(each))
        ConnHandler = Connector(JSON_DATA[each])
        print("Getting L3 Details")
        L3_details = L3_extractor(ConnHandler.net_Connect)







