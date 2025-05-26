# network.tf

# 1. Create the VPC
resource "aws_vpc" "scalpel" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "scalpel_vpc" }
}

# 2. Two private subnets (for RDS & Lambda ENIs)
resource "aws_subnet" "private" {
  count                   = 2
  vpc_id                  = aws_vpc.scalpel.id
  cidr_block              = cidrsubnet(aws_vpc.scalpel.cidr_block, 8, count.index)
  map_public_ip_on_launch = false
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "scalpel-private-${count.index}", Tier = "private" }
}

# 3. Public subnet & Internet Gateway (if you need egress/NAT)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.scalpel.id
  cidr_block              = cidrsubnet(aws_vpc.scalpel.cidr_block, 8, count.index + 2)
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "scalpel-public-${count.index}", Tier = "public" }
}

resource "aws_internet_gateway" "scalpel" {
  vpc_id = aws_vpc.scalpel.id
  tags   = { Name = "scalpel-igw" }
}

# 4. Route table & associations for public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.scalpel.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.scalpel.id
  }
  tags = { Name = "scalpel-public-rt" }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# 5. NAT Gateway for private subnets (optional, if Lambdas need internet)
resource "aws_eip" "nat" {
  count = 1
  domain = "vpc"
}

resource "aws_nat_gateway" "scalpel" {
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
  tags          = { Name = "scalpel-natgw" }
}

# 6. Private route table pointing to the NAT
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.scalpel.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.scalpel.id
  }
  tags = { Name = "scalpel-private-rt" }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# 7. Pull in AZ names
data "aws_availability_zones" "available" {}
