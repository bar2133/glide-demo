# Telco OAuth Token Generation System

## Overview

The system consists of a broker service that acts as an intermediary between clients and multiple telco provider services, implementing intelligent routing based on Mobile Country Code (MCC) and Service Number (SN) prefixes.

## Deployment

### Prerequisites

-   Docker and Docker Compose

### Quick Start

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd glide-assignment
    ```

2. **Start all services**

    ```bash
    cd deployment
    docker-compose up -d
    ```

## Monitoring and Observability

The deployment includes comprehensive monitoring capabilities with Prometheus for metrics collection and Grafana for visualization and dashboards.

### Prometheus Configuration

**Access**: http://localhost:9090

Prometheus is configured to scrape metrics from all services every 5 seconds:

-   **Broker Service**: `http://broker-service:8001/metrics`
-   **Telco Orange Service**: `http://telco-orange-service:8080/metrics`
-   **Telco Vodafone Service**: `http://telco-vodafone-service:8081/metrics`

**Key Configuration Settings:**

-   Scrape interval: 5 seconds
-   Scrape timeout: 5 seconds
-   Evaluation interval: 8 seconds

**Available Metrics:**

-   HTTP request duration and count
-   Token generation performance
-   Service health and availability

### Grafana Dashboard

**Access**: http://localhost:3000

-   **Default Credentials**: admin/admin (change on first login)

**Pre-configured Features:**

-   **Data Source**: Automatically configured to connect to Prometheus
-   **Dashboard**: Pre-built dashboard with key system metrics
-   **Auto-refresh**: Dashboard updates every 5 seconds
-   **Alerting**: Ready for custom alert rules

**Dashboard Panels Include:**

-   Request rate and latency metrics
-   Token generation success/failure rates
-   Cache performance metrics
-   Service availability status

**Dashboard Management:**

-   Dashboards are provisioned automatically from `deployment/configs/grafana-dashboard.json`
-   Changes to dashboards persist and can be exported
-   Additional dashboards can be imported or created through the UI

### Monitoring Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Services  │───▶│ Prometheus  │───▶│   Grafana   │
│             │    │   :9090     │    │    :3000    │
│ - Broker    │    │             │    │             │
│ - Telco-*   │    │ Scrapes     │    │ Visualizes  │
│             │    │ Metrics     │    │ Dashboards  │
└─────────────┘    └─────────────┘    └─────────────┘
```

**Network Configuration:**

-   All monitoring services run on the `auth-network`
-   Services expose `/metrics` endpoints for Prometheus scraping
-   Grafana connects to Prometheus via internal Docker network

**Configuration Files:**

-   `deployment/configs/prometheus.yml`: Prometheus scraping configuration
-   `deployment/configs/grafana-datasources.yml`: Grafana data source setup
-   `deployment/configs/grafana-dashboard-config.yml`: Dashboard provisioning
-   `deployment/configs/grafana-dashboard.json`: Pre-built dashboard definition

### Metrics Collection

Each service exposes metrics at the `/metrics` endpoint in Prometheus format, including:

**HTTP Metrics:**

-   `http_requests_total`: Total HTTP requests by method, endpoint, and status
-   `http_request_duration_seconds`: Request duration histograms
-   `http_requests_in_progress`: Current number of HTTP requests being processed

**System Metrics:**

-   Process CPU and memory usage
-   Service startup and health metrics

## Services

### 1. Broker Service (Port 8001)

-   **Purpose**: Acts as an intelligent proxy between clients and telco services
-   **Key Features**:
    -   Two-phase token generation (telco + broker tokens)
    -   Intelligent routing based on MCC/SN prefix matching
    -   Redis caching for performance optimization
    -   Comprehensive error handling and timeout management
-   **Endpoint**: `POST /api/demo/token`

### 2. Telco Services

Multiple instances representing different telecom providers:

### 3. Common Components Library

Shared functionality across all services:

-   Data models and validation
-   JWT generation and validation
-   Redis caching utilities
-   Configuration management
-   Logging and utilities

## Data Flow

### Token Generation Process

1. **Client Request**: Client sends OAuth token request to broker service

    ```bash
    POST /api/demo/token?mcc=972&sn=050
    Content-Type: application/x-www-form-urlencoded

    auth_code=best_auth_code_123
    ```

2. **Prefix Matching**: Broker service uses telco directory to find matching telco service

    - Query: `972050` (MCC + SN)
    - Match: `972050` → Vodafone service
    - Route to: `http://telco-vodafone:8081`

3. **Telco Token Generation**: Forward request to telco service

    - Telco service validates authorization code
    - Generates JWT token with telco-specific claims
    - Returns token to broker service

4. **Broker Token Generation**: Broker service creates its own token

    - Embeds MCC, SN, and auth_code in JWT payload
    - Signs with broker-specific key
    - Sets appropriate expiration

5. **Response**: Return broker token to client

### Caching Strategy

Both telco and broker tokens are cached in Redis with automatic expiration:

-   **Cache Keys**: Structured format based on token type and telecom identifiers
-   **Expiration**: Aligned with JWT token expiration times
-   **Performance**: Reduces redundant token generation and telco service calls

## Configuration

### Telco Directory (YAML)

Located at `deployment/data/telco_data.yaml`:

```yaml
prefixes:
    97205:
        base_url: http://telco-orange:8080
        client_id: ORANGE_DEMO_ID
        client_secret: ORANGE_DEMO_SECRET
    972050:
        base_url: http://telco-vodafone:8081
        client_id: VF_DEMO_ID
        client_secret: VF_DEMO_SECRET
    4477:
        base_url: http://telco-vodafone:8081
        client_id: VF_UK_ID
        client_secret: VF_UK_SECRET
```

### Environment Configuration

Each service has its own environment file:

-   `deployment/envs/broker.env`: Broker service configuration
-   `deployment/envs/telco-orange.env`: Orange telco service configuration
-   `deployment/envs/telco-vodafone.env`: Vodafone telco service configuration

## API Documentation

### Broker Service API

#### POST /api/demo/token

Generate access token through broker service.

**Request:**

-   **Method**: POST
-   **URL**: `http://localhost:8001/api/demo/token`
-   **Query Parameters**:
    -   `mcc` (required): Mobile Country Code (1-3 digits)
    -   `sn` (required): Subscriber Number (variable length)
-   **Form Data**:
    -   `auth_code` (required): OAuth authorization code

**Example Request:**

```bash
curl -X POST "http://localhost:8001/api/demo/token?mcc=972&sn=0527464600" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "auth_code=best_auth_code_123"
```

**Success Response (200 OK):**

```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtY2MiOiI5NzIiLCJzbiI6IjA1MCIsImF1dGhfY29kZSI6ImJlc3RfYXV0aF9jb2RlXzEyMyIsImlhdCI6MTY0MjI0ODYwMCwiZXhwIjoxNjQyMjUyMjAwfQ.signature",
	"grant_type": "client_credentials",
	"iat": "2024-01-15T10:30:00Z",
	"exp": "2024-01-15T11:30:00Z"
}
```

**Error Responses:**

-   **400 Bad Request**: Telco data not found for MCC/SN combination
-   **401 Unauthorized**: Invalid authorization code
-   **503 Service Unavailable**: Telco service unreachable
-   **500 Internal Server Error**: Unexpected error

### Telco Service API

#### POST /api/demo/token

Generate telco-specific OAuth access token.

**Request:**

-   **Method**: POST
-   **URL**: `http://<telco-api>:<port>>/api/demo/token`
-   **Query Parameters**:
    -   `mcc` (required): Mobile Country Code
    -   `sn` (required): Service Number
-   **Form Data**:
    -   `auth_code` (required)

**Example Request:**

```bash
curl -X POST "http://localhost:8080/api/demo/token?mcc=972&sn=05" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "auth_code=best_auth_demo"
```

**Success Response (200 OK):**

```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"grant_type": "client_credentials",
	"iat": "2024-01-15T10:30:00Z",
	"exp": "2024-01-15T11:30:00Z"
}
```

**Error Responses:**

-   **401 Unauthorized**: Invalid authorization code

### Network Architecture

The system uses multiple Docker networks for service isolation:

-   **auth-network**: Communication between broker and telco services
-   **broker-network**: Broker service and its Redis instance
-   **telco-orange-network**: Orange telco service and its Redis instance
-   **telco-vodafone-network**: Vodafone telco service and its Redis instance

### Scaling

To add new telco providers:

1. **Create environment file**: `deployment/envs/telco-newprovider.env`
2. **Add service to docker-compose.yaml**:
    ```yaml
    telco-newprovider-service:
        build:
            context: ..
            dockerfile: telco-service/Dockerfile
        ports:
            - 8082:8082
        env_file:
            - ./envs/telco-newprovider.env
    ```
3. **Update telco directory**: Add new prefixes to `deployment/data/telco_data.yaml`
4. **Restart services**

### Code Quality

All code follows strict quality standards:

-   **PEP 8 compliance** with flake8
-   **Type hints** for all public APIs
-   **Google-style docstrings**
-   **Line length limit** of 120 characters

## Performance Analysis: Cache Impact on Service Communication Latency

### System Communication Patterns

The telco OAuth system implements a multi-tier architecture with the following communication flow:

1. **Client → Broker Service** (HTTP REST API)
2. **Broker Service → Redis Cache** (In-memory lookup)
3. **Broker Service → Telco Directory** (In-memory YAML lookup)
4. **Broker Service → Telco Service** (HTTP REST API)
5. **Telco Service → Redis Cache** (In-memory lookup)
6. **Telco Service → JWT Generation** (In-memory cryptographic operations)

### Latency Analysis: With Cache vs Without Cache

#### **Scenario 1: Cold Start (No Cache)**

| Component                      | Operation      | Details                       |
| ------------------------------ | -------------- | ----------------------------- |
| Client → Broker                | HTTP Request   | Network + FastAPI processing  |
| Broker → Telco Directory       | Prefix Lookup  | In-memory YAML data structure |
| Broker → Telco Service         | HTTP Forward   | Network + service processing  |
| Telco Service → JWT Generation | Token Creation | RSA/ECDSA signing operations  |
| Telco Service → Redis          | Cache Write    | Redis SETEX operation         |
| Broker → JWT Generation        | Broker Token   | Second JWT creation           |
| Broker → Redis                 | Cache Write    | Redis SETEX operation         |
| Response Processing            | Serialization  | JSON response formatting      |

**Key Bottlenecks:**

-   **Network Communication**: Broker ↔ Telco Service
-   **Cryptographic Operations**: JWT generation
-   **Redis Operations**: Cache writes

#### **Scenario 2: Cache Hit (Warm Cache)**

| Component           | Operation       | Details                      |
| ------------------- | --------------- | ---------------------------- |
| Client → Broker     | HTTP Request    | Network + FastAPI processing |
| Broker → Redis      | Cache Lookup    | Redis GET operation          |
| Response Processing | Deserialization | JSON parsing                 |

**Performance Gains:**

-   **Eliminated Network Calls**: No broker-to-telco communication
-   **Eliminated Cryptographic Operations**: No JWT generation
-   **Eliminated Directory Lookups**: No prefix matching required

### Cache Architecture Benefits

#### **1. Redis Instance Separation**

```yaml
# Each service has dedicated Redis instance
broker-redis: # Port 6379 - Broker tokens
telco-orange-redis: # Port 6379 - Orange tokens
telco-vodafone-redis: # Port 6380 - Vodafone tokens
```

**Advantages:**

-   **Isolation**: Service failures don't affect other caches
-   **Scalability**: Independent scaling per service
-   **Security**: Network-level separation via Docker networks

#### **3. Automatic Expiration Alignment**

```python
# Cache TTL matches JWT expiration
exp_sec = int((token.exp - token.iat).total_seconds())
await redis.setex(key, exp_sec, token_json)
```

**Benefits:**

-   **Consistency**: Cached tokens expire with actual tokens
-   **Memory Efficiency**: Automatic cleanup prevents memory leaks

### Performance Optimization Strategies

#### **1. Asynchronous Cache Operations**

```python
# Non-blocking cache writes
asyncio.create_task(save_token_to_redis(redis, telecom_dto, token))
```

**Impact**: Cache writes don't block response

#### **2. Cache-First Architecture**

```python
# Check cache before expensive operations
if redis and (cached_token := await redis.get_value(cache_key)):
    return cached_token  # Fast cache response vs full token generation
```

**Impact**: Significant latency reduction for repeated requests

## Monitoring and Logging (in production)

-   **Structured Logging**: All services use structured logging with appropriate levels and will collect by log exporter in OCP or any Loki style operator in K8S.
-   **Request Tracing**: Requests can be traced through the system using correlation IDs using traceing headers.
-   **Performance Metrics**: Token generation and cache performance metrics via prometheus.
-   **Health Checks**: All services expose health check endpoints.
