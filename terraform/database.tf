## database.tf

# Subnet group for Aurora
resource "aws_db_subnet_group" "aurora" {
  name       = "scalpel-aurora-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  description = "Subnet group for Aurora cluster"
}

# Security group for Aurora
resource "aws_security_group" "aurora" {
  name        = "scalpel-aurora-sg"
  description = "Allow Lambda to connect to Aurora"
  vpc_id      = aws_vpc.scalpel.id

  ingress {
    from_port                = var.db_port
    to_port                  = var.db_port
    protocol                 = "tcp"
    security_groups          = [aws_security_group.lambda.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Aurora PostgreSQL cluster
resource "aws_rds_cluster" "aurora" {
  cluster_identifier      = "scalpel-aurora-cluster"
  engine                  = "aurora-postgresql"
  engine_version          = "16"
  database_name           = var.db_name
  master_username         = var.db_username
  master_password         = var.db_password
  port                    = var.db_port
  db_subnet_group_name    = aws_db_subnet_group.aurora.name
  vpc_security_group_ids  = [aws_security_group.aurora.id]
  skip_final_snapshot     = true
}

# Two instances in the cluster
resource "aws_rds_cluster_instance" "aurora_instances" {
  count                   = 2
  identifier              = "scalpel-aurora-${count.index}"
  cluster_identifier      = aws_rds_cluster.aurora.id
  instance_class          = var.db_instance_class
  engine                  = aws_rds_cluster.aurora.engine
  engine_version          = aws_rds_cluster.aurora.engine_version
  publicly_accessible     = false
}

output "aurora_endpoint" {
  value       = aws_rds_cluster.aurora.endpoint
  description = "Writer endpoint for the Aurora cluster"
}
