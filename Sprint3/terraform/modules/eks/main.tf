
/*module "eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"             

  name               = var.cluster_name       
  kubernetes_version = var.k8s_cluster_version    

  vpc_id          = data.aws_vpc.default.id
  subnet_ids      = data.aws_subnets.all.ids

  endpoint_public_access = var.cluster_endpoint_public_access  

  create_iam_role = false
  iam_role_arn    = tolist(data.aws_iam_roles.eks_cluster.arns)[0]

  compute_config = {
    enabled    = true
    node_pools = ["general-purpose"]
  }

  enable_irsa = false 
}
*/
module "eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 18.31"             

  cluster_name    = var.cluster_name       
  cluster_version = var.k8s_cluster_version    
  vpc_id          = data.aws_vpc.default.id
  subnet_ids      = data.aws_subnets.all.ids

  cluster_endpoint_public_access = var.cluster_endpoint_public_access  

  create_iam_role = false
  iam_role_arn    = local.cluster_role_arn

  eks_managed_node_groups = {
    default = {
      create_iam_role = false
      iam_role_arn    = local.node_role_arn
      ami_type       = "AL2023_x86_64_STANDARD" # Si esto se podrá modificar convierta esto en una variable
      instance_types = ["t3.medium"] # Si esto se podrá modificar convierta esto en una variable
      desired_size   = 2 # Si esto se podrá modificar< convierta esto en una variable
      min_size       = 1 # Si esto se podrá modificar convierta esto en una variable
      max_size       = 5 # Si esto se podrá modificar convierta esto en una variable
    }
  }

  aws_auth_roles = [
    {
      rolearn  = local.lab_role_arn
      username = "system:node:{{EC2PrivateDNSName}}"
      groups   = ["system:bootstrappers", "system:nodes"]
    },
    {
      rolearn  = local.lab_role_arn
      username = "lab-admin"
      groups   = ["system:masters"]
    },
  ]

  node_security_group_additional_rules = {

    ingress_control_plane_to_nodes_webhook = {
      description                   = "Allow EKS Control Plane to connect to Ingress webhook"
      protocol                      = "tcp"
      from_port                     = 8443
      to_port                       = 8443
      type                          = "ingress"
      # This special variable provided by the EKS module refers to the Control Plane's SG
      source_cluster_security_group = true
    }

    ingress_nodes_to_nodes_all_traffic = {
      description = "Allow nodes to communicate with each other on all ports"
      protocol    = "-1" # "-1" means all protocols
      from_port   = 0    # 0 means all ports
      to_port     = 0    # 0 means all ports
      type        = "ingress"
      self        = true
    }

    egress_nodes_to_internet = {
      description = "Allow nodes to connect to the internet for connecting to DB and call the ingress"
      protocol    = "-1"      # All protocols
      from_port   = 0         # All ports
      to_port     = 0         # All ports
      type        = "egress"
      cidr_blocks = ["0.0.0.0/0"] # Represents all IPv4 addresses (the internet)
    }
  }

  enable_irsa = false 
  create_aws_auth_configmap = false
  manage_aws_auth_configmap = false
}