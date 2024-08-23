#!/bin/bash

# Set namespace and remote base directory
NAMESPACE="zk-evm"
REMOTE_BASE_DIR="/opt/prover_cli"
LOCAL_BASE_DIR="/tmp"

# Automatically detect the jumpbox pod name
JUMPBOX_POD_NAME=$(kubectl get pods --namespace "$NAMESPACE" -o=jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep zk-evm-jumpbox)

# Check if the pod name was detected
if [ -z "$JUMPBOX_POD_NAME" ]; then
  echo "Error: Could not find a pod with the name containing 'zk-evm-jumpbox'."
  exit 1
fi

echo "Detected jumpbox pod: $JUMPBOX_POD_NAME"

# Directories to copy
DIRECTORIES=("plots" "metrics" "reports")

# Loop through each directory and copy it
for DIR in "${DIRECTORIES[@]}"; do
  echo "Copying ${DIR} from pod ${JUMPBOX_POD_NAME}..."
  kubectl cp "${NAMESPACE}/${JUMPBOX_POD_NAME}:${REMOTE_BASE_DIR}/${DIR}" "${LOCAL_BASE_DIR}/${DIR}"
done

echo "All files have been copied successfully."
