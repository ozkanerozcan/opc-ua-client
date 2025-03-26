<template>
  <q-page padding>
    <div class="row q-col-gutter-md">
      <!-- Connection Panel -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">OPC UA Connection</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model="serverUrl" label="Server URL" :disable="isConnected" />
            <div class="row q-gutter-sm q-mt-md">
              <q-btn v-if="!isConnected" class="full-width" color="primary" :loading="loadingEndpoints" @click="getEndpoints">
                Get Endpoints
              </q-btn>

              <q-btn v-if="isConnected" class="full-width" color="negative" :loading="loadingDisconnect" @click="disconnect">
                Disconnect
              </q-btn>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Data Operations Cards -->
      <template v-if="isConnected">
        <!-- Read/Write Operations Card -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="row items-center justify-between">
                <div class="text-h6">Read/Write Operations</div>
                <q-btn flat round icon="add" color="primary" @click="addNodeId" />
              </div>
            </q-card-section>
            <q-card-section>
              <div v-for="(node, index) in nodeIds" :key="index" class="row q-gutter-sm q-mb-sm">
                <q-input v-model="nodeIds[index]" label="Node ID" class="col" :disable="loadingRead || loadingWrite" />
                <q-input v-model="values[index]" label="Value" class="col" :disable="loadingRead || loadingWrite"/>
                <q-btn flat round color="negative" icon="cancel" @click="removeNodeId(index) " :disable="loadingRead || loadingWrite"
                       v-if="nodeIds.length > 1"/>
              </div>

              <div class="row q-mt-md">
                <div class="col-6 q-pa-xs">
                  <q-btn class="full-width" color="secondary" @click="writeValues" :loading="loadingWrite" :disable="loadingRead">
                    Write All
                  </q-btn>
                </div>
                <div class="col-6 q-pa-xs">
                  <q-btn class="full-width" color="primary" @click="readValues" :loading="loadingRead" :disable="loadingWrite">
                    Read All
                  </q-btn>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Register/Unregister Card -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6">Node Registration</div>
            </q-card-section>
            <q-card-section>
              <q-input v-model="registerNodeId" label="Node ID" class="q-mb-md" :disable="loadingUnregister || loadingRegister"/>
              <div class="row q-gutter-sm">
                <q-btn class="full-width" color="primary" @click="registerNode" :loading="loadingRegister" :disable="loadingUnregister">
                  Register
                </q-btn>
              </div>

              <!-- Active Subscriptions List -->
              <div class="q-mt-md" v-if="Object.keys(registeredNodes).length">
                <div class="text-subtitle2 q-mb-sm">Registered Nodes</div>
                <q-list bordered separator>
                  <q-item v-for="(sub, id) in registeredNodes" :key="id">
                    <q-item-section>
                      <q-item-label>{{ id }}</q-item-label>
                      <q-item-label caption>
                        {{ sub.node }}
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn flat round color="negative" icon="cancel"
                             @click="unregisterNode(id)" :loading="loadingUnregister" :disable="loadingRegister"/>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Subscription Card -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6">Subscription Management</div>
            </q-card-section>
            <q-card-section>
              <q-input v-model="subscribeNodeId" label="Node ID" class="q-mb-md" :disable="loadingSubscribe || loadingUnsubscribe"/>
              <q-input v-model="subscribeInterval" type="number" label="Interval (ms)" class="q-mb-md" :disable="loadingSubscribe || loadingUnsubscribe" />
              <div class="row q-gutter-sm q-mb-md">
                <q-btn class="full-width" color="primary" @click="subscribe" :loading="loadingSubscribe" :disable="loadingUnsubscribe">
                  Subscribe
                </q-btn>
              </div>

              <!-- Active Subscriptions List -->
              <div class="q-mt-md" v-if="Object.keys(activeSubscriptions).length">
                <div class="text-subtitle2 q-mb-sm">Active Subscriptions</div>
                <q-list bordered separator>
                  <q-item v-for="(sub, id) in activeSubscriptions" :key="id">
                    <q-item-section>
                      <q-item-label>{{ sub.node }}</q-item-label>
                      <q-item-label caption>
                        ID: {{ id }}
                      </q-item-label>
                      <q-item-label caption>Value: {{ subscribedNode[sub.node] || 'Waiting...' }}</q-item-label>
                      <q-item-label caption>
                        Interval: {{ sub.interval }}ms
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn flat round color="negative" icon="cancel"
                             @click="unsubscribe(id)" :loading="loadingUnsubscribe" :disable="loadingSubscribe"/>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </template>

    <q-dialog v-model="dialogEndpoints" full-width position="bottom">
      <q-card>
        <q-list>
          <template
            v-for="(endpoint, index) in endpoints"
            :key="index"
          >
            <q-item>
              <q-item-section>
                <q-item-label>{{ endpoint.endpoint_url }}</q-item-label>
                <q-item-label caption>
                  Policy: {{ endpoint.security_policy_uri.split('#')[1] }}
                </q-item-label>
                <q-item-label caption>
                  Security Mode: {{ endpoint.security_mode }}
                </q-item-label>
                <q-item-label caption>
                  Security Level: {{ endpoint.security_level }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-btn color="primary" :loading="loadingConnect && JSON.stringify(endpoint) === JSON.stringify(selectedEndpoint)" :disable="loadingConnect"  @click="beforeConnect(index)">
                  Connect
                </q-btn>
              </q-item-section>
            </q-item>
          </template>
        </q-list>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogAuth" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Authentication</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input dense v-model="username" autofocus label="Username"/>
          <q-input dense v-model="password" label="Password"/>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" @click="loadingConnect = false" v-close-popup />
          <q-btn flat label="Connect" :loading="loadingConnectAuth" @click="connect" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

const $q = useQuasar()

// State variables
const serverUrl = ref('opc.tcp://192.168.0.1:4840')
const loadingEndpoints = ref(false)
const dialogEndpoints = ref(false)
const loadingConnect = ref(false)
const loadingConnectAuth = ref(false)
const loadingDisconnect = ref(false)
const loadingRegister  = ref(false)
const loadingUnregister = ref(false)
const loadingSubscribe  = ref(false)
const loadingUnsubscribe = ref(false)
const loadingRead  = ref(false)
const loadingWrite  = ref(false)
const selectedEndpoint = ref(null)
const dialogAuth = ref(false)
const username = ref('')
const password = ref('')
const endpoints = ref([])
const isConnected = ref(false)
const activeSubscriptions = ref({})
const registeredNodes = ref({})
const subscribedNode = ref({})

// Add new reactive variables
const registerNodeId = ref('ns=3;s="Data_block_1"."drive1"."rLREAL"')
const subscribeNodeId = ref('ns=3;s="Data_block_1"."drive1"."rLREAL"')
const subscribeInterval = ref(1000)

// Add new reactive variables for multiple node IDs and values
const nodeIds = ref(['ns=3;s="Data_block_1"."drive1"."iINTEGER"'])
const values = ref([''])

// Notification helper
const showNotification = (message, color = 'positive') => {
  $q.notify({
    message,
    color,
    position: 'top-right',
    timeout: 2000
  })
}

// API endpoints configuration
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 5000
})

// Add response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ERR_NETWORK') {
      showNotification('Network error: Please check if the server is running', 'negative')
    }
    return Promise.reject(error)
  }
)

const getEndpoints = async () => {
  try {
    loadingEndpoints.value = true
    const response = await api.get('/connection/', {
      params: { url: serverUrl.value }
    })
    if (response.data.status === 'connected') {
      await disconnect() // Properly awaiting the function
    }
    endpoints.value = response.data.endpoints
    dialogEndpoints.value = true
  } catch (err) {
    endpoints.value = []
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingEndpoints.value = false
  }
}

const beforeConnect = async (index) => {
  loadingConnect.value = true
  selectedEndpoint.value = endpoints.value[index]
  if (Number(selectedEndpoint.value.security_level) != 0) {
    dialogAuth.value = true
  } else {
    await connect()
  }
}

const connect = async () => {

  try {
    loadingConnectAuth.value = true
    await api.post('/connection/', {
      endpoint: selectedEndpoint.value,
      username: username.value,
      password: password.value
    });
    showNotification('Connected successfully')
    isConnected.value = true
    dialogAuth.value = false
    dialogEndpoints.value = false
    loadingConnect.value = false
  } catch (err) {
    console.log(err)
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingConnectAuth.value = false
  }
}

const disconnect = async () => {
  try {
    loadingDisconnect.value = true
    await api.delete('/connection/')
    showNotification('Disconnected successfully')
    activeSubscriptions.value = {}
    isConnected.value = false
  } catch (err) {
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingDisconnect.value = false
  }
}

// Registered Node management
const getRegisteredNode = async () => {
  try {
    const response = await api.get('/register/')
    registeredNodes.value = response.data.registered_nodes
    console.log("activeSubscriptions.value : ", registeredNodes.value )
  } catch (err) {
    showNotification(err.response.data.message, 'negative')
  } finally {
    loading.value = false
  }
}

// Node registration
const registerNode = async () => {
  loadingRegister.value = true
  try {
    const response = await api.post('/register/', {
      node_ids: [registerNodeId.value]
    })
    registeredNodes.value = response.data.registered_nodes
    console.log(response)
    showNotification('Node registered successfully')
    await getRegisteredNode()
  } catch (err) {
    console.log(err)
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingRegister.value = false
  }
}

const unregisterNode = async (UnregisterNode) => {
  loadingUnregister.value = true
  try {
    await api.delete('/register/', {
      data: { node_ids: [UnregisterNode] }
    })
    showNotification('Node unregistered successfully')
    await getRegisteredNode()
  } catch (err) {
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingUnregister.value = false
  }
}

// Subscription management
const getSubscriptions = async () => {
  console.log("getSubscribed")
  try {
    const response = await api.get('/subscribe/')
    activeSubscriptions.value = response.data.active_subscriptions
    console.log("activeSubscriptions.value : ", activeSubscriptions.value )
  } catch (err) {
    showNotification(err.response.data.message, 'negative')
  } finally {
    loading.value = false
  }
}

// Update subscribe function to use the input values
const subscribe = async () => {
  loadingSubscribe.value = true
  try {
    const response = await api.post('/subscribe/', {
      node_id: subscribeNodeId.value,
      interval: subscribeInterval.value
    })
    showNotification('Subscription created successfully')
    await getSubscriptions()
  } catch (err) {
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingSubscribe.value = false
  }
}

const unsubscribe = async (subscriptionId) => {
  loadingUnsubscribe.value = true
  try {
    await api.delete('/subscribe/', {
      data: { subscription_id: subscriptionId }
    })
    showNotification('Unsubscribed successfully')
    await getSubscriptions()
  } catch (err) {
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingUnsubscribe.value = false
  }
}

// Add new methods for adding and removing node IDs
const addNodeId = () => {
  nodeIds.value.push('')
  values.value.push('')
}

const removeNodeId = (index) => {
  nodeIds.value.splice(index, 1)
  values.value.splice(index, 1)
}

// Modify readValues function to read multiple node IDs
const readValues = async () => {
  try {
    loadingRead.value = true
    const response = await api.post('/read-write/', {
      node_ids: nodeIds.value.filter(node => node) // Filter out empty nodes
    })
    // Handle the response data
    if (typeof response.data === 'object') {
      // If response is an object, convert to array of values
      values.value = Object.values(response.data)
    } else {
      // If response is a single value, wrap in array
      values.value = [response.data]
    }
  } catch (err) {
    console.log(err)
    showNotification(err.response?.data?.message || 'Error reading values', 'negative')
  } finally {
    loadingRead.value = false
  }
}

// Add new writeValues function
const writeValues = async () => {
  loadingWrite.value = true
  try {
    await api.put('/read-write/', {
      node_id: nodeIds.value,
      value: values.value
    })

    showNotification('Values written successfully')
    // Automatically read the values after writing
    await readValues()
  } catch (err) {
    console.log(err)
    showNotification(err.response.data.message, 'negative')
  } finally {
    loadingWrite.value = false
  }
}

let url = `ws://127.0.0.1:8000/ws/socket-server/`
const socket = new WebSocket(url);
console.log("url",url)
// When the WebSocket is open, you can start receiving updates
socket.onopen = function() {
    console.log("WebSocket connection established.");
};

// Handle incoming messages
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const timestamp = new Date().toLocaleString(); // Get current timestamp
    console.log(`[${timestamp}] Received real-time data: `, data);

    subscribedNode.value[data.node_id] = data.value;
};

// Handle any errors
socket.onerror = function(error) {
    console.log("WebSocket Error: ", error);
};

// When the WebSocket is closed
socket.onclose = function() {
    console.log("WebSocket connection closed.");
};

</script>
