variable "region" { 
  description = "La región de AWS donde se desplegarán los recursos."
  type        = string
  nullable    = false
}

variable "owner" {
  description = "Dueño de los recursos. Para propósito académico."
  type        = string
  nullable    = false
}

variable "keep_tags_number" {
  description = "Number of tags to keep in the registry"
  type        = number
}

variable "repository_names" {
  description = "List of repository names to create in the registry"
  type        = list(string)
  nullable    = false
}
