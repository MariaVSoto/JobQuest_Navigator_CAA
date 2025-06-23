terraform {
  backend "s3" {
    bucket = "caa900resume"
    key    = "terraform_state/terraform.tfstate"
    region = "us-east-1"
  }
}
