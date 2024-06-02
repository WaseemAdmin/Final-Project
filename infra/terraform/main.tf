provider "aws" {
  region = "eu-west-3"
}

resource "aws_s3_bucket" "photo_bucket" {
  bucket = "waseembucketinstancevarginia"
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "microservices-cluster"
  cluster_version = "1.21"
  subnets         = ["subnet-12345", "subnet-67890"]
  vpc_id          = "vpc-12345"

  node_groups = {
    eks_nodes = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 1

      instance_type = "t3.medium"
    }
  }
}
