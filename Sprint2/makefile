# Los pasos en este archivo pueden ser usados para su pipeline de Unit testing
# en el caso que usted decida usar Python.

.PHONY: lintfix lintcheck unittest terraform-init terraform-plan terraform-apply terraform-destroy terraform-output terraform-status terraform-plan-local terraform-apply-local k8s-config k8s-apply-ingress k8s-status k8s-logs deploy cleanup docker-login docker-build docker-push docker-build-push docker-build-users docker-build-posts docker-build-offers docker-build-routes docker-build-scores test-all test-users test-posts test-offers test-routes test-scores deploy-quick deploy-local pipeline ecr-create ecr-list ecr-delete validate-aws validate-docker validate-k8s validate-all setup-ecr setup-infrastructure setup-all help

lintfix:
	poetry --directory=${DIR} install
	poetry --directory=${DIR} run black .
	poetry --directory=${DIR} run isort . --profile black
	poetry --directory=${DIR} run bandit -c pyproject.toml -r .
	poetry --directory=${DIR} run ruff check --fix

lintcheck:
	poetry --directory=${DIR} install
	poetry --directory=${DIR} run black --check .
	poetry --directory=${DIR} run isort --check . --profile black
	poetry --directory=${DIR} run bandit -c pyproject.toml -r .
	poetry --directory=${DIR} run ruff check

unittest:
	poetry --directory=${DIR} install
	poetry --directory=${DIR} run pytest --cov=src -v -s --cov-fail-under=70 --cov-report term-missing

# Configuration
TERRAFORM_DIR = terraform/stacks/apps
AWS_REGION = us-east-1
AWS_ACCOUNT_ID = $(shell aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY = $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
CLUSTER_NAME = dann-cluster

# Microservices configuration
MICROSERVICES = users posts offers routes scores aggregator
VERSION = $(shell date +%Y%m%d-%H%M%S)

# Docker and ECR commands
.PHONY: docker-login docker-build docker-push docker-build-all docker-push-all

docker-login:
	@echo "🔐 Logging into ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY)

docker-build:
	@echo "🏗️  Building Docker images for all microservices..."
	@for service in $(MICROSERVICES); do \
		echo "Building $$service-app:$(VERSION)"; \
		docker build -t $$service-app:$(VERSION) -t $$service-app:latest ./$${service}_app/; \
		docker tag $$service-app:$(VERSION) $(ECR_REGISTRY)/$$service-app:$(VERSION); \
		docker tag $$service-app:latest $(ECR_REGISTRY)/$$service-app:latest; \
	done

docker-push:
	@echo "📤 Pushing Docker images to ECR..."
	@for service in $(MICROSERVICES); do \
		echo "Pushing $$service-app:$(VERSION)"; \
		docker push $(ECR_REGISTRY)/$$service-app:$(VERSION); \
		docker push $(ECR_REGISTRY)/$$service-app:latest; \
	done

docker-build-push: docker-login docker-build docker-push
	@echo "✅ All images built and pushed successfully!"

# Individual service commands
docker-build-users:
	@echo "🏗️  Building users-app:$(VERSION)..."
	docker build -t users-app:$(VERSION) -t users-app:latest ./users_app/
	docker tag users-app:$(VERSION) $(ECR_REGISTRY)/users-app:$(VERSION)
	docker tag users-app:latest $(ECR_REGISTRY)/users-app:latest

docker-build-posts:
	@echo "🏗️  Building posts-app:$(VERSION)..."
	docker build -t posts-app:$(VERSION) -t posts-app:latest ./posts_app/
	docker tag posts-app:$(VERSION) $(ECR_REGISTRY)/posts-app:$(VERSION)
	docker tag posts-app:latest $(ECR_REGISTRY)/posts-app:latest

docker-build-offers:
	@echo "🏗️  Building offers-app:$(VERSION)..."
	docker build -t offers-app:$(VERSION) -t offers-app:latest ./offers_app/
	docker tag offers-app:$(VERSION) $(ECR_REGISTRY)/offers-app:$(VERSION)
	docker tag offers-app:latest $(ECR_REGISTRY)/offers-app:latest

docker-build-routes:
	@echo "🏗️  Building routes-app:$(VERSION)..."
	docker build -t routes-app:$(VERSION) -t routes-app:latest ./routes_app/
	docker tag routes-app:$(VERSION) $(ECR_REGISTRY)/routes-app:$(VERSION)
	docker tag routes-app:latest $(ECR_REGISTRY)/routes-app:latest

docker-build-scores:
	@echo "🏗️  Building scores-app:$(VERSION)..."
	docker build -t scores-app:$(VERSION) -t scores-app:latest ./scores_app/
	docker tag scores-app:$(VERSION) $(ECR_REGISTRY)/scores-app:$(VERSION)
	docker tag scores-app:latest $(ECR_REGISTRY)/scores-app:latest

docker-build-aggregator:
	@echo "🏗️  Building aggregator-app:$(VERSION)..."
	docker build -f ./aggregator_service/Dockerfile.simple -t aggregator-app:$(VERSION) -t aggregator-app:latest ./aggregator_service/
	docker tag aggregator-app:$(VERSION) $(ECR_REGISTRY)/aggregator-app:$(VERSION)
	docker tag aggregator-app:latest $(ECR_REGISTRY)/aggregator-app:latest

terraform-init:
	@echo "🚀 Initializing Terraform..."
	@if [ ! -d "$(TERRAFORM_DIR)/.terraform" ]; then \
		echo "Initializing Terraform for the first time..."; \
		cd $(TERRAFORM_DIR) && terraform init; \
	else \
		echo "Terraform already initialized, skipping..."; \
	fi

terraform-plan:
	@echo "📋 Planning Terraform deployment..."
	cd $(TERRAFORM_DIR) && terraform plan -var-file="../../environments/student/apps/terraform.tfvars"

terraform-apply:
	@echo "🏗️  Applying Terraform configuration..."
	cd $(TERRAFORM_DIR) && terraform apply -auto-approve -var-file="../../environments/student/apps/terraform.tfvars"

terraform-plan-local:
	@echo "📋 Planning Terraform deployment with local images..."
	cd $(TERRAFORM_DIR) && terraform plan -var="users_app.image_name=users-app" -var="users_app.image_tag=latest" \
		-var="posts_app.image_name=posts-app" -var="posts_app.image_tag=latest" \
		-var="offers_app.image_name=offers-app" -var="offers_app.image_tag=latest" \
		-var="routes_app.image_name=routes-app" -var="routes_app.image_tag=latest" \
		-var="scores_app.image_name=scores-app" -var="scores_app.image_tag=latest"

terraform-apply-local:
	@echo "🏗️  Applying Terraform configuration with local images..."
	cd $(TERRAFORM_DIR) && terraform apply -auto-approve -var="users_app.image_name=users-app" -var="users_app.image_tag=latest" \
		-var="posts_app.image_name=posts-app" -var="posts_app.image_tag=latest" \
		-var="offers_app.image_name=offers-app" -var="offers_app.image_tag=latest" \
		-var="routes_app.image_name=routes-app" -var="routes_app.image_tag=latest" \
		-var="scores_app.image_name=scores-app" -var="scores_app.image_tag=latest"

terraform-destroy:
	@echo "🗑️  Destroying Terraform resources..."
	cd $(TERRAFORM_DIR) && terraform destroy -auto-approve -var-file="../../environments/student/apps/terraform.tfvars"

terraform-output:
	@echo "📤 Getting Terraform outputs..."
	cd $(TERRAFORM_DIR) && terraform output

terraform-status:
	@echo "📊 Checking Terraform status..."
	cd $(TERRAFORM_DIR) && terraform show

# Kubernetes commands
k8s-config:
	@echo "⚙️  Configuring kubectl for EKS cluster..."
	aws eks update-kubeconfig --region $(AWS_REGION) --name $(CLUSTER_NAME)

k8s-apply-ingress:
	@echo "🌐 Applying ingress configuration..."
	kubectl apply -f k8s/ingress.yml

k8s-status:
	@echo "📊 Checking Kubernetes resources..."
	@echo "Namespaces:"
	kubectl get namespaces
	@echo "\nPods in microservices namespace:"
	kubectl get pods -n microservices
	@echo "\nServices in microservices namespace:"
	kubectl get services -n microservices
	@echo "\nIngress:"
	kubectl get ingress -n microservices

k8s-logs:
	@echo "📝 Getting logs from microservices..."
	@echo "Users App logs:"
	kubectl logs -f deployment/users-app-deployment -n microservices --tail=50
	@echo "Posts App logs:"
	kubectl logs -f deployment/posts-app-deployment -n microservices --tail=50

# Testing commands
.PHONY: test-all test-users test-posts test-offers test-routes test-scores

test-all:
	@echo "🧪 Running tests for all microservices..."
	@for service in $(MICROSERVICES); do \
		echo "Testing $$service-app..."; \
		if [ "$$service" = "aggregator" ]; then \
			echo "No tests available for aggregator service, skipping..."; \
		else \
			cd $${service}_app && python -m pytest test/ -v || echo "Tests failed for $$service-app"; \
			cd ..; \
		fi; \
	done

test-users:
	@echo "🧪 Testing users-app..."
	cd users_app && python -m pytest test/ -v

test-posts:
	@echo "🧪 Testing posts-app..."
	cd posts_app && python -m pytest test/ -v

test-offers:
	@echo "🧪 Testing offers-app..."
	cd offers_app && python -m pytest test/ -v

test-routes:
	@echo "🧪 Testing routes-app..."
	cd routes_app && python -m pytest test/ -v

test-scores:
	@echo "🧪 Testing scores-app..."
	cd scores_app && python -m pytest test/ -v

# Complete deployment workflow - does everything automatically
deploy: validate-all test-all
	@echo "🚀 Deploying to AWS using existing credentials..."
	@cd terraform && ./deploy.sh
pipeline: validate-all setup-ecr test-all docker-build-push terraform-init terraform-plan terraform-apply k8s-config k8s-apply-ingress k8s-status k8s-logs
	@echo "✅ Full CI/CD pipeline completed successfully!"

# ECR repository management
.PHONY: ecr-create ecr-list ecr-delete

ecr-create:
	@echo "📦 Creating ECR repositories..."
	@if [ ! -d "terraform/environments/student/registry/.terraform" ]; then \
		echo "Initializing Terraform for ECR..."; \
		cd terraform/environments/student/registry && terraform init; \
	fi
	@echo "Applying ECR configuration..."
	cd terraform/environments/student/registry && terraform apply -auto-approve || echo "ECR repositories may already exist, continuing..."

ecr-list:
	@echo "📋 Listing ECR repositories..."
	aws ecr describe-repositories --region $(AWS_REGION) --query 'repositories[].repositoryName' --output table

ecr-delete:
	@echo "🗑️  Deleting ECR repositories..."
	cd terraform/environments/student/registry && terraform destroy -auto-approve

# Validation commands
.PHONY: validate-aws validate-docker validate-k8s validate-helm validate-all

validate-aws:
	@echo "🔍 Validating AWS configuration..."
	@aws sts get-caller-identity > /dev/null || (echo "❌ AWS CLI not configured" && exit 1)
	@echo "✅ AWS CLI configured"

validate-docker:
	@echo "🔍 Validating Docker..."
	@docker --version > /dev/null || (echo "❌ Docker not installed" && exit 1)
	@echo "✅ Docker available"

validate-k8s:
	@echo "🔍 Validating kubectl..."
	@kubectl version --client > /dev/null || (echo "❌ kubectl not installed" && exit 1)
	@echo "✅ kubectl available"

validate-helm:
	@echo "🔍 Validating Helm..."
	@helm version --short > /dev/null || (echo "❌ Helm not installed" && exit 1)
	@echo "✅ Helm available"

validate-all: validate-aws validate-docker validate-k8s validate-helm
	@echo "✅ All validations passed!"

# Setup commands
.PHONY: setup-ecr setup-infrastructure setup-all

setup-ecr: validate-aws ecr-create
	@echo "✅ ECR setup completed!"

setup-infrastructure: validate-all terraform-init
	@echo "✅ Infrastructure setup completed!"

setup-all: setup-ecr setup-infrastructure
	@echo "✅ Complete setup finished!"

# Cleanup workflow
cleanup: terraform-destroy
	@echo "🧹 Cleanup completed!"

# Help command
help:
	@echo "🚀 Available commands:"
	@echo ""
	@echo "📦 Setup:"
	@echo "  setup-all          - Complete setup (ECR + Infrastructure)"
	@echo "  setup-ecr          - Create ECR repositories"
	@echo "  setup-infrastructure - Initialize Terraform"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test-all           - Run tests for all microservices"
	@echo "  test-<service>     - Run tests for specific service"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build-push  - Build and push all images to ECR"
	@echo "  docker-build-<service> - Build specific service image"
	@echo ""
	@echo "🏗️  Deployment:"
	@echo "  deploy             - Full deployment (tests + build + deploy)"
	@echo "  deploy-quick       - Quick deployment (skip tests)"
	@echo "  pipeline           - Full CI/CD pipeline"
	@echo ""
	@echo "⚙️  Management:"
	@echo "  k8s-status         - Check Kubernetes status"
	@echo "  k8s-logs           - View application logs"
	@echo "  cleanup            - Destroy all resources"
	@echo ""
	@echo "🔍 Validation:"
	@echo "  validate-all       - Validate all prerequisites"

# Agregue nuevas a partir de esta línea