from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .opc_ua_client import OPCUAClient
from opcua import ua

client = None

class OPCUAConnectView(APIView):

    def get(self, request):
        """
        Retrieve available endpoints from the OPC UA server.
        """
        global client
        url = request.query_params.get('url')
        if not url:
            return Response(
                {"message": "The 'url' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client_endpoint = OPCUAClient(url)
            endpoints = client_endpoint.get_endpoints()
            if not endpoints:
                return Response(
                    {"message": "No endpoints found for the provided URL."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"message": {str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            client_endpoint = None


        status_msg = "connected" if client else "disconnected"
        return Response({"status": status_msg, "endpoints": endpoints}, status=status.HTTP_200_OK)

    def post(self, request):
        """Connect to OPC UA server with selected endpoint"""
        global client
        endpoint = request.data.get('endpoint')
        username = request.data.get('username')
        password = request.data.get('password')
        print(endpoint, username, password)
        if client:
            return Response({
                "message": "Already connected to OPC UA server. Please disconnect first."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not endpoint:
            return Response({
                "message": "Endpoint selection is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if int(endpoint["security_level"]) != 0:
            if not username or not password:
                return Response({
                    "message": "Username and password are required for secure connection"
                }, status=status.HTTP_400_BAD_REQUEST)

        client = OPCUAClient(endpoint['endpoint_url'])
        client.configure(endpoint, username, password)
        try:
            # Connect with configured security
            client.connect()
        except Exception as e:
            client = None
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({"message": "Connected to OPC UA Server"}, status=status.HTTP_200_OK)

    def delete(self, request):
        """Disconnect from OPC UA server"""
        global client
        if not client:
            return Response({
                "message": "Not connected to OPC UA server"
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            client.disconnect()
            return Response({
                "message": "Disconnected from OPC UA Server"
            }, status=status.HTTP_200_OK)
        except ConnectionError as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            client = None

class OPCUADataView(APIView):
    def post(self, request):
        """Read value(s) from OPC UA node(s)"""
        node_ids = request.data.get('node_ids')
        if not node_ids:
            return Response({
                "message": "node_ids is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        try:

            values = client.read_value(node_ids)
            return Response(values, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """Write value(s) to OPC UA node(s)"""
        data = request.data
        if not data:
            return Response({
                "message": "data required"
            }, status=status.HTTP_400_BAD_REQUEST)
        node_id = data.get('node_id')
        value = data.get('value')
        print(node_id)
        print(value)
        if not node_id or value is None:
            return Response({
                "message": "node_id and value are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            client.write_value(node_id, value)
            return Response({
                "message": "Value(s) written successfully",
                "data": data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OPCUARegisterView(APIView):
    def get(self, request):
        """Get all active subscriptions"""
        global client
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Get active subscriptions directly from client
            serialized_nodes = {
                node_id: {
                    "node": str(reg_node.nodeid),  # Convert NodeId to string representation
                }
                for node_id, reg_node in client.registered_nodes.items()
            }
            return Response({
                "registered_nodes": serialized_nodes
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)}
            , status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        """Register nodes with OPC UA server"""
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if not data or 'node_ids' not in data:
            return Response({
                "message": "node_ids is required in request body"
            }, status=status.HTTP_400_BAD_REQUEST)
        node_ids = data['node_ids']
        if not isinstance(node_ids, list):
            node_ids = [node_ids]
        try:
            registered_nodes = client.register_nodes(node_ids)
            return Response({
                "message": "Nodes registered successfully",
                "registered_nodes": registered_nodes
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Unregister nodes from OPC UA server"""
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if not data or 'node_ids' not in data:
            return Response({
                "message": "node_ids is required in request body"
            }, status=status.HTTP_400_BAD_REQUEST)
        node_ids = data['node_ids']
        if not isinstance(node_ids, list):
            node_ids = [node_ids]
        try:
            client.unregister_nodes(node_ids)
            return Response({
                "message": "Nodes unregistered successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OPCUASubscribeView(APIView):
    def get(self, request):
        """Get all active subscriptions"""
        global client
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Get active subscriptions directly from client
            print("Deneme")
            print(client.subscriptions)
            print("Deneme2")
            active_subs = {}
            for sub_id, sub_data in client.subscriptions.items():
                print("sun_id", sub_id)
                print("sub_data", sub_data['subscription'])
                active_subs[sub_id] = {
                    'node': sub_data['node'],
                    'interval': sub_data['interval']
                }

            return Response({
                "active_subscriptions": active_subs
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)}
            , status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Subscribe to nodes"""
        if not client:
            return Response({
                "message": "Not connected to OPC UA server. Please connect first."
            }, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if not data or 'node_id' not in data:
            return Response({
                "message": "node_id is required in request body"
            }, status=status.HTTP_400_BAD_REQUEST)
        node_id = data['node_id']
        interval = int(data.get('interval', 500))  # Default 500ms
        try:
            subscription_id = client.subscribe(node_id, interval)
            return Response({
                "message": "Subscription created successfully",
                "subscription_id": subscription_id,
                "node": node_id,
                "interval": interval
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Unsubscribe from nodes"""
        try:
            if not client:
                return Response({
                    "message": "Not connected to OPC UA server. Please connect first."
                }, status=status.HTTP_400_BAD_REQUEST)

            data = request.data
            if not data or 'subscription_id' not in data:
                return Response({
                    "message": "subscription_id is required in request body"
                }, status=status.HTTP_400_BAD_REQUEST)

            subscription_id = data['subscription_id']
            client.unsubscribe(subscription_id)
            
            return Response({
                "message": "Unsubscribed successfully",
                "subscription_id": subscription_id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
