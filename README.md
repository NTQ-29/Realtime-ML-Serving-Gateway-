# Real-Time Adaptive Model Serving Platform

A production-grade, real-time machine learning serving infrastructure designed to manage, scale, and dynamically route inference traffic across competing models behind an intelligent, low-latency API gateway. 

This platform leverages a **Feast-powered feature store** for sub-15ms online feature retrieval, an **asynchronous Kafka pipeline** to process real-time feature streaming, and a **Thompson Sampling Multi-Armed Bandit router** to optimize online model exploration versus exploitation. It explicitly addresses the foundational operational challenge that traditional ML architectures ignore: safely serving, comparing, and dynamically scaling multiple model variations concurrently in a high-throughput live environment.

---

## Performance & Architecture Metrics

The platform achieves predictable, high-throughput performance characteristics under simulated production loads:

| Metric | Target Baseline | Infrastructure Layer |
| :--- | :--- | :--- |
| **Feature Retrieval Latency (P99)** | 12ms | Redis Online Store |
| **End-to-End Prediction Latency (P95)** | 28ms | FastAPI Router Gateway |
| **System Throughput Capacity** | 3,400 req/s | 8 Kubernetes Pod Replicas |
| **Bandit Convergence Velocity** | ~2,000 requests | Thompson Sampling Engine |
| **Feature Freshness / Age** | < 30 seconds | Kafka ──► Redis Push Sync |
| **Cold Start Target** | < 5 seconds | Parameterized Container Pods |

---

##  System Core Capabilities

### 1. Multi-Strategy Intelligent Traffic Routing
The gateway abstracts execution logic from the client payload, supporting three core operational modes switchable via configuration definitions:
* **Thompson Sampling (Multi-Armed Bandit):** Maintains unique Beta probability distributions ($\alpha, \beta$) over each model's success rate. The system samples these distributions on every request to route traffic toward the statistically superior model while preserving efficient exploration.
* **Shadow Deployment Mode:** Emits incoming request vectors to all active model containers simultaneously. The gateway discards shadow payloads from the end-user response, logging performance data asynchronously to safely evaluate new models before activation.
* **Deterministic A/B Testing:** Allocates sticky traffic profiles based on an MD5 hash of the incoming `user_id` to guarantee consistent user experiences.

### 2. Dual-Headed Unified Feature Store
Built on top of **Feast**, the data tier explicitly separates state management to eliminate online-offline data skew:
* **Online Layer (Redis):** Acts as a high-performance, low-latency cache for live prediction querying.
* **Offline Layer (S3):** Houses historical batch aggregates utilized for training cycles and nightly materialization jobs.
* **Streaming Engine (Kafka):** Intercepts live app events (e.g., clickstreams) and pushes micro-window feature updates directly into Redis, bypassing batch latency boundaries.

### 3. Asymmetric Infrastructure Scaling
Every model variant (XGBoost, LightGBM, PyTorch Neural Network) operates inside isolated container instances managed via dedicated Kubernetes Helm charts. Resource allocations, memory parameters, and Horizontal Pod Autoscalers (HPA) are defined independently per model to handle structural compute imbalances seamlessly.

---

## Technical Stack Engine

* **Serving Frameworks:** FastAPI, Uvicorn, Pydantic
* **Data & Feature Infrastructure:** Feast, Redis (Online Store), Apache Kafka, AWS S3 (Offline Store)
* **Machine Learning Contexts:** XGBoost, LightGBM, PyTorch
* **Infrastructure & Orchestration:** Terraform, Kubernetes, Helm Charts, Amazon EKS, AWS ECR
* **Observability Matrix:** Prometheus, Grafana Dashboards
* **Automation Engineering:** GitHub Actions CI/CD

---

## Local Quickstart & Verification

### 1. Launch Local Infrastructure Stacks
Spin up the decoupled data and event layers using Docker Compose:
```bash

# Start local Kafka, Zookeeper, and Redis engines
docker-compose up -d

├── .github/workflows/    # CI/CD Pipeline automation scripts (Linting & Testing)
├── gateway/              # FastAPI Serving Gateway & Routing Strategy Engine
│   ├── app.py            # API Entry Point & Validation Schema
│   ├── router.py         # Deterministic A/B & Shadow router routing rules
│   └── bandit.py         # Thompson Sampling mathematical engine
├── features/             # Unified Feature Store definitions
│   ├── feature_store/    # Feast core configuration profiles & schemas
│   └── streaming/        # Kafka consumer workers syncing real-time features to Redis
├── models/               # Isolated Model Container Application frameworks
│   ├── xgboost/          # XGBoost service definitions and config maps
│   ├── lightgbm/         # LightGBM service configuration structures
│   └── neural/           # Neural network framework boundaries
├── infra/                # Infrastructure as Code provisioning configurations
│   └── environments/     # Environment parameter deployment files (dev.tfvars)
├── k8s/                  # Kubernetes Helm deployment manifests
│   ├── gateway/          # API Gateway deployment chart values
│   └── model-server/     # Asymmetric scaling and HPA chart values
├── tests/                # System automated integration test suites
├── docker-compose.yml    # Local multi-service infrastructure orchestrator
└── .gitignore            # Git exclusion mapping
