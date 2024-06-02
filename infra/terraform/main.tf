provider "aws" {
  region = "us-west-2"
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "microservices-cluster"
  cluster_version = "1.21"
  subnets         = ["subnet-12345", "subnet-67890"]
  vpc_id          = "vpc-abcdef"
}

resource "aws_db_instance" "default" {
  allocated_storage    = 20
  db_subnet_group_name = "my-subnet-group"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t2.micro"
  name                 = "mydb"
  username             = "foo"
  password             = "bar"
  parameter_group_name = "default.mysql8.0"
}
