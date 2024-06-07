pipeline {
  
    agent any

    parameters {
        booleanParam(name: 'isRelease', defaultValue: false, description: 'Mark as Release')
    }
  
    stages {
       
        stage('Build and Push Docker Image') {
            environment {
                def label_AZ = "kaniko-${UUID.randomUUID().toString()}"
                def label_PaaS = "kaniko-${UUID.randomUUID().toString()}"
                def imagetag = "latest"                
                def namespace = "shuttle-san"
                def project = "shuttle-openshift-heapdump"
                def timestamp = sh (returnStdout: true, script: '''
                                                  #!/busybox/sh                                                  
                                                  timestamp=$(date +%Y%m%d%H%M)
                                                  tag="${timestamp}"
                                                  echo $tag ''')
            }
            parallel{
                stage("Registry: CAN"){
                    steps {                          
                        podTemplate(name: 'kaniko', label: label_PaaS, yaml: readFile('kaniko-paas.yaml')){
                            node(label_PaaS){
                                container (name: 'kaniko', shell: '/busybox/sh') {                      
                                    checkout scm
                                    withCredentials([usernamePassword(credentialsId: 'aplappshuttle-cred', passwordVariable: 'c_PASS', usernameVariable: 'c_USER')]) {
                                        withCredentials([string(credentialsId: 'jenkinstemp', variable: 'JENKINSSECRET')]) {
                                            script{
                                                if (isRelease) { 
                                                    imagetag = "${timestamp}"
                                                } else {  
                                                    imagetag = "snapshot"
                                                }
                                            }         
                                            
                                            sh """
                                                sed -i "s|JENKINSKEY|${JENKINSSECRET}|" requirements.txt
                                            """
                                                
                                            sh """
                                                #!/busybox/sh
                                                /kaniko/executor -f ./Dockerfile -c `pwd` --insecure --skip-tls-verify --digest-file /tmp/${BUILD_TAG} --build-arg USERNAME=${c_USER} --build-arg PASSWORD=${c_PASS} --destination=registry.global.ccc.srvb.can.paas.cloudcenter.corp/shuttle-sgt/${project}:${imagetag}
                                            """ 
                                        }
                                    }
                                }
                            }   
                        }    
                    }
                }
                stage("Registry: BO"){
                    steps {                          
                        podTemplate(name: 'kaniko', label: label_PaaS, yaml: readFile('kaniko-paas.yaml')){
                            node(label_PaaS){
                                container (name: 'kaniko', shell: '/busybox/sh') {                      
                                    checkout scm
                                    withCredentials([usernamePassword(credentialsId: 'aplappshuttle-cred', passwordVariable: 'c_PASS', usernameVariable: 'c_USER')]) {
                                        withCredentials([string(credentialsId: 'jenkinstemp', variable: 'JENKINSSECRET')]) {
                                            script{
                                                if (isRelease) { 
                                                    imagetag = "${timestamp}"
                                                } else {  
                                                    imagetag = "snapshot"
                                                }
                                            }         
                                            
                                            sh """
                                                sed -i "s|JENKINSKEY|${JENKINSSECRET}|" requirements.txt
                                            """
                                                
                                            sh """
                                                #!/busybox/sh
                                                /kaniko/executor -f ./Dockerfile -c `pwd` --insecure --skip-tls-verify --digest-file /tmp/${BUILD_TAG} --build-arg USERNAME=${c_USER} --build-arg PASSWORD=${c_PASS} --destination=registry.global.ccc.srvb.bo.paas.cloudcenter.corp/shuttle-san/${project}:${imagetag}
                                            """    
                                        }
                                    }
                                }
                            }   
                        }    
                    }
                }
            }
        }
        stage ('Launch deploy to DEV') {
            steps {
                sh """
                echo 'Build complete, initializing deploy to DEV'
                """
                build job: """../shuttle-openshift-heapdump-deploy/dev""", parameters: [[$class: 'StringParameterValue', name: 'DOCKER_IMAGE', value: """${imagetag}"""]]
            }
        }
    }
}
