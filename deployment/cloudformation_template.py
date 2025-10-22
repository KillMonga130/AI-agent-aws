"""CloudFormation template for deploying the Ocean Forecasting Agent."""

import json
import yaml


CFN_TEMPLATE = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Autonomous Ocean Forecasting Agent - AWS Bedrock AgentCore Deployment",
    "Parameters": {
        "BedrockModelId": {
            "Type": "String",
            "Default": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "Description": "Bedrock model ID to use"
        },
        "S3BucketName": {
            "Type": "String",
            "Description": "S3 bucket for storing ocean data"
        }
    },
    "Resources": {
        "OceanForecastingBucket": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": {"Ref": "S3BucketName"},
                "VersioningConfiguration": {
                    "Status": "Enabled"
                },
                "LifecycleConfiguration": {
                    "Rules": [
                        {
                            "Id": "DeleteRawDataAfter30Days",
                            "Prefix": "raw/",
                            "ExpirationInDays": 30,
                            "Status": "Enabled"
                        },
                        {
                            "Id": "DeleteProcessedAfter90Days",
                            "Prefix": "processed/",
                            "ExpirationInDays": 90,
                            "Status": "Enabled"
                        }
                    ]
                }
            }
        },
        "AgentExecutionRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": "OceanForecastingAgentRole",
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": [
                                    "lambda.amazonaws.com",
                                    "bedrock.amazonaws.com"
                                ]
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                },
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                ],
                "Policies": [
                    {
                        "PolicyName": "BedrockAccess",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "bedrock:InvokeModel",
                                        "bedrock-runtime:InvokeModel"
                                    ],
                                    "Resource": "*"
                                }
                            ]
                        }
                    },
                    {
                        "PolicyName": "S3Access",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:GetObject",
                                        "s3:PutObject",
                                        "s3:ListBucket"
                                    ],
                                    "Resource": [
                                        {"Fn::Sub": "arn:aws:s3:::${S3BucketName}"},
                                        {"Fn::Sub": "arn:aws:s3:::${S3BucketName}/*"}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "AgentLambdaFunction": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "FunctionName": "ocean-forecasting-agent",
                "Runtime": "python3.11",
                "Handler": "src.lambda_handler.lambda_handler",
                "Role": {"Fn::GetAtt": ["AgentExecutionRole", "Arn"]},
                "Timeout": 60,
                "MemorySize": 512,
                "Environment": {
                    "Variables": {
                        "BEDROCK_MODEL_ID": {"Ref": "BedrockModelId"},
                        "S3_BUCKET_NAME": {"Ref": "S3BucketName"},
                        "LOG_LEVEL": "INFO"
                    }
                }
            }
        },
        "ApiGateway": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "Name": "OceanForecastingAgentAPI",
                "Description": "API for the Autonomous Ocean Forecasting Agent"
            }
        }
    },
    "Outputs": {
        "S3Bucket": {
            "Value": {"Ref": "OceanForecastingBucket"},
            "Description": "S3 bucket for ocean data storage"
        },
        "LambdaFunctionArn": {
            "Value": {"Fn::GetAtt": ["AgentLambdaFunction", "Arn"]},
            "Description": "ARN of the Lambda function"
        },
        "ExecutionRoleArn": {
            "Value": {"Fn::GetAtt": ["AgentExecutionRole", "Arn"]},
            "Description": "ARN of the execution role"
        }
    }
}


def generate_cfn_template():
    """Generate CloudFormation template for the agent."""
    return CFN_TEMPLATE


if __name__ == "__main__":
    template = generate_cfn_template()
    print(json.dumps(template, indent=2))
