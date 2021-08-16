pipeline {
    agent { docker { image 'python:3' } }
    stages {
        stage('setup') {
            steps {
                sh """#!/bin/bash
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --no-cache --upgrade pip wheel setuptools twine
                    pip install --no-cache -e .
                """
            }
        }
        stage('coverage') {
            steps {
                sh """#!/bin/bash
                    source venv/bin/activate
                    python -m pip install --no-cache --upgrade coverage pytest
                    python -m coverage run --branch --source screenio -m pytest --disable-pytest-warnings --junitxml junittest-coverage.xml
                    python -m coverage xml
                """
            }
        }
        stage('pylint') {
            steps {
                sh """#!/bin/bash
                    source venv/bin/activate
                    python -m pip install --no-cache --upgrade pylint pylint_junit
                    python -m pylint --rcfile=setup.cfg --output-format=pylint_junit.JUnitReporter screenio | tee junittest-pylint.xml
                """
            }
        }
        stage('build') {
            steps {
                sh """#!/bin/bash
                    source venv/bin/activate
                    python setup.py sdist bdist_wheel
                """
            }
        }
        
    }
    post {
        always {
            junit allowEmptyResults: true, healthScaleFactor: 0.0, testResults: 'junittest*.xml'
            step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
        }
        cleanup {
            cleanWs()
        }
    }
}
