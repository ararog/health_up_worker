@Library('jenkins-pipeline-library@main')

String appName = 'health_up_worker'

//project CI/CD pipeline config
String dockerRepository = "training/${appName}"
String dockerRegistry = "registry.local:5000"
String infraJob = "Training/training%2F${appName}-kube"
String infraBranch = "main"
dockerPipeline([
  createEnv: true,
  dockerRepository: dockerRepository,
  dockerRegistry: dockerRegistry,
  platform: "linux/amd64",
  infra: [
      job: "${infraJob}/${infraBranch}"
  ]
])
