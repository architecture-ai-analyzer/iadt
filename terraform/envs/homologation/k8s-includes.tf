# Link K8s resources for homologation
include {
  path = find_in_parent_folders("envs/dev/k8s-*.tf")
}
