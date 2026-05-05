# OpenBrain ROS — common dev tasks.
#
# Usage: `make help`

.DEFAULT_GOAL := help
SHELL         := /bin/bash

IMAGE         ?= ghcr.io/openkinematics/openbrain-ros:dev
COMPOSE_BASE  := docker compose -f docker/docker-compose.yml
COMPOSE_DEV   := $(COMPOSE_BASE) -f docker/docker-compose.dev.yml
COMPOSE_SIM   := $(COMPOSE_BASE) -f docker/docker-compose.sim.yml

# ---- top-level ------------------------------------------------------------

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_.-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## colcon build the workspace inside the dev container.
	$(COMPOSE_DEV) run --rm dev bash -lc "colcon build --symlink-install"

test: ## colcon test + surface results.
	$(COMPOSE_DEV) run --rm dev bash -lc "colcon test --event-handlers console_direct+ && colcon test-result --verbose"

lint: ## ruff + clang-format-15 + shellcheck.
	@command -v ruff >/dev/null || { echo "install ruff first: pip install ruff"; exit 1; }
	ruff check src/
	@command -v clang-format-15 >/dev/null && find src -name '*.cpp' -o -name '*.hpp' -o -name '*.h' -o -name '*.cc' 2>/dev/null | xargs --no-run-if-empty clang-format-15 --dry-run --Werror || true
	@command -v shellcheck >/dev/null && shellcheck install.sh utils/*.sh 2>/dev/null || true

format: ## Auto-format Python (ruff --fix) and C++ (clang-format -i).
	ruff check --fix src/ || true
	@find src -name '*.cpp' -o -name '*.hpp' -o -name '*.h' -o -name '*.cc' 2>/dev/null | xargs --no-run-if-empty clang-format-15 -i || true

# ---- dev shell -----------------------------------------------------------

dev: ## Drop into an interactive dev shell with the workspace mounted.
	$(COMPOSE_DEV) run --rm dev

up: ## Bring up the production stack (rosbridge :9090, streamer :8080).
	$(COMPOSE_BASE) up -d

down: ## Tear down the production stack.
	$(COMPOSE_BASE) down

logs: ## Tail logs from the running stack.
	$(COMPOSE_BASE) logs -f

# ---- simulation ----------------------------------------------------------

sim: ## Bring up the Gazebo simulation profile (no hardware).
	$(COMPOSE_SIM) up

sim-down:
	$(COMPOSE_SIM) down

# ---- image -----------------------------------------------------------------

image: ## Build the Jetson image locally (linux/arm64).
	docker buildx build --platform linux/arm64 -f docker/Dockerfile.jetson -t $(IMAGE) .

image-push: image ## Build and push the Jetson image to GHCR.
	docker push $(IMAGE)

# ---- doctor / utils -------------------------------------------------------

doctor: ## Run the hardware self-test against the running stack.
	$(COMPOSE_BASE) exec openbrain bash -lc "ros2 run openbrain_diagnostics doctor || ob doctor"

# ---- cleanup --------------------------------------------------------------

clean: ## Remove build/, install/, log/, and __pycache__.
	rm -rf build install log
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

distclean: clean ## Also remove docker volumes (DESTRUCTIVE — wipes maps + models + recordings).
	$(COMPOSE_BASE) down -v

.PHONY: help build test lint format dev up down logs sim sim-down image image-push doctor clean distclean
