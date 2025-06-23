
## Pod Related commands
kubectl get pods 
kubectl describe pod <pod name>
kubectl get pod <pod-name> -o yaml > pod-definition.yaml
kubectl edit pod <pod-name> 
    To modify the properties of the pod, you can utilize the 

kubectl describe replicaset <replica set name>



## Create pods
kubectl run nginx --image=nginx



## Replica Set

kubectl get all
kubectl get deployments

## Namespces
 - kube-system
 - Default
 - kube-public

kubectl get namespaces/ns
kubectl get pods -n=<namespace_name>
---
# Configuration 
---
## Config Map
kubectl get configmaps
kubectl describe configmaps
kubectl create configmap \
    <config-name> --from-literal=<key>=<Value>

Ex : kubectl create configmap \
   app-config --from-literal=APP_COLOR=orange \
              --from-literal=DB_URL=https://db.service.postgres.com 


kubectl create configmap app-config --from-file=app_config.properties
or
kubectl create -f config-map.yaml

config-map.yaml:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
    name: app-config
data:
    APP_COLOR: orange
    DB_URL: https://db.service.postgres.com
    APP_MODE: dev
```

### Get the env from the config map
```yaml
apiVersion: v1
kind: Pod
metadata:
   name: blah
spec:
   containers:
   - env:
      - name: APP_COLOR
        valueFrom:
            configMapKeyRef:
               name: web-config-map
               key: APP_COLOR
```
## Secrets

imperative way:
kubectl create secret generic 
   <secret-name> --from-literal=<key>=<value>
kubectl create secret generic \
    app-secret --from-literal=DB_HOST=postgres


### Get data from secret 
```yaml
apiVersion: v1
kind: Secret
metadata:
   name: app-secret
data:
    DB_host: mysql #use echo -n 'mysql' | base64
    DB_User: root #use echo -n 'root' | base64
    DB_Password: password #use echo -n 'password' | base64
```            
kubectl create -f secret-data.yaml

kubectl get secrets 
kubectl describe secrets

kubectl get secret app-secret -o yaml --> put the values into yaml
echo -n 'cGFzd3Jk' | base64 --decode 

```yaml
apiVersion: v1
kind: Secret
metadata:
   name: app-secret
spec: 
   containers: 
   - name: simple-application-example
     envFrom:
       - secretRef:
           name: app-secret

data:
    DB_host: mysql #use echo -n 'mysql' | base64
    DB_User: root #use echo -n 'root' | base64
    DB_Password: password #use echo -n 'password' | base64

```
## Security Context
```yaml
apiVersion: v1
kind: Pod
metadata:
   name: web-pod
spec:
   secuityContext:
     runAsUser: 1000
   containers:
     - name: ubuntu
       image: ubuntu
       command: ['sleep', '3600']
```       
## Service Account

1. User Account: for users ex: users/admin/developer
2. Servie Account: for applications ex: promethus,jenkins

kubectl create servcieaccount dashboard-sa
kubectl get serviceaccount
kubectl describe serviceaccount dashboard-sa
kubectl describe secret <token-from-describe-of-dashboard-sa>

## Resource Requirements

* Scheduler is responsible for running the pod in particular node.
```yaml
apiVersionL v1
kind: pod
metadata:

spec:
  containers:
     - name : some-app
       ports:
          - containerPort 8080
       resources:
         requests:
           memory: "4Gi"/"256M"/ 
           cpu: 2
        limits:
           memory: "8Gi"
           cpu: 4
```

1 Cpu means:  
   - 1 AWS vCPU
   - 1 GCP Core
   - 1 Azure Core
   - 1 Hyperthread

## Taints and Tolerations
   Assiging what pods to run on what nodes. 

   Taints are placed on Nodes 
   Tolerant is placed on pods

   ### Taint addition
   kubectl taint nodes node-name key=value:taint-effect
   taint-effect: NoSchedule
                 PreferNoSchedule
                 NoExecute

   Ex: kubectl taint nodes node1 app=blue:NoSchedule
    
   ### Toleration addition
   in spec section of the yaml file
   tolerations"
   - key: "app"
     operator: "Equal"
     value: "blue"
     effect: "NoSchedule"

## Node Selectors
kubectl label nodes <node-name> <label-key>=<label-value>
kubectl label nodes node-1 size=Large

then in the pod configuration file of spec use 
nodeSelector:
   size: Large

## Node Affinity

  in spec section 
     affinity:
        nodeAffinity:

---          
# Multi Container Pods
---
### Side Car Pattern

A Sidecar container is a secondary container that runs alongside the main application container within the same Pod. Its primary purpose is to enhance or extend the functionality of the main application without modifying its code. Common use cases include logging, monitoring, proxying, and data synchronization.

Example: Application with a Logging Sidecar
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-logging-sidecar
spec:
  volumes:
    - name: shared-logs
      emptyDir: {}
  initContainers:
    - name: log-shipper
      image: alpine:latest
      command: ['sh', '-c', 'tail -F /opt/logs.txt']
      volumeMounts:
        - name: shared-logs
          mountPath: /opt
      restartPolicy: Always
  containers:
    - name: main-app
      image: alpine:latest
      command: ['sh', '-c', 'while true; do echo "logging" >> /opt/logs.txt; sleep 1; done']
      volumeMounts:
        - name: shared-logs
          mountPath: /opt
```   
   In this example, the log-shipper sidecar container tails the log file generated by the main-app container. The shared volume shared-logs facilitates communication between the two containers.

### Adapter Pattern

### Ambassador Pattern
 
### Init containers

 at times you may want to run a process that runs to completion in a container. For example a process that pulls a code or binary from a repository that will be used by the main web application. That is a task that will be run only one time when the pod is first created. Or a process that waits for an external service or database to be up before the actual application starts. That's where initContainers comes in.



An initContainer is configured in a pod like all other containers, except that it is specified inside a initContainers section, like this:


```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
  - name: myapp-container
    image: busybox:1.28
    command: ['sh', '-c', 'echo The app is running! && sleep 3600']
  initContainers:
  - name: init-myservice
    image: busybox
    command: ['sh', '-c', 'git clone <some-repository-that-will-be-used-by-application> ;']
```

When a POD is first created the initContainer is run, and the process in the initContainer must run to a completion before the real container hosting the application starts.

You can configure multiple such initContainers as well, like how we did for multi-pod containers. In that case each init container is run one at a time in sequential order.

If any of the initContainers fail to complete, Kubernetes restarts the Pod repeatedly until the Init Container succeeds.
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
  - name: myapp-container
    image: busybox:1.28
    command: ['sh', '-c', 'echo The app is running! && sleep 3600']
  initContainers:
  - name: init-myservice
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup myservice; do echo waiting for myservice; sleep 2; done;']
  - name: init-mydb
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup mydb; do echo waiting for mydb; sleep 2; done;']
```
---
# Observability
---
### Pod status 
  pending
  creating
  running

### Readiness Probe
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
  - name: myapp-container
    image: myapp-container

    readinessProbe
      httpGet:
         path: /api/ready
         port: 8080
    
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 8
```
Similar to this other reayness probe examples:

```yaml
    readinessProbe
      tcpSocket:
         port: 3306

    readinessProbe
      tcpSocket:
         port: 3306

    readinessProbe
      exec:
         command
          - cat
          - /app/is_ready

```
### Liveness Probe
Similar to ready, but more deeper before considering actual application works. 

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
  - name: myapp-container
    image: myapp-container

    readinessProbe
      httpGet:
         path: /api/ready
         port: 8080
    
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 8
    livenessProbe:
      httpGet:
        path: /api/healthy
        port: 8080
```
### Container Logging
kubectl logs -f <congainer-name>

### Monitoring and Debug Applications
Heapster/Metrics Server

get the metrics server from git hub
then 
kubectl create -f deploy/1.8+/ (what ever is the latest verison)

---

# Pod Design

## Labels, Selectors and Annotations

Real-world scenario: A service automatically routes traffic to all pods labeled app: frontend, while annotations store deployment notes, monitoring configs, and contact info that tools like Prometheus or kubectl can read without affecting pod selection.

**Labels** are key-value pairs attached to Kubernetes objects for identification and organization. They're used by selectors to group and filter resources. Labels are meant for identifying objects and are queryable.
```yaml
  yamlmetadata:
    labels:
      app: nginx
      version: v1.2
      environment: production
```yaml
**Selectors** are queries that use labels to identify and group objects. They're used by controllers, services, and other resources to find their target objects. Selectors enable loose coupling between resources.
```yaml
selector:
  matchLabels:
    app: nginx
    environment: production
```
**Annotations** are key-value pairs that store non-identifying metadata about objects. They hold descriptive information, configuration data, or metadata used by tools and libraries. Unlike labels, annotations aren't used for selection.
yaml
```yaml
metadata:
  annotations:
    description: "Frontend web server"
    last-updated: "2024-01-15"
    deployment.kubernetes.io/revision: "3"
```
## Rolling Updates & Rollback Deployments

kubectl describe deployment <deployment-name>

kubectl rollout status deployment/myapp-deployment

if we have deployment file then 
kubectl apply -f deployment-definion.yaml. 
or
kubectl set image deployment/myapp-deployment nginx-container=nginx:1.9.1


### Recreate strategy

### Rolling Update (Default deployment strategy)

to undo a rollout
kubect rollout undo deployment/myapp-deployment
#### Commands
create:
kubectl create -f deployment-definition.yml
get:
kubect get deployments
update:
kubectl appl -f deployment-definition.yml
kubectl set image deployment/myapp-deployment nginx-container=nginx:1.9.1
status:
kubectl status deployment/myapp-deployment
kubectl rollout history deployment/myapp-deployment
rollback:
kubectl rollout undo deployment/myapp-deployment

### Blue Green Strategy
blue: old version and 
green: new version 
once all thigns are up : traffic will be moved .
its done in service. All the serviec is sent to version:1
Then put the new deployment label to version 2. 
do all tests. 
themove the 

service defn:
_____________
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
     version: v1
```
my-app-blue.yaml
_______________________
```yaml
apiVersion: v1
kind: Deployment
metadata:
  name: myapp-blue
  labels:
     app: myapp
     type: front-end

spec:
  template:
    metadata:
      name: myapp-pod
      labels:
         version: v1 
    spec:
      containder:
        - name: app-container
          image: myapp-image:1.0
  replicas:5             
  selector:
    matchLabels:
      version: v1
```
my-app-green.yaml
_______________________
```yaml
apiVersion: v1
kind: Deployment
metadata:
  name: myapp-GREEN<===== change here
  labels:
     app: myapp
     type: front-end

spec:
  template:
    metadata:
      name: myapp-pod
      labels:
         version: v2 
    spec:
      containder:
        - name: app-container
          image: myapp-image:1.0
  replicas:5             
  selector:
    matchLabels:
      version: v2<===== change here
```
to rouute the traffic chagne the version 2 in service. 
service defn:
_____________
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
     version: v2 <===== change here
```
### Canary Strategy

Small amount of the traffic is routed first to new versions, then all are sent here. 

service defn:
_____________
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
     app: front-end
```
my-app-primary.yaml
_______________________
```yaml
apiVersion: v1
kind: Deployment
metadata:
  name: myapp-blue
  labels:
     app: myapp
     type: front-end

spec:
  template:
    metadata:
      name: myapp-pod
      labels:
         version: v1 
    spec:
      containder:
        - name: app-container
          image: myapp-image:1.0
  replicas:5             
  selector:
    matchLabels:
      version: v1
```
my-app-canary.yaml
_______________________
```yaml
apiVersion: v1
kind: Deployment
metadata:
  name: myapp-CANARY<===== change here
  labels:
     app: myapp
     type: front-end

spec:
  template:
    metadata:
      name: myapp-pod
      labels:
         version: v2 
         app: front-end
    spec:
      containder:
        - name: app-container
          image: myapp-image:1.0
  replicas:1            <===== change here 
  selector:
    matchLabels:
      version: v2
```
to rouute the traffic chagne the version 2 in service. 
service defn:
_____________
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
     app: front-end <===== NOTE, no change here
```

## Jobs and CronJobs


### Jobs

POD definition
_________________
```yaml
apiVersion: v1
kind: Pod
metadata: 
   name: math-pod 
spec:
   containers:
     - nam: math-add
       imag: ubuntu
       command: ['expr', '3', '+', '2']
   restartPolicy: Never
```
JOB definition
_________________
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: math-add-job
spec:
  template:
    spec:
      containers:
        -name: math-add
        image: ubuntu
        command: ['expr', '3', '+', '2']
      restarPolicy: Never
```

To start the job
```console
kubectl create -f job-definition.yaml
```

To delete the job
```console
kubectl delete job math-add-job
```


### Cronjobs


CRON JOB definition
_________________
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: reporting-cron-job
spec:
  schedule: "*/1 * * * *"
  spec:
    template:
      spec:
        containers:
          -name: reporting-tool
          image: reporting-tool
          
        restarPolicy: Never
```

To start the job
```console
kubectl create -f cron-job-definition.yaml

kubectl get cronjob
```

# Services

## Node Port
┌─────────────────────────────────────────────────────┐
│                External Traffic                     │
└─────────────────┬───────────────────────────────────┘
                  │ :30080
┌─────────────────▼──────────────────────────────────┐
│           Kubernetes Cluster                       │
│                                                    │
│  ┌─────────┐    ┌─────────────────┐                │
│  │ Node 1  │    │   NodePort      │                │
│  │:30080   │◄───┤   Service       │                │
│  └─────────┘    │   ClusterIP:80  │                │
│                 │   NodePort:30080│                │
│  ┌─────────┐    │                 │   ┌─────────┐  │
│  │ Node 2  │◄───┤                 │──►│  Pod A  │  │
│  │:30080   │    │                 │   │ :8080   │  │
│  └─────────┘    └─────────────────┘   └─────────┘  │
│                                                    │
│                                       ┌─────────┐  │
│                                       │  Pod B  │  │
│                                       │ :8080   │  │
│                                       └─────────┘  │
└────────────────────────────────────────────────────┘
Summary: Exposes service on each node's IP at a static port (30000-32767 range).
Use Cases:

Development and testing environments
Small applications with limited traffic
When you don't have a load balancer
Quick external access without complex setup

Example: A web application in a development environment where you need external access but don't want to configure a load balancer.

```yaml

```
## Cluster IP
┌─────────────────────────────────────┐
│           Kubernetes Cluster        │
│                                     │
│  ┌─────────┐    ┌─────────────────┐ │
│  │  Pod A  │    │   ClusterIP     │ │
│  │ :8080   │◄───┤   Service       │ │
│  └─────────┘    │   10.96.1.100   │ │
│                 │   :80           │ │
│  ┌─────────┐    │                 │ │
│  │  Pod B  │◄───┤                 │ │
│  │ :8080   │    └─────────────────┘ │
│  └─────────┘                        │
└─────────────────────────────────────┘
Summary: Exposes service only within the cluster using an internal IP address.
Use Cases:

Internal microservice communication
Database services accessed only by applications within cluster
Backend APIs not meant for external access
Inter-pod communication within the same cluster

Example: A database service that should only be accessible by your application pods.

```yaml

```

## LoadBalancer



# Ingress Networking

Think like its a layer 7 load balancer  built in to k8 cluster 
it can be configured with native kubernetes primitive like any other object. 
With SSL and load balancing. 

## Ingress Controller
 you should deploy one
    nginx, contour, haproxy, traefik, istio
### Deployment
### Service
### ConfigMap
### Auth

## Configuration


# State Persistence

## Volumes 
 
 ```yaml
 volumes:
 - name: data-volume
   hostPath:
      path: /data
      type: Directory
   awsElasticBlockStore:
      volumeID: <volume-id>
      fsType: ext4
 ```

 ## Persistant Volumes

 ```yaml
 apiVersion: v1
 kind: PersistentVolume
 metadata:
  name: pv-vol1
 spec:
   accessModes:
      - ReadWriteOnce
   capacity:
      storage: 1Gi
   hostPath:
      path: /tmp/data
```

```command
kubectl get persistentvolume
```
 ## Persistant Volume Claims
    These are separate objects from the PV. When PV is created, claims are requested by the pds. 

 ```yaml
 apiVersion: v1
 kind: PersistentVolumeClaim
 metadata:
  name: myclaim
 spec:
   accessModes:
      - ReadWriteOnce
   resources:
      requests
        storage: 500Mi
```
   
```command
kubectl get persistentvolumeclaim

```
### Using PVCs in Pods

Once you create a PVC use it in a POD definition file by specifying the PVC Claim name under persistentVolumeClaim section in the volumes section like this:

 ```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: myfrontend
      image: nginx
      volumeMounts:
      - mountPath: "/var/www/html"
        name: mypd
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: myclaim
```

## Storage Classes
Dynamic storage provisioning

PV Definition

 ```yaml
 apiVersion: v1
 kind: PersistentVolume
 metadata:
  name: pv-vol1
 spec:
   accessModes:
      - ReadWriteOnce
   capacity:
      storage: 1Gi
   gcePersistentDisk:   <== these are specific to the provisioner, look for documentation
      pdName: pd-disk
      fsType: ext4

```
Corresponding Storage Class Definition

```yaml
 apiVersion: storage.k8s.io/v1
 kind: StorageClass
 metadata:
  name: google-storage
 provisioner; Kubernetes.io/gce-pd

 spec:
   accessModes:
      - ReadWriteOnce
   capacity:
      storage: 1Gi
   gcePersistentDisk:
      pdName: pd-disk
      fsType: ext4

```
Corresponding PVC claim

 ```yaml
 apiVersion: v1
 kind: PersistentVolumeClaim
 metadata:
  name: myclaim
 spec:
   accessModes:
      - ReadWriteOnce
   storageClassName: google-storage

   resources:
      requests
        storage: 500Mi
```

Corresponding POD definition
 ```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: myfrontend
      image: nginx
      volumeMounts:
      - mountPath: "/var/www/html"
        name: mypd
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: myclaim
```
## Stateful Set
ex: When you want replication of db, you want master to come first then second third etc.
Also the first name is always <service>-0, its better to know the single first copy


Ordered launch and reverse order take down. 

```yaml
apiversion: apps/v1
kind: StatefulSet
metadata
 name: mysql
 labels:
  app: mysql 

```

# Security

# Helm Fundamentals
Some times referred to as package manager for kubernetes.

artifacthub.io for the helm chart repository

```command
helm install [release-name] [chart-name]

helm install release-1 binami/wordpress

```

# Kustomize



