variable "region" {
  default = "us-east-1"
}

variable "access_key" {
  default = ""
}

variable "secret_key" {
  default = ""
}

variable "amis" {
  type = map(string)
  default = {
    "us-east-1" = "ami-0915bcb5fa77e4892" 
    "us-west-2" = "ami-fc0b939c"
  }
}