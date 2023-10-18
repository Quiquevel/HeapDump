pipeline {
  
    agent any
  
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
            steps {                          
                podTemplate(name: 'kaniko', label: label_PaaS, yaml: readFile('kaniko-paas.yaml')){
                    node(label_PaaS){
                        container (name: 'kaniko', shell: '/busybox/sh') {                      
                            checkout scm
                            withCredentials([usernamePassword(credentialsId: 'aplappshuttle-cred', passwordVariable: 'c_PASS', usernameVariable: 'c_USER')]) {
                                withCredentials([string(credentialsId: 'jenkinstemp', variable: 'JENKINSSECRET')]) {
                                    script{
                                        /* env.c_PASS_ENCODED=URLEncoder.encode(c_PASS, "UTF-8")
                                        env.c_USER_ENCODED=URLEncoder.encode(c_USER, "UTF-8") */
                                        if ("${JOB_BASE_NAME}" != "develop"){ 
                                            imagetag = "${BRANCH_NAME}"
                                        }else {  
                                        imagetag = "${timestamp}"
                                        }
                                    }         
                                    
                                    /* sh """
                                            sed -i "s|GIT_USERNAME|${c_USER_ENCODED}|" requirements.txt && \
                                            # sed -i "s|URL_ENCODED_GIT_PASSWORD|URLEncoder.encode("${c_PASS}", "UTF-8")|" requirements.txt
                                            sed -i "s|URL_ENCODED_GIT_PASSWORD|${c_PASS_ENCODED}|" requirements.txt
                                    """  */ 
                                    sh """
                                        sed -i "s|JENKINSKEY|${JENKINSSECRET}|" requirements.txt
                                    """
                                        
                                    retry(3){
                                        sh """
                                        #!/busybox/sh
                                        /kaniko/executor -f ./Dockerfile -c `pwd` --insecure --skip-tls-verify --digest-file /tmp/${BUILD_TAG} --build-arg USERNAME=${c_USER} --build-arg PASSWORD=${c_PASS} --destination=registry.global.ccc.srvb.bo.paas.cloudcenter.corp/${namespace}/${project}:${imagetag}
                                    """ 
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
