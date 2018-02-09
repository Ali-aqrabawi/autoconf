from vlan_model import Vlan



while True :

    x = input("Enter option\n" + "1.add vlan\n" + "2.view vlans\n" + ":")

    if int(x) == 1 :
        id = input("enter vlan id")
        name = input("enter vlan name")
        description = input("enter vlan descriptoin")
        sessionVlan = Vlan()
        sessionVlan.id = id
        sessionVlan.name = name
        sessionVlan.description = description

        sessionVlan.AddVlan()
        print("##########################################################")

    elif int(x) == 2 :
        sessionVlan = Vlan()

        sessionVlan.ViewVlans()
        print("##########################################################")

    else :
        print("enter valid value please")
        print("##########################################################")
