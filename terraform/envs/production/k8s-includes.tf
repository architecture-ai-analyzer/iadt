# Link K8s resources for production
include {
  path = find_in_parent_folders("envs/dev/k8s-*.tf")
}
