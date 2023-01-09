# flatTun

A successor of [wgtools-dev](https://github.com/TerenceLiu98/wgtools/tree/dev), where I fxxk up the structure the code.

Based on the my understanding of the SDN:
1. Control: control the network traffic, issue the configuration and monitor (both data plane and the network)
2. Receiver/User: follow the instruction from the controller

Thus, In this time, flatTun can be seen into two parts:

* Server-side: Flask-based with SQLite, trying to store the client information and subnet information.
  * Netspace: like zerotier, the user can create multiple subnet, and we call this subnet "Netspace"
  * Node: Node is the machine inside the netspace, it can be:
    * supernode: where it can contains Endpoint (Public IP)
    * normalnode: where it can only access other nodes via the supernode
* Client: python-based script, trying to help setup the wireguard interface and vxlan is corresponds to the "Node" definition
  * Login with the account
  * Get peer's infomation, based on the TCP requests
  * Parse the configuration
  * Start/Stop/Restart the wireguard interface, based on the `wg-quick`

## Trying To

* Background:
  * `VxLAN over Wireguard`, where `VxLAN` is the overlay and `Wireguard` as the underlay
  * `EVPN` as the control plane of the `VxLAN`
* Web and Client:
  * REST API everywhere -> frontend-backend separate
  * Token-based authentication and RBAC-based authorization
  * Clean & easy to use


*Issues, Pull Requests/Contributions are welcomed!* :)