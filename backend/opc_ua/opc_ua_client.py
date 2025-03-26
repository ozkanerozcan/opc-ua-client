from opcua import Client, ua
import os
from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync

class SubHandler:
    """Handles subscription updates from OPC UA server."""
    def datachange_notification(self, node, val, data):
        print(f"📡 Data Change: Node {node}, New Value: {val}")
        
        # Send data to WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "opcua_updates",  # WebSocket group name
            {
                "type": "send_update",
                "data": json.dumps({
                    "node_id": str(node),
                    "value": val
                })
            }
        )

class OPCUAError(Exception):
    """Custom exception for OPC UA connection failures."""
    pass

class OPCUAClient:
    def __init__(self, url):
        self.client = Client(url)
        self.cert_path = os.path.join(os.path.dirname(__file__), 'certificates')
        self.registered_nodes = {}
        self.subscriptions = {} 

    def configure(self, endpoint, username, password):
        self.endpoint = endpoint
        self.username = username
        self.password = password

    
    def get_endpoints(self):
        """Get available endpoints from the OPC UA server."""
        try:
            endpoints = self.client.connect_and_get_server_endpoints()
            endpoints_info = []
            print(f"🔗 Found {len(endpoints)} available endpoints.")

            for endpoint in endpoints:
                endpoint_data = {
                    "endpoint_url": str(endpoint.EndpointUrl),
                    "security_mode": str(endpoint.SecurityMode),
                    "security_policy_uri": str(endpoint.SecurityPolicyUri),
                    "security_level": int(endpoint.SecurityLevel)
                }
                endpoints_info.append(endpoint_data)

            return endpoints_info
        except Exception as e:
            raise OPCUAError(f"Endpoints: {str(e)}")



    def connect(self):
        """Connect to OPC UA server"""
        if int(self.endpoint['security_level']) != 0:
            print("🔒 Connecting with security...")
            # Extract security policy and mode
            security_policy = self.endpoint['security_policy_uri'].split("#")[1]
            security_mode = int(self.endpoint['security_mode'])

            # Get absolute paths for certificates
            cert_file = os.path.join(self.cert_path, 'opcua_client_cert.pem')
            private_key_file = os.path.join(self.cert_path, 'opcua_client_key.pem')
            
            mode = "Sign" if security_mode == 2 else "SignAndEncrypt"

            security_string = f"{security_policy},{mode},{cert_file},{private_key_file}"
            
            self.client.set_security_string(security_string)
            self.client.application_uri = "urn:example.org:ozkanerozcan.com"

            self.client.set_user(self.username)
            self.client.set_password(self.password)
    
        try:
            self.client.connect()
            print("✅ OPC UA Connected successfully!")
        except Exception as e:
            raise OPCUAError(f"Connect: {str(e)}")

    def disconnect(self):
        """Disconnect from OPC UA server"""
        try:
            self.client.disconnect()
            self._connected = False
            print("🔌 OPC UA Disconnected.")
        except Exception as e:
            raise OPCUAError(f"Disconnect: {str(e)}")
        finally:
            self.client = None

    def read_value(self, node_id):
        """Read single or multiple node values"""
        try:
            nodes = [self.client.get_node(nid) for nid in node_id]
            values = self.client.get_values(nodes)
            return dict(zip(node_id, values))
        except Exception as e:
            raise OPCUAError(f"Read: {str(e)}")

    def write_value(self, node_id, value):
        """Write single or multiple values to nodes with automatic data type detection"""
        try:
            # Get node objects
            nodes = [self.client.get_node(nodeid) for nodeid in node_id]

            # Write multiple values with correct data types
            variant_values = []

            for idx, node in enumerate(nodes):
                variant_type = node.get_data_type_as_variant_type()
                if variant_type == ua.VariantType.Double:
                    variant_values.append(ua.DataValue(ua.Variant(float(value[idx]), variant_type)))
                elif variant_type == ua.VariantType.Int16:
                    variant_values.append(ua.DataValue(ua.Variant(int(value[idx]), variant_type)))
                elif variant_type == ua.VariantType.Boolean:
                    variant_values.append(ua.DataValue(ua.Variant(value[idx] == "True", variant_type)))
                else:
                    print(f"Unsupported data type for Node {node.nodeid}")

            # Write values
            self.client.set_values(nodes, variant_values)
            print("✅ Values written successfully!")
        except Exception as e:
            raise OPCUAError(f"Write: {str(e)}")

    def register_nodes(self, node_ids):
        """Register nodes with the server for optimized access"""
        try:
            print("Registering nodes...")
            nodes_to_register = [self.client.get_node(nid) for nid in node_ids]
            
            # Register the nodes
            registered_nodes = self.client.register_nodes(nodes_to_register)
            print('Registered Nodes Response: ', registered_nodes)
            print("Nodes registered successfully!")
            
            # Prepare a dictionary to store the registered nodes
            for idx, reg_node in enumerate(registered_nodes):
                self.registered_nodes[node_ids[idx]] = reg_node
            
            # Instead of printing `self.registered_nodes` directly, serialize it
            # Serialize the dictionary with meaningful data (e.g., NodeId, BrowseName):
            serialized_nodes = {
                node_id: {
                    "node": str(reg_node.nodeid),  # Convert NodeId to string representation
                }
                for node_id, reg_node in self.registered_nodes.items()
            }
            print("Serialized Registered Nodes: ", serialized_nodes)  # JSON-serializable data
            
            # Optionally return the serialized data
            return serialized_nodes
        except Exception as e:
            raise OPCUAError(f"Register: {str(e)}")

    def unregister_nodes(self, node_ids):
        """Unregister previously registered nodes"""
        try:
            print("Unregistering nodes...")
            registered_nodes = []
            for nid in node_ids:
                if nid in self.registered_nodes:
                    registered_nodes.append(self.registered_nodes[nid])
                    del self.registered_nodes[nid]
            
            if registered_nodes:
                self.client.unregister_nodes(registered_nodes)
                print("Nodes unregistered successfully!")
            
            print('REgistered Nodes After Delete', self.registered_nodes)
        except Exception as e:
            raise OPCUAError(f"Unregister: {str(e)}")

    def subscribe(self, node_id, interval=500):
        """Subscribe to nodes with specified interval (ms)"""
        try:
            print(f"Creating subscription with interval {interval}ms...")
            subscription = self.client.create_subscription(interval, SubHandler())
            
            node = self.client.get_node(node_id)

            handle = subscription.subscribe_data_change(node)

            print(f"Subscribed to node: {node}")

            # Store subscription and handles for later
            sub_id = str(subscription.subscription_id)
            self.subscriptions[sub_id] = {
                'subscription': subscription,
                'handle': handle,
                'node': node_id,
                'interval': interval  # Store the interval value
            }
            
            return sub_id

        except Exception as e:
            raise OPCUAError(f"Subscribe: {str(e)}")

    def unsubscribe(self, subscription_id):
        """Unsubscribe from nodes"""
        try:
            if subscription_id in self.subscriptions:
                print(f"Unsubscribing from subscription {subscription_id}...")
                sub_data = self.subscriptions[subscription_id]
                
                # Delete subscription
                sub_data['subscription'].delete()
                del self.subscriptions[subscription_id]
                print("Unsubscribed successfully!")
            else:
                raise ValueError(f"Subscription ID {subscription_id} not found")

        except Exception as e:
            raise OPCUAError(f"Unsubscribe: {str(e)}")

