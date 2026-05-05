#!/usr/bin/env bash
# OpenBrain ROS — one-shot installer for the Kinematics Mini and Max boxes
# and any NVIDIA Jetson. Idempotent: safe to re-run.
#
# Steps (each one is its own function so a re-run skips finished work):
#   1. Detect (or ask for) the robot type and write /etc/openbrain/robot.conf
#   2. Install Docker if missing
#   3. Install the NVIDIA container toolkit (Jetson only)
#   4. Pull (or build locally) the openbrain-ros image
#   5. Install + enable the openbrain.service systemd unit
#   6. Install the `openbrain` CLI shim
#   7. Run `openbrain doctor` against the running stack and report

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETC_DIR="/etc/openbrain"
CONF_FILE="${ETC_DIR}/robot.conf"
IMAGE="${OPENBRAIN_IMAGE:-ghcr.io/openkinematics/openbrain-ros:latest}"
SERVICE_NAME="openbrain.service"
CLI_SHIM="/usr/local/bin/openbrain"
LOG_FILE="/tmp/openbrain-install-$(date -u +%Y%m%dT%H%M%SZ).log"

# ---- pretty printing ------------------------------------------------------

if [[ -t 1 ]]; then
  C_RESET='\033[0m'
  C_DIM='\033[2m'
  C_BOLD='\033[1m'
  C_BLUE='\033[1;34m'
  C_GREEN='\033[1;32m'
  C_YELLOW='\033[1;33m'
  C_RED='\033[1;31m'
  C_CYAN='\033[1;36m'
else
  C_RESET=''; C_DIM=''; C_BOLD=''; C_BLUE=''; C_GREEN=''; C_YELLOW=''; C_RED=''; C_CYAN=''
fi

step()  { printf "${C_BLUE}▶${C_RESET} ${C_BOLD}%s${C_RESET}\n" "$*"; }
ok()    { printf "  ${C_GREEN}✓${C_RESET} %s\n" "$*"; }
warn()  { printf "  ${C_YELLOW}⚠${C_RESET} %s\n" "$*" >&2; }
fail()  { printf "  ${C_RED}✗${C_RESET} %s\n" "$*" >&2; exit 1; }
skip()  { printf "  ${C_DIM}—${C_RESET} ${C_DIM}%s${C_RESET}\n" "$*"; }
banner() {
  printf "\n${C_CYAN}╭─────────────────────────────────────────────╮${C_RESET}\n"
  printf "${C_CYAN}│${C_RESET}  ${C_BOLD}OpenBrain ROS installer${C_RESET}                    ${C_CYAN}│${C_RESET}\n"
  printf "${C_CYAN}│${C_RESET}  https://github.com/openkinematics            ${C_CYAN}│${C_RESET}\n"
  printf "${C_CYAN}╰─────────────────────────────────────────────╯${C_RESET}\n\n"
}

# ---- prerequisites --------------------------------------------------------

require_root() {
  if [[ $EUID -ne 0 ]]; then
    fail "Please run with sudo: 'sudo ./install.sh'"
  fi
}

is_jetson() { [[ -e /etc/nv_tegra_release ]]; }

# ---- step 1: robot.conf ---------------------------------------------------

current_robot_type() {
  if [[ -n "${ROBOT_TYPE:-}" ]]; then
    echo "${ROBOT_TYPE}"; return
  fi
  if [[ -f "${CONF_FILE}" ]]; then
    grep -E '^robot_type=' "${CONF_FILE}" | head -1 | cut -d= -f2- | tr -d '"' || true
  fi
}

ask_robot_type() {
  local current="$1"
  printf "  Which robot is this box driving? [current: ${current:-none}]\n"
  printf "    1) UNITREE_GO2\n"
  printf "    2) UNITREE_G1\n"
  printf "    3) TITA\n"
  printf "    4) GENERIC (default)\n"
  read -rp "  > " ans
  case "${ans}" in
    1) echo UNITREE_GO2 ;;
    2) echo UNITREE_G1 ;;
    3) echo TITA ;;
    4|"") echo "${current:-GENERIC}" ;;
    UNITREE_GO2|UNITREE_G1|TITA|GENERIC) echo "${ans}" ;;
    *) echo "${current:-GENERIC}" ;;
  esac
}

write_conf() {
  local robot_type="$1"
  local compute="$2"
  install -d -m 0755 "${ETC_DIR}"
  {
    echo "# Written by openbrain-ros/install.sh"
    echo "robot_type=${robot_type}"
    echo "image=${IMAGE}"
    if [[ -n "${compute}" ]]; then
      echo "compute=${compute}"
    fi
  } > "${CONF_FILE}"
  chmod 0644 "${CONF_FILE}"
  if [[ -n "${compute}" ]]; then
    ok "wrote ${CONF_FILE} (robot_type=${robot_type}, compute=${compute})"
  else
    ok "wrote ${CONF_FILE} (robot_type=${robot_type})"
  fi
}

ask_max_sku() {
  printf "  Which Max compute SKU is this box?\n"
  printf "    1) jetson_t4000_64gb     (base, \$4,999)\n"
  printf "    2) jetson_t5000_128gb    (+\$1,500 — most headroom)\n"
  printf "    3) jetson_agx_orin_64gb  (-\$1,199 — value)\n"
  printf "    4) skip — auto-detect at boot\n"
  read -rp "  > " ans
  case "${ans}" in
    1) echo jetson_t4000_64gb ;;
    2) echo jetson_t5000_128gb ;;
    3) echo jetson_agx_orin_64gb ;;
    *) echo "" ;;
  esac
}

autodetect_compute() {
  if [[ -r /proc/device-tree/model ]]; then
    local model
    model="$(tr -d '\0' </proc/device-tree/model | tr '[:upper:]' '[:lower:]')"
    case "${model}" in
      *t5000*|*thor*) echo jetson_t5000_128gb; return ;;
      *t4000*)        echo jetson_t4000_64gb;  return ;;
      *"agx orin"*|*"agx-orin"*) echo jetson_agx_orin_64gb; return ;;
    esac
  fi
  echo ""
}

is_max_box() {
  # Heuristic: Max boxes have > 16 GB RAM (Mini = 8 GB Orin Nano).
  if [[ -r /proc/meminfo ]]; then
    local kb
    kb="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"
    if [[ -n "${kb}" && "${kb}" -gt 16000000 ]]; then
      return 0
    fi
  fi
  return 1
}

step_conf() {
  step "robot configuration"
  local current robot_type compute
  current="$(current_robot_type || true)"
  if [[ -t 0 && -t 1 && -z "${ROBOT_TYPE:-}" ]]; then
    robot_type="$(ask_robot_type "${current}")"
    if is_max_box; then
      compute="$(ask_max_sku)"
    else
      compute=""
    fi
  else
    robot_type="${current:-GENERIC}"
    compute="$(autodetect_compute)"
    skip "non-interactive — robot_type=${robot_type} compute=${compute:-(unset)}"
  fi
  write_conf "${robot_type}" "${compute}"
}

# ---- step 2: docker -------------------------------------------------------

step_docker() {
  step "docker"
  if command -v docker >/dev/null 2>&1; then
    ok "docker already installed ($(docker --version | awk '{print $3}'))"
    return
  fi
  warn "docker not found — installing now"
  apt-get update >>"${LOG_FILE}" 2>&1
  apt-get install -y ca-certificates curl gnupg >>"${LOG_FILE}" 2>&1
  install -d -m 0755 /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update >>"${LOG_FILE}" 2>&1
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin >>"${LOG_FILE}" 2>&1
  systemctl enable --now docker
  ok "installed docker"
}

# ---- step 3: nvidia toolkit (Jetson only) --------------------------------

step_nvidia() {
  step "nvidia container toolkit"
  if ! is_jetson; then
    skip "not a Jetson — skipping"
    return
  fi
  if dpkg -l 2>/dev/null | grep -q '^ii  nvidia-container-toolkit'; then
    ok "nvidia-container-toolkit already installed"
    return
  fi
  apt-get update >>"${LOG_FILE}" 2>&1
  apt-get install -y nvidia-container-toolkit >>"${LOG_FILE}" 2>&1
  nvidia-ctk runtime configure --runtime=docker >>"${LOG_FILE}" 2>&1
  systemctl restart docker
  ok "installed and configured nvidia container toolkit"
}

# ---- step 4: image --------------------------------------------------------

step_image() {
  step "openbrain image (${IMAGE})"
  if docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    ok "image already present"
    return
  fi
  if docker pull "${IMAGE}" 2>>"${LOG_FILE}"; then
    ok "pulled ${IMAGE}"
    return
  fi
  warn "could not pull (likely offline or no GHCR access) — building locally from ${REPO_ROOT}"
  if ! docker build -f "${REPO_ROOT}/docker/Dockerfile.jetson" -t "${IMAGE}" "${REPO_ROOT}" 2>&1 | tee -a "${LOG_FILE}"; then
    fail "local build failed — check ${LOG_FILE}"
  fi
  ok "built ${IMAGE} locally"
}

# ---- step 5: systemd unit -------------------------------------------------

step_systemd() {
  step "systemd unit"
  local unit_path="/etc/systemd/system/${SERVICE_NAME}"
  cat > "${unit_path}" <<EOF
[Unit]
Description=OpenBrain ROS stack
After=network-online.target docker.service
Wants=network-online.target docker.service

[Service]
Type=simple
EnvironmentFile=-${CONF_FILE}
ExecStartPre=-/usr/bin/docker rm -f openbrain
ExecStart=/usr/bin/docker run --rm --name openbrain \\
  --restart=on-failure \\
  --network=host --privileged --runtime=nvidia \\
  -e ROBOT_TYPE=\${robot_type} \\
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \\
  -v /dev:/dev \\
  -v openbrain_maps:/maps \\
  -v openbrain_models:/opt/openbrain/models \\
  -v openbrain_recordings:/recordings \\
  -v /etc/openbrain:/etc/openbrain:ro \\
  \${image}
ExecStop=/usr/bin/docker stop openbrain
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable "${SERVICE_NAME}" >>"${LOG_FILE}" 2>&1
  ok "installed and enabled ${SERVICE_NAME}"
}

# ---- step 6: CLI shim -----------------------------------------------------

step_cli_shim() {
  step "openbrain CLI shim"
  cat > "${CLI_SHIM}" <<'EOF'
#!/usr/bin/env bash
# Thin host-side shim that forwards `openbrain ...` into the running
# container. Falls back to a workspace install if the container isn't up.
set -euo pipefail
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^openbrain$'; then
  exec docker exec -it openbrain bash -lc "openbrain $*"
fi
if [[ -f /workspace/install/setup.bash ]]; then
  source /workspace/install/setup.bash
  exec openbrain "$@"
fi
echo "openbrain.service is not running. Try: sudo systemctl start openbrain.service" >&2
exit 1
EOF
  chmod +x "${CLI_SHIM}"
  ln -sf "${CLI_SHIM}" /usr/local/bin/ob
  ok "installed ${CLI_SHIM} (also available as 'ob')"
}

# ---- step 7: post-install self-test --------------------------------------

step_doctor() {
  step "post-install self-test"
  if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
    skip "service not running yet — start with: sudo systemctl start ${SERVICE_NAME}"
    return
  fi
  if openbrain doctor 2>&1 | tee -a "${LOG_FILE}"; then
    ok "doctor passed"
  else
    warn "doctor returned warnings — see output above"
  fi
}

# ---- main -----------------------------------------------------------------

main() {
  banner
  printf "  log file: ${C_DIM}%s${C_RESET}\n\n" "${LOG_FILE}"
  require_root

  step_conf
  step_docker
  step_nvidia
  step_image
  step_systemd
  step_cli_shim
  step_doctor

  printf "\n${C_GREEN}╭─────────────────────────────────────────────╮${C_RESET}\n"
  printf "${C_GREEN}│${C_RESET}  ${C_BOLD}install complete${C_RESET}                          ${C_GREEN}│${C_RESET}\n"
  printf "${C_GREEN}╰─────────────────────────────────────────────╯${C_RESET}\n"
  printf "  start now: ${C_BOLD}sudo systemctl start ${SERVICE_NAME}${C_RESET}\n"
  printf "  logs:      ${C_BOLD}journalctl -u ${SERVICE_NAME} -f${C_RESET}\n"
  printf "  CLI:       ${C_BOLD}openbrain doctor${C_RESET} ${C_DIM}(or 'ob doctor')${C_RESET}\n"
  printf "  Stack will auto-start on next boot.\n"
}

main "$@"
